#!/usr/bin/env python3
"""
Mizrahi Compliance Platform - Unified FastAPI Server v5
Supports Hook 1, Hook 2, and Hook 5:

Hook 1 (Monthly Report): Event ID 5618
Hook 2 (Special Transactions): Event ID 5615
Hook 5 (K.303 Disclosure): Maya TASE reports
"""

import asyncio
import base64
import os
import tempfile
import uuid
import httpx
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional
from collections import Counter

from fastapi import FastAPI, Form, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
import resend

# Import Hook 2 processor
from scripts.mizrahi_special_transactions import (
    load_mizrahi_fund_ids,
    load_manager_report,
    check_1_abs_quantity_pairs,
    check_3_dates_in_report_month,
    check_4_decision_method_rules,
    check_4g_dachatz_vote_required,
    check_4d_dachatz_vote_2_flag,
    pick_samples,
    check_6_tase_prices,
    check_6_price_limits,
    check_6g_internal_price_discrepancy,
    fetch_problematic_lists,
    check_7_problematic_securities,
    write_output_xlsx,
    MIZRAHI_TRUSTEE_NAME_DEFAULT,
)

# Import Hook 1 processor
from scripts.fund_automation_complete import (
    process_fund_reports,
    generate_excel_report,
    ProcessingResult,
    FUND_MANAGER_CODES,
    TRUSTEE_NAME,
)

# Import Hook 5 processor (K.303 Disclosure)
from scripts.disclosure_k303_validator import (
    load_mutual_funds as load_k303_mutual_funds,
    load_disclosure_report,
    get_trustee_fund_ids,
    check_1a_fund_completeness,
    check_1b_report_month_validity,
    check_2a_prev_month_comparison,
    check_2b_exposure_profile,
    check_3_combinations,
    write_output_xlsx as write_k303_output_xlsx,
    MIZRAHI_TRUSTEE_NAME as K303_TRUSTEE_NAME,
)

# =======================
# Configuration
# =======================

RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
APIFY_API_TOKEN = os.getenv("APIFY_API_TOKEN", "")
APIFY_REPORT_SCRAPER_ACTOR = "5lhI6O39Qbgv9O0gs"  # Generic Maya report scraper
APIFY_MAIN_FUNDS_ACTOR = "K9WppTziYC3n2vxTu"  # Maya main funds list scraper
APIFY_K303_SCRAPER_ACTOR = "iTpNz9ixbdQCmH43C"  # Maya TASE K.303 scraper (custom actor)

MUTUAL_FUNDS_LIST_PATH = Path(
    os.getenv("MUTUAL_FUNDS_LIST_PATH", "/opt/mizrahi/Mutual_Funds_List.xlsx")
)
SPEC_FILE_PATH = Path(
    os.getenv("SPEC_FILE_PATH", "/opt/mizrahi/Special_Transactions_Specifications.xlsx")
)
K303_SPEC_FILE_PATH = Path(
    os.getenv("K303_SPEC_FILE_PATH", "/opt/mizrahi/K303_Specifications.csv")
)
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "/tmp/mizrahi-outputs"))
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@notifications.82labs.io")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY

# =======================
# Fund Manager Mapping
# =======================

FUND_MANAGERS = {
    "מגדל": {"item_id": "10040", "name_en": "Migdal"},
    "איילון": {"item_id": "10054", "name_en": "Ayalon"},
    "קסם": {"item_id": "10047", "name_en": "Kesem"},
    "סיגמא": {"item_id": "10048", "name_en": "Sigma"},
    "פורסט": {"item_id": "10082", "name_en": "Forest"},
    "הראל": {"item_id": "10031", "name_en": "Harel"},
    "אנליסט": {"item_id": "10019", "name_en": "Analyst"},
    "מיטב": {"item_id": "10083", "name_en": "Meitav"},
    "איביאי": {"item_id": "10068", "name_en": "IBI"},
    "אלטשולר-שחם": {"item_id": "10017", "name_en": "Altshuler-Shaham"},
}

# =======================
# FastAPI App
# =======================

app = FastAPI(
    title="Mizrahi Compliance Platform API",
    description="Unified API for Hook 1 (Monthly Report) and Hook 2 (Special Transactions)",
    version="4.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://mizrahi-smart-tools-portal.vercel.app",
        "http://localhost:3000",
        "http://localhost:5173",
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

job_status: dict[str, dict] = {}


# =======================
# Maya URL Builders
# =======================


def build_maya_url_hook1(item_id: str) -> str:
    """Build Maya URL for Hook 1 - Monthly Report (eventsId=5618)."""
    today = datetime.now()
    one_year_ago = today - timedelta(days=365)

    return (
        f"https://maya.tase.co.il/he/reports/funds?"
        f"fromDate={one_year_ago.strftime('%Y-%m-%d')}&toDate={today.strftime('%Y-%m-%d')}"
        f"&noMeetings=false&isSingle=false&isIntendToTaseMember=false"
        f"&by=group&groupId=7&itemId={item_id}&eventsIds%5B%5D=5618"
    )


def build_maya_url_hook2(item_id: str) -> str:
    """Build Maya URL for Hook 2 - Special Transactions (eventsId=5615)."""
    today = datetime.now()
    one_year_ago = today - timedelta(days=365)

    return (
        f"https://maya.tase.co.il/he/reports/funds?"
        f"fromDate={one_year_ago.strftime('%Y-%m-%d')}&toDate={today.strftime('%Y-%m-%d')}"
        f"&noMeetings=false&isSingle=false&isIntendToTaseMember=false"
        f"&by=group&groupId=7&itemId={item_id}&eventsIds%5B%5D=5615"
    )


def build_maya_url_hook5(item_id: str) -> str:
    """Build Maya URL for Hook 5 - K.303 Disclosure Reports (formId=ק303)."""
    today = datetime.now()
    one_year_ago = today - timedelta(days=365)

    # K.303 reports are under /reports/etfs with formId=%D7%A7303 (ק303 URL-encoded)
    return (
        f"https://maya.tase.co.il/he/reports/etfs?"
        f"fromDate={one_year_ago.strftime('%Y-%m-%d')}&toDate={today.strftime('%Y-%m-%d')}"
        f"&noMeetings=false&isPriority=false&isSingle=false&isIntendToTaseMember=false"
        f"&by=group&formId=%D7%A7303&groupId=7&itemId={item_id}"
    )


# =======================
# Apify Integration
# =======================


async def run_apify_scraper(
    manager_name: str, hook_type: str
) -> tuple[bytes, bytes, str]:
    """
    Run Apify actor to download manager's report.

    Args:
        manager_name: Hebrew name of fund manager
        hook_type: "hook1" for monthly report or "hook2" for special transactions

    Returns:
        (latest_month_content, previous_month_content, original_filename)
        Note: previous_month_content may be empty bytes for hook2
    """
    if manager_name not in FUND_MANAGERS:
        raise ValueError(f"Unknown manager: {manager_name}")

    manager_config = FUND_MANAGERS[manager_name]
    item_id = manager_config["item_id"]

    # Build Maya URL based on hook type
    if hook_type == "hook1":
        maya_url = build_maya_url_hook1(item_id)
    else:
        maya_url = build_maya_url_hook2(item_id)

    actor_input = {"url": maya_url}

    async with httpx.AsyncClient(timeout=300.0) as client:
        run_url = f"https://api.apify.com/v2/acts/{APIFY_REPORT_SCRAPER_ACTOR}/runs"
        headers = {"Authorization": f"Bearer {APIFY_API_TOKEN}"}

        response = await client.post(
            run_url, json=actor_input, headers=headers, params={"timeout": 180}
        )

        if response.status_code != 201:
            raise Exception(f"Failed to start Apify actor: {response.text}")

        run_data = response.json()
        run_id = run_data["data"]["id"]
        status = run_data["data"]["status"]

        # Poll for completion
        if status not in ["SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"]:
            for _ in range(60):
                await asyncio.sleep(5)
                status_url = f"https://api.apify.com/v2/actor-runs/{run_id}"
                status_response = await client.get(status_url, headers=headers)
                run_data = status_response.json()
                status = run_data["data"]["status"]

                if status in ["SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"]:
                    break

        if status != "SUCCEEDED":
            dataset_id = run_data["data"].get("defaultDatasetId")
            error_msg = f"Apify actor failed with status: {status}"

            if dataset_id:
                try:
                    dataset_url = (
                        f"https://api.apify.com/v2/datasets/{dataset_id}/items"
                    )
                    dataset_response = await client.get(dataset_url, headers=headers)
                    if dataset_response.status_code == 200:
                        items = dataset_response.json()
                        if items and items[0].get("status") == "failed":
                            error_detail = items[0].get("error", "")
                            if "Timeout" in error_detail:
                                error_msg = f"התקבלה שגיאת timeout בעת טעינת דוח מנהל הקרן {manager_name} מאתר Maya."
                            else:
                                error_msg = f"שגיאה בהורדת דוח: {error_detail[:200]}"
                except:
                    pass

            raise Exception(error_msg)

        # Get downloaded files from key-value store
        kv_store_id = run_data["data"]["defaultKeyValueStoreId"]

        # Latest month report
        latest_url = f"https://api.apify.com/v2/key-value-stores/{kv_store_id}/records/report_latest_month.csv"
        latest_response = await client.get(latest_url, headers=headers)

        if latest_response.status_code != 200:
            raise Exception(f"לא נמצא דוח עבור מנהל הקרן {manager_name}.")

        latest_content = latest_response.content

        # Previous month report (for Hook 1)
        previous_content = b""
        if hook_type == "hook1":
            previous_url = f"https://api.apify.com/v2/key-value-stores/{kv_store_id}/records/report_previous_month.csv"
            previous_response = await client.get(previous_url, headers=headers)
            if previous_response.status_code == 200:
                previous_content = previous_response.content

        timestamp = datetime.now().strftime("%Y%m%d")
        filename = f"{hook_type}_{manager_name}_{timestamp}.csv"

        return latest_content, previous_content, filename


async def download_main_funds_list() -> bytes:
    """Download the main funds list from Maya via Apify."""
    async with httpx.AsyncClient(timeout=300.0) as client:
        headers = {"Authorization": f"Bearer {APIFY_API_TOKEN}"}

        run_url = f"https://api.apify.com/v2/acts/{APIFY_MAIN_FUNDS_ACTOR}/runs"
        response = await client.post(
            run_url, json={}, headers=headers, params={"timeout": 60}
        )

        if response.status_code != 201:
            raise Exception(f"Failed to start main funds actor: {response.text}")

        run_data = response.json()
        run_id = run_data["data"]["id"]
        status = run_data["data"]["status"]

        if status not in ["SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"]:
            for _ in range(30):
                await asyncio.sleep(5)
                status_url = f"https://api.apify.com/v2/actor-runs/{run_id}"
                status_response = await client.get(status_url, headers=headers)
                run_data = status_response.json()
                status = run_data["data"]["status"]

                if status in ["SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"]:
                    break

        if status != "SUCCEEDED":
            raise Exception(f"Main funds actor failed with status: {status}")

        kv_store_id = run_data["data"]["defaultKeyValueStoreId"]
        file_url = (
            f"https://api.apify.com/v2/key-value-stores/{kv_store_id}/records/download"
        )

        file_response = await client.get(file_url, headers=headers)

        if file_response.status_code != 200:
            raise Exception(
                f"Failed to download main funds list: {file_response.status_code}"
            )

        return file_response.content


async def run_k303_apify_scraper(manager_name: str) -> tuple[bytes, bytes]:
    """
    Run custom Apify actor to download K.303 disclosure reports from Maya TASE.

    Uses custom actor iTpNz9ixbdQCmH43C (Maya-K303-Reports-Downloader).
    Same pattern as Hook 1/2 actors - just pass the Maya URL.

    Output files in Key-Value Store:
    - report_latest_month.csv (current month)
    - report_previous_month.csv (previous month)

    Args:
        manager_name: Hebrew name of fund manager

    Returns:
        (current_month_content, previous_month_content) as bytes
    """
    if manager_name not in FUND_MANAGERS:
        raise ValueError(f"Unknown manager: {manager_name}")

    manager_config = FUND_MANAGERS[manager_name]
    item_id = manager_config["item_id"]

    maya_url = build_maya_url_hook5(item_id)

    # Simple input format - same as Hook 1/2 actors
    actor_input = {"url": maya_url}

    async with httpx.AsyncClient(timeout=600.0) as client:
        headers = {"Authorization": f"Bearer {APIFY_API_TOKEN}"}

        run_url = f"https://api.apify.com/v2/acts/{APIFY_K303_SCRAPER_ACTOR}/runs"
        response = await client.post(
            run_url, json=actor_input, headers=headers, params={"timeout": 300}
        )

        if response.status_code != 201:
            raise Exception(f"Failed to start K.303 actor: {response.text}")

        run_data = response.json()
        run_id = run_data["data"]["id"]
        status = run_data["data"]["status"]

        # Poll for completion
        if status not in ["SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"]:
            for _ in range(120):  # Up to 10 minutes
                await asyncio.sleep(5)
                status_url = f"https://api.apify.com/v2/actor-runs/{run_id}"
                status_response = await client.get(status_url, headers=headers)
                run_data = status_response.json()
                status = run_data["data"]["status"]

                if status in ["SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"]:
                    break

        if status != "SUCCEEDED":
            # Try to get error details from dataset
            dataset_id = run_data["data"].get("defaultDatasetId")
            error_msg = f"K.303 actor failed with status: {status}"

            if dataset_id:
                try:
                    dataset_url = (
                        f"https://api.apify.com/v2/datasets/{dataset_id}/items"
                    )
                    dataset_response = await client.get(dataset_url, headers=headers)
                    if dataset_response.status_code == 200:
                        items = dataset_response.json()
                        if items and items[0].get("error"):
                            error_detail = items[0].get("error", "")
                            if "Timeout" in error_detail:
                                error_msg = f"התקבלה שגיאת timeout בעת טעינת דוח ק.303 מאתר Maya."
                            else:
                                error_msg = (
                                    f"שגיאה בהורדת דוח ק.303: {error_detail[:200]}"
                                )
                except Exception:
                    pass

            raise Exception(error_msg)

        # Get downloaded files from key-value store
        # Actor outputs: report_latest_month.csv, report_previous_month.csv
        kv_store_id = run_data["data"]["defaultKeyValueStoreId"]

        # Download current month file (report_latest_month.csv)
        current_content = b""
        latest_url = f"https://api.apify.com/v2/key-value-stores/{kv_store_id}/records/report_latest_month.csv"
        latest_response = await client.get(latest_url, headers=headers)

        if latest_response.status_code != 200:
            raise Exception(f"לא נמצא דוח ק.303 עבור מנהל הקרן {manager_name}.")

        current_content = latest_response.content

        # Download previous month file (report_previous_month.csv)
        previous_content = b""
        previous_url = f"https://api.apify.com/v2/key-value-stores/{kv_store_id}/records/report_previous_month.csv"
        previous_response = await client.get(previous_url, headers=headers)
        if previous_response.status_code == 200:
            previous_content = previous_response.content

        return current_content, previous_content


# =======================
# Email Templates
# =======================


def build_hook2_email_html(
    manager_name: str, report_filename: str, created_date: str, created_time: str
) -> str:
    """Build HTML email for Hook 2 (Special Transactions)."""
    return f"""<!DOCTYPE html>
<html dir="rtl" lang="he">
<head><meta charset="UTF-8"><title>דוח עסקאות מיוחדות</title></head>
<body style="font-family: 'Segoe UI', Tahoma, sans-serif; direction: rtl; padding: 20px;">
<h1 style="color: #F97316;">דוח עסקאות מיוחדות - {manager_name}</h1>
<p>שם הדוח: {report_filename}</p>
<p>תאריך יצירה: {created_date} {created_time}</p>
<p>הדוח המלא מצורף למייל זה כקובץ Excel.</p>
<hr><p style="color: #888;">Powered by 82Labs</p>
</body></html>"""


def build_hook1_email_html(
    manager_name: str, report_filename: str, created_date: str, created_time: str
) -> str:
    """Build HTML email for Hook 1 (Monthly Report)."""
    return f"""<!DOCTYPE html>
<html dir="rtl" lang="he">
<head><meta charset="UTF-8"><title>דוח חודשי</title></head>
<body style="font-family: 'Segoe UI', Tahoma, sans-serif; direction: rtl; padding: 20px;">
<h1 style="color: #3B82F6;">דוח בקרה חודשי - {manager_name}</h1>
<p>שם הדוח: {report_filename}</p>
<p>תאריך יצירה: {created_date} {created_time}</p>
<p>הדוח המלא מצורף למייל זה כקובץ Excel.</p>
<hr><p style="color: #888;">Powered by 82Labs</p>
</body></html>"""


def build_hook5_email_html(
    manager_name: str, report_filename: str, created_date: str, created_time: str
) -> str:
    """Build HTML email for Hook 5 (K.303 Disclosure)."""
    return f"""<!DOCTYPE html>
<html dir="rtl" lang="he">
<head><meta charset="UTF-8"><title>דוח גילוי נאות ק.303</title></head>
<body style="font-family: 'Segoe UI', Tahoma, sans-serif; direction: rtl; padding: 20px;">
<h1 style="color: #10B981;">דוח גילוי נאות ק.303 - {manager_name}</h1>
<p>שם הדוח: {report_filename}</p>
<p>תאריך יצירה: {created_date} {created_time}</p>
<p>הדוח כולל בדיקות:</p>
<ul>
<li>בדיקה 1א - שלמות קרנות</li>
<li>בדיקה 1ב - תקינות תאריכים</li>
<li>בדיקה 2א - סבירות מול דוח קודם</li>
<li>בדיקה 2ב - סבירות מול מאפייני הקרן</li>
<li>בדיקות 3 - הצלבות קודים</li>
</ul>
<p>הדוח המלא מצורף למייל זה כקובץ Excel.</p>
<hr><p style="color: #888;">Powered by 82Labs</p>
</body></html>"""


def send_report_email(
    to_emails: list[str],
    manager_name: str,
    output_xlsx_path: Path,
    hook_type: str,
) -> dict:
    """Send report email with Excel attachment via Resend."""
    if not RESEND_API_KEY:
        return {"status": "skipped", "reason": "No RESEND_API_KEY configured"}

    now = datetime.now()
    created_date = now.strftime("%d/%m/%Y")
    created_time = now.strftime("%H:%M")
    date_str = now.strftime("%Y%m%d")

    if hook_type == "hook1":
        report_filename = f"דוח_בקרה_חודשי_{manager_name}_{date_str}.xlsx"
        subject = f"דוח בקרה חודשי - {manager_name}"
        html_body = build_hook1_email_html(
            manager_name, report_filename, created_date, created_time
        )
    elif hook_type == "hook5":
        report_filename = f"דוח_גילוי_נאות_ק303_{manager_name}_{date_str}.xlsx"
        subject = f"דוח גילוי נאות ק.303 - {manager_name}"
        html_body = build_hook5_email_html(
            manager_name, report_filename, created_date, created_time
        )
    else:
        report_filename = f"דוח_עסקאות_מיוחדות_{manager_name}_{date_str}.xlsx"
        subject = f"דוח עסקאות מיוחדות - {manager_name}"
        html_body = build_hook2_email_html(
            manager_name, report_filename, created_date, created_time
        )

    with open(output_xlsx_path, "rb") as f:
        xlsx_content = f.read()
    xlsx_b64 = base64.b64encode(xlsx_content).decode("utf-8")

    params = {
        "from": FROM_EMAIL,
        "to": to_emails,
        "subject": subject,
        "html": html_body,
        "attachments": [{"filename": report_filename, "content": xlsx_b64}],
    }

    response = resend.Emails.send(params)
    return response


# =======================
# Hook 2 Processing
# =======================


def process_hook2_report(
    input_report_path: Path,
    manager_name: str,
    output_xlsx_path: Path,
    report_month: Optional[str] = None,
    price_threshold: float = 5.0,
    skip_tase_prices: bool = True,
    mutual_funds_list_path: Optional[Path] = None,
) -> dict[str, Any]:
    """Process Hook 2 (Special Transactions) report."""
    funds_list_path = mutual_funds_list_path or MUTUAL_FUNDS_LIST_PATH
    if not funds_list_path.exists():
        raise FileNotFoundError(f"Mutual Funds List not found at {funds_list_path}")

    in_scope_funds = load_mizrahi_fund_ids(
        funds_list_path, MIZRAHI_TRUSTEE_NAME_DEFAULT
    )
    rows, meta = load_manager_report(input_report_path)

    report_month = report_month or meta.get("report_month_inferred")
    if not report_month:
        raise ValueError("Could not infer report month from report data.")

    # Check #1 - Inter-fund transactions
    ex_dup = check_1_abs_quantity_pairs(rows)

    # Filter to in-scope
    in_scope_rows = [r for r in rows if r.fund_no in in_scope_funds]
    out_scope_rows = [
        r for r in rows if r.fund_no is not None and r.fund_no not in in_scope_funds
    ]

    out_of_scope_funds: dict[int, dict[str, Any]] = {}
    if out_scope_rows:
        counts = Counter([r.fund_no for r in out_scope_rows if r.fund_no is not None])
        for fid, cnt in counts.items():
            out_of_scope_funds[int(fid)] = {
                "count_rows": int(cnt),
                "fund_name": next(
                    (
                        r.fund_name
                        for r in out_scope_rows
                        if r.fund_no == fid and r.fund_name
                    ),
                    None,
                ),
                "reason": "לא ברשימת קרנות מזרחי",
            }

    # Check #3, #4
    ex_date = check_3_dates_in_report_month(in_scope_rows, report_month)
    ex_decision = check_4_decision_method_rules(in_scope_rows)

    # Check #4ג, #4ד
    ex_4g = check_4g_dachatz_vote_required(in_scope_rows)
    ex_4d = check_4d_dachatz_vote_2_flag(in_scope_rows)

    # Valid rows for sampling
    ex_row_nums = {
        e.row.row_num for e in (ex_dup + ex_date + ex_decision + ex_4g + ex_4d)
    }
    valid_rows = [r for r in in_scope_rows if r.row_num not in ex_row_nums]

    # Check #5
    samples = pick_samples(valid_rows, seed=None)

    # Check #6
    price_check_results = []
    if not skip_tase_prices:
        price_check_results = check_6_tase_prices(
            in_scope_rows, variance_threshold_pct=price_threshold
        )

    price_limit_results = check_6_price_limits(in_scope_rows)
    price_internal_results = check_6g_internal_price_discrepancy(in_scope_rows)

    # Check #7
    problematic_lists = fetch_problematic_lists()
    problematic_security_results = check_7_problematic_securities(
        in_scope_rows, problematic_lists
    )

    unique_funds_in_input = len({r.fund_no for r in rows if r.fund_no is not None})
    unique_mizrahi_funds_in_input = len(
        {r.fund_no for r in in_scope_rows if r.fund_no is not None}
    )

    summary = {
        "חודש דוח": report_month,
        "סיבת סינון": "קרנות מזרחי בלבד",
        "מספר קרנות של מנהל הקרן": unique_funds_in_input,
        "מספר קרנות של מנהל הקרן – בניהול מזרחי": unique_mizrahi_funds_in_input,
        "שורות בתחום": len(in_scope_rows),
        "קרנות מחוץ לתחום": len(out_of_scope_funds),
        "חריגות עסקאות בין קרנות": len(ex_dup),
        "חריגות תאריך": len(ex_date),
        "חריגות אופן החלטה": len(ex_decision),
        "חריגות דחצ ללא הצבעה 1": len(ex_4g),
        "חריגות דחצ עם הצבעה 2": len(ex_4d),
        "חריגות מחיר מעל 100": len(price_limit_results),
        "חריגות אי-התאמת מחירים פנימית": len(price_internal_results),
        "חריגות ניירות בעייתיים": len(problematic_security_results),
        "שורות תקינות לדגימה": len(valid_rows),
        "דגימה אופן החלטה 1 - שורה": samples.decision_1.row_num
        if samples.decision_1
        else None,
        "דגימה אופן החלטה 2 - שורה": samples.decision_2.row_num
        if samples.decision_2
        else None,
        "סף סטייה במחיר": f"{price_threshold}%",
    }

    spec_path = SPEC_FILE_PATH if SPEC_FILE_PATH.exists() else None

    write_output_xlsx(
        output_xlsx_path,
        report_month=report_month,
        manager_name=manager_name,
        trustee_name="מזרחי טפחות",
        summary=summary,
        exceptions_duplicates=ex_dup,
        exceptions_date=ex_date,
        exceptions_decision=ex_decision + ex_4g + ex_4d,
        samples=samples,
        in_scope_funds=in_scope_funds,
        price_check_results=price_check_results,
        price_limit_results=price_limit_results + price_internal_results,
        problematic_security_results=problematic_security_results,
        spec_file_path=spec_path,
    )

    samples_data = []
    for sample in [samples.decision_1, samples.decision_2]:
        if sample:
            samples_data.append(
                {
                    "fund_no": sample.fund_no,
                    "fund_name": sample.fund_name or "",
                    "security_name": sample.security_name or "",
                    "security_no": sample.security_no or "",
                    "quantity": sample.quantity,
                    "price": sample.price,
                    "tx_date": sample.tx_date.strftime("%d/%m/%Y")
                    if sample.tx_date
                    else "",
                    "tx_type": sample.tx_type,
                    "decision_method": sample.decision_method,
                }
            )

    return {
        "summary": summary,
        "num_samples": len(samples_data),
        "output_path": str(output_xlsx_path),
        "samples_data": samples_data,
        "report_month": report_month,
    }


# =======================
# Hook 5 Processing (K.303 Disclosure)
# =======================


def process_hook5_report(
    current_report_path: Path,
    previous_report_path: Path,
    manager_name: str,
    output_xlsx_path: Path,
    report_month: str,
    mutual_funds_list_path: Optional[Path] = None,
) -> dict[str, Any]:
    """Process Hook 5 (K.303 Disclosure) report."""
    funds_list_path = mutual_funds_list_path or MUTUAL_FUNDS_LIST_PATH

    # Load data
    all_funds = load_k303_mutual_funds(funds_list_path)
    in_scope_fund_ids = get_trustee_fund_ids(all_funds, K303_TRUSTEE_NAME)

    current_rows = load_disclosure_report(current_report_path)
    prev_rows = load_disclosure_report(previous_report_path)

    # Calculate summary stats
    funds_in_report = set(r.fund_no for r in current_rows if r.fund_no is not None)
    in_scope_funds = funds_in_report & in_scope_fund_ids
    out_of_scope_funds = funds_in_report - in_scope_fund_ids

    summary = {
        "total_funds_in_report": len(funds_in_report),
        "in_scope_funds": len(in_scope_funds),
        "out_of_scope_funds": len(out_of_scope_funds),
        "total_rows": len(current_rows),
    }

    # Run checks
    exceptions_1a = check_1a_fund_completeness(
        current_rows, in_scope_fund_ids, all_funds
    )
    exceptions_1b = check_1b_report_month_validity(
        current_rows, report_month, in_scope_fund_ids
    )
    exceptions_2a = check_2a_prev_month_comparison(
        current_rows, prev_rows, in_scope_fund_ids
    )
    exceptions_2b = check_2b_exposure_profile(
        current_rows, all_funds, in_scope_fund_ids
    )
    exceptions_3 = check_3_combinations(current_rows, in_scope_fund_ids)

    # Write output
    spec_path = K303_SPEC_FILE_PATH if K303_SPEC_FILE_PATH.exists() else None

    write_k303_output_xlsx(
        output_xlsx_path,
        report_month=report_month,
        manager_name=manager_name,
        trustee_name=K303_TRUSTEE_NAME,
        summary=summary,
        exceptions_1a=exceptions_1a,
        exceptions_1b=exceptions_1b,
        exceptions_2a=exceptions_2a,
        exceptions_2b=exceptions_2b,
        exceptions_3=exceptions_3,
        spec_file_path=spec_path,
    )

    # Count total exceptions
    total_exceptions = (
        len(exceptions_1a)
        + len(exceptions_1b)
        + len(exceptions_2a)
        + len(exceptions_2b)
        + sum(len(v) for v in exceptions_3.values())
    )

    return {
        "summary": summary,
        "total_exceptions": total_exceptions,
        "check_results": {
            "check_1a": len(exceptions_1a),
            "check_1b": len(exceptions_1b),
            "check_2a": len(exceptions_2a),
            "check_2b": len(exceptions_2b),
            "check_3": {k: len(v) for k, v in exceptions_3.items()},
        },
        "output_path": str(output_xlsx_path),
        "report_month": report_month,
    }


# =======================
# Background Tasks
# =======================


async def run_hook2_job(
    job_id: str,
    manager_name: str,
    emails: list[str],
    price_threshold: float,
    skip_tase_prices: bool,
):
    """Background task for Hook 2 (Special Transactions)."""
    try:
        temp_dir = Path(tempfile.mkdtemp())

        job_status[job_id]["status"] = "downloading"
        job_status[job_id]["message"] = "מוריד רשימת קרנות מ-Maya..."

        main_funds_content = await download_main_funds_list()
        main_funds_path = temp_dir / "main_funds_list.xlsx"
        main_funds_path.write_bytes(main_funds_content)

        job_status[job_id]["message"] = "מוריד דוח עסקאות מיוחדות מ-TASE Maya..."

        latest_content, _, original_filename = await run_apify_scraper(
            manager_name, "hook2"
        )
        input_file_path = temp_dir / original_filename
        input_file_path.write_bytes(latest_content)

        job_status[job_id]["status"] = "processing"
        job_status[job_id]["message"] = "מעבד את הדוח..."

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"special_transactions_{manager_name}_{timestamp}.xlsx"
        output_path = OUTPUT_DIR / output_filename

        result = process_hook2_report(
            input_report_path=input_file_path,
            manager_name=manager_name,
            output_xlsx_path=output_path,
            price_threshold=price_threshold,
            skip_tase_prices=skip_tase_prices,
            mutual_funds_list_path=main_funds_path,
        )

        job_status[job_id]["status"] = "sending_email"
        job_status[job_id]["message"] = "שולח דוח במייל..."

        email_result = send_report_email(
            to_emails=emails,
            manager_name=manager_name,
            output_xlsx_path=output_path,
            hook_type="hook2",
        )

        job_status[job_id]["status"] = "completed"
        job_status[job_id]["message"] = "הדוח נשלח בהצלחה!"
        job_status[job_id]["result"] = {
            "summary": result["summary"],
            "email_sent_to": emails,
            "output_file": output_filename,
            "email_id": email_result.get("id")
            if isinstance(email_result, dict)
            else str(email_result),
        }

        input_file_path.unlink(missing_ok=True)

    except Exception as e:
        job_status[job_id]["status"] = "failed"
        job_status[job_id]["error"] = str(e)
        job_status[job_id]["message"] = f"שגיאה: {str(e)}"


async def run_hook1_job(
    job_id: str,
    manager_name: str,
    emails: list[str],
):
    """Background task for Hook 1 (Monthly Report)."""
    try:
        temp_dir = Path(tempfile.mkdtemp())

        job_status[job_id]["status"] = "downloading"
        job_status[job_id]["message"] = "מוריד רשימת קרנות מ-Maya..."

        main_funds_content = await download_main_funds_list()
        main_funds_path = temp_dir / "main_funds_list.xlsx"
        main_funds_path.write_bytes(main_funds_content)

        job_status[job_id]["message"] = "מוריד דוח חודשי מ-TASE Maya..."

        latest_content, previous_content, _ = await run_apify_scraper(
            manager_name, "hook1"
        )

        current_report_path = temp_dir / f"{manager_name}_current.csv"
        current_report_path.write_bytes(latest_content)

        previous_report_path = temp_dir / f"{manager_name}_previous.csv"
        if previous_content:
            previous_report_path.write_bytes(previous_content)
        else:
            previous_report_path = None

        job_status[job_id]["status"] = "processing"
        job_status[job_id]["message"] = "מעבד את הדוח..."

        # Determine report month from current date
        now = datetime.now()
        report_month = now.strftime("%Y-%m")

        result = process_fund_reports(
            funds_list_path=str(main_funds_path),
            current_report_path=str(current_report_path),
            previous_report_path=str(previous_report_path)
            if previous_report_path
            else str(current_report_path),
            manager_name=manager_name,
            trustee_name=TRUSTEE_NAME,
            report_month=report_month,
        )

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"monthly_report_{manager_name}_{timestamp}.xlsx"
        output_path = OUTPUT_DIR / output_filename

        generate_excel_report(result, str(output_path))

        job_status[job_id]["status"] = "sending_email"
        job_status[job_id]["message"] = "שולח דוח במייל..."

        email_result = send_report_email(
            to_emails=emails,
            manager_name=manager_name,
            output_xlsx_path=output_path,
            hook_type="hook1",
        )

        job_status[job_id]["status"] = "completed"
        job_status[job_id]["message"] = "הדוח נשלח בהצלחה!"
        job_status[job_id]["result"] = {
            "manager_name": result.manager_name,
            "magna_funds_count": result.magna_funds_count,
            "manager_funds_count": result.manager_funds_count,
            "matching_funds_count": result.matching_funds_count,
            "has_discrepancies": result.has_discrepancies,
            "email_sent_to": emails,
            "output_file": output_filename,
            "email_id": email_result.get("id")
            if isinstance(email_result, dict)
            else str(email_result),
        }

        current_report_path.unlink(missing_ok=True)
        if previous_report_path:
            previous_report_path.unlink(missing_ok=True)

    except Exception as e:
        job_status[job_id]["status"] = "failed"
        job_status[job_id]["error"] = str(e)
        job_status[job_id]["message"] = f"שגיאה: {str(e)}"


async def run_hook5_job(
    job_id: str,
    manager_name: str,
    emails: list[str],
    report_month: str,
):
    """Background task for Hook 5 (K.303 Disclosure)."""
    try:
        temp_dir = Path(tempfile.mkdtemp())

        job_status[job_id]["status"] = "downloading"
        job_status[job_id]["message"] = "מוריד רשימת קרנות מ-Maya..."

        main_funds_content = await download_main_funds_list()
        main_funds_path = temp_dir / "main_funds_list.xlsx"
        main_funds_path.write_bytes(main_funds_content)

        job_status[job_id]["message"] = "מוריד דוחות גילוי נאות ק.303 מ-Maya TASE..."

        current_content, previous_content = await run_k303_apify_scraper(manager_name)

        current_report_path = temp_dir / f"{manager_name}_k303_current.xlsx"
        current_report_path.write_bytes(current_content)

        previous_report_path = temp_dir / f"{manager_name}_k303_previous.xlsx"
        if previous_content:
            previous_report_path.write_bytes(previous_content)
        else:
            # Use current as previous if no previous available
            previous_report_path.write_bytes(current_content)

        job_status[job_id]["status"] = "processing"
        job_status[job_id]["message"] = "מעבד את הדוח..."

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"k303_disclosure_{manager_name}_{timestamp}.xlsx"
        output_path = OUTPUT_DIR / output_filename

        result = process_hook5_report(
            current_report_path=current_report_path,
            previous_report_path=previous_report_path,
            manager_name=manager_name,
            output_xlsx_path=output_path,
            report_month=report_month,
            mutual_funds_list_path=main_funds_path,
        )

        job_status[job_id]["status"] = "sending_email"
        job_status[job_id]["message"] = "שולח דוח במייל..."

        email_result = send_report_email(
            to_emails=emails,
            manager_name=manager_name,
            output_xlsx_path=output_path,
            hook_type="hook5",
        )

        job_status[job_id]["status"] = "completed"
        job_status[job_id]["message"] = "הדוח נשלח בהצלחה!"
        job_status[job_id]["result"] = {
            "summary": result["summary"],
            "total_exceptions": result["total_exceptions"],
            "check_results": result["check_results"],
            "email_sent_to": emails,
            "output_file": output_filename,
            "email_id": email_result.get("id")
            if isinstance(email_result, dict)
            else str(email_result),
        }

        current_report_path.unlink(missing_ok=True)
        previous_report_path.unlink(missing_ok=True)

    except Exception as e:
        job_status[job_id]["status"] = "failed"
        job_status[job_id]["error"] = str(e)
        job_status[job_id]["message"] = f"שגיאה: {str(e)}"


# =======================
# API Endpoints - General
# =======================


@app.get("/")
async def root():
    return {
        "status": "ok",
        "service": "Mizrahi Compliance Platform API",
        "version": "5.0.0",
        "hooks": {
            "hook1": "Monthly Report (event 5618)",
            "hook2": "Special Transactions (event 5615)",
            "hook5": "K.303 Disclosure (Maya TASE)",
        },
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/api/managers")
async def get_managers():
    """Get list of available fund managers."""
    return {
        "managers": [
            {"name": name, "item_id": config["item_id"], "name_en": config["name_en"]}
            for name, config in FUND_MANAGERS.items()
        ]
    }


# =======================
# API Endpoints - Hook 2 (Special Transactions)
# =======================


@app.post("/api/process-report")
async def process_report_endpoint(
    background_tasks: BackgroundTasks,
    manager_name: str = Form(...),
    email: str = Form(...),
    price_threshold: float = Form(5.0),
    skip_tase_prices: bool = Form(True),
):
    """
    Process Hook 2 - Special Transactions report (auto-download from TASE Maya).
    Uses event ID 5615.

    - **manager_name**: Fund manager name (Hebrew)
    - **email**: Recipient email(s), semicolon-separated
    - **price_threshold**: Price variance threshold % (default 5.0)
    - **skip_tase_prices**: Skip TASE price scraping (default True)
    """
    if manager_name not in FUND_MANAGERS:
        raise HTTPException(
            status_code=400,
            detail=f"מנהל קרן לא מוכר: {manager_name}. אפשרויות: {', '.join(FUND_MANAGERS.keys())}",
        )

    emails = [e.strip() for e in email.replace(",", ";").split(";") if e.strip()]
    if not emails:
        raise HTTPException(status_code=400, detail="נדרשת כתובת אימייל אחת לפחות")

    if not APIFY_API_TOKEN:
        raise HTTPException(status_code=500, detail="APIFY_API_TOKEN not configured")

    job_id = str(uuid.uuid4())
    job_status[job_id] = {
        "status": "queued",
        "message": "הבקשה התקבלה",
        "created_at": datetime.now().isoformat(),
        "hook_type": "hook2",
        "manager_name": manager_name,
        "emails": emails,
    }

    background_tasks.add_task(
        run_hook2_job,
        job_id=job_id,
        manager_name=manager_name,
        emails=emails,
        price_threshold=price_threshold,
        skip_tase_prices=skip_tase_prices,
    )

    return {
        "job_id": job_id,
        "status": "queued",
        "message": "Hook 2 - עסקאות מיוחדות: הבקשה התקבלה",
    }


# =======================
# API Endpoints - Hook 1 (Monthly Report)
# =======================


@app.post("/api/process-monthly-report")
async def process_monthly_report_endpoint(
    background_tasks: BackgroundTasks,
    manager_name: str = Form(...),
    email: str = Form(...),
):
    """
    Process Hook 1 - Monthly Report (auto-download from TASE Maya).
    Uses event ID 5618.

    - **manager_name**: Fund manager name (Hebrew)
    - **email**: Recipient email(s), semicolon-separated
    """
    if manager_name not in FUND_MANAGERS:
        raise HTTPException(
            status_code=400,
            detail=f"מנהל קרן לא מוכר: {manager_name}. אפשרויות: {', '.join(FUND_MANAGERS.keys())}",
        )

    emails = [e.strip() for e in email.replace(",", ";").split(";") if e.strip()]
    if not emails:
        raise HTTPException(status_code=400, detail="נדרשת כתובת אימייל אחת לפחות")

    if not APIFY_API_TOKEN:
        raise HTTPException(status_code=500, detail="APIFY_API_TOKEN not configured")

    job_id = str(uuid.uuid4())
    job_status[job_id] = {
        "status": "queued",
        "message": "הבקשה התקבלה",
        "created_at": datetime.now().isoformat(),
        "hook_type": "hook1",
        "manager_name": manager_name,
        "emails": emails,
    }

    background_tasks.add_task(
        run_hook1_job,
        job_id=job_id,
        manager_name=manager_name,
        emails=emails,
    )

    return {
        "job_id": job_id,
        "status": "queued",
        "message": "Hook 1 - דוח חודשי: הבקשה התקבלה",
    }


# =======================
# API Endpoints - Hook 5 (K.303 Disclosure)
# =======================


@app.post("/api/process-disclosure-report")
async def process_disclosure_report_endpoint(
    background_tasks: BackgroundTasks,
    manager_name: str = Form(...),
    email: str = Form(...),
    report_month: str = Form(None),
):
    """
    Process Hook 5 - K.303 Disclosure Report (auto-download from Maya TASE).

    - **manager_name**: Fund manager name (Hebrew)
    - **email**: Recipient email(s), semicolon-separated
    - **report_month**: Report month in YYYY-MM format (default: current month)
    """
    if manager_name not in FUND_MANAGERS:
        raise HTTPException(
            status_code=400,
            detail=f"מנהל קרן לא מוכר: {manager_name}. אפשרויות: {', '.join(FUND_MANAGERS.keys())}",
        )

    emails = [e.strip() for e in email.replace(",", ";").split(";") if e.strip()]
    if not emails:
        raise HTTPException(status_code=400, detail="נדרשת כתובת אימייל אחת לפחות")

    if not APIFY_API_TOKEN:
        raise HTTPException(status_code=500, detail="APIFY_API_TOKEN not configured")

    # Default to current month if not specified
    if not report_month:
        report_month = datetime.now().strftime("%Y-%m")

    job_id = str(uuid.uuid4())
    job_status[job_id] = {
        "status": "queued",
        "message": "הבקשה התקבלה",
        "created_at": datetime.now().isoformat(),
        "hook_type": "hook5",
        "manager_name": manager_name,
        "emails": emails,
        "report_month": report_month,
    }

    background_tasks.add_task(
        run_hook5_job,
        job_id=job_id,
        manager_name=manager_name,
        emails=emails,
        report_month=report_month,
    )

    return {
        "job_id": job_id,
        "status": "queued",
        "message": "Hook 5 - דוח גילוי נאות ק.303: הבקשה התקבלה",
    }


# =======================
# API Endpoints - Job Status
# =======================


@app.get("/api/job/{job_id}")
async def get_job_status(job_id: str):
    """Get the status of a processing job."""
    if job_id not in job_status:
        raise HTTPException(status_code=404, detail="Job not found")
    return job_status[job_id]


@app.get("/api/download/{filename}")
async def download_file(filename: str):
    """Download a generated report file."""
    file_path = OUTPUT_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


# =======================
# Run Server
# =======================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
