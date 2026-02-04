#!/usr/bin/env python3
"""
Unified Batch Processor for All Hooks

Runs Hook 1, Hook 2, and Hook 5 for all (or selected) fund managers,
then sends ONE consolidated email per manager with 3 XLSX attachments.

Usage:
    python batch_all_hooks.py
    python batch_all_hooks.py --managers "מגדל,סיגמא"
    python batch_all_hooks.py --email "test@example.com" --send-email

Environment Variables:
    APIFY_API_TOKEN - Required for data fetching from Maya TASE
    RESEND_API_KEY  - Required for --send-email flag
"""

import os
import sys
import json
import base64
import argparse
import asyncio
import subprocess
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Any

import httpx

try:
    import resend
except ImportError:
    resend = None

# =======================
# Configuration
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

# Apify Actor IDs
APIFY_MAIN_FUNDS_ACTOR = "K9WppTziYC3n2vxTu"
APIFY_REPORT_SCRAPER_ACTOR = "5lhI6O39Qbgv9O0gs"
APIFY_K303_SCRAPER_ACTOR = "iTpNz9ixbdQCmH43C"

# Environment variables
APIFY_API_TOKEN = os.getenv("APIFY_API_TOKEN", "")
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@notifications.82labs.io")
DEFAULT_EMAIL = "alexandrf539@gmail.com"

# Script paths
SCRIPTS_DIR = Path(__file__).parent
HOOK1_SCRIPT = SCRIPTS_DIR / "fund_automation_complete.py"
HOOK2_SCRIPT = SCRIPTS_DIR / "mizrahi_special_transactions.py"
HOOK5_SCRIPT = SCRIPTS_DIR / "disclosure_k303_validator.py"


# =======================
# Logging Helpers
# =======================


def log(message: str) -> None:
    """Print timestamped log message."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")


def log_success(message: str) -> None:
    """Print success message."""
    log(f"✓ {message}")


def log_error(message: str) -> None:
    """Print error message."""
    log(f"✗ {message}")


def log_info(message: str) -> None:
    """Print info message."""
    log(f"ℹ {message}")


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
    """Build Maya URL for Hook 5 - K.303 Disclosure Reports."""
    today = datetime.now()
    one_year_ago = today - timedelta(days=365)
    return (
        f"https://maya.tase.co.il/he/reports/etfs?"
        f"fromDate={one_year_ago.strftime('%Y-%m-%d')}&toDate={today.strftime('%Y-%m-%d')}"
        f"&noMeetings=false&isPriority=false&isSingle=false&isIntendToTaseMember=false"
        f"&by=group&formId=%D7%A7303&groupId=7&itemId={item_id}"
    )


# =======================
# Apify Integration
# =======================


async def download_main_funds_list() -> bytes:
    """Download the main funds list from Maya via Apify."""
    log_info("Downloading main funds list from Maya...")

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

        log_success("Main funds list downloaded")
        return file_response.content


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
    """
    if manager_name not in FUND_MANAGERS:
        raise ValueError(f"Unknown manager: {manager_name}")

    manager_config = FUND_MANAGERS[manager_name]
    item_id = manager_config["item_id"]

    if hook_type == "hook1":
        maya_url = build_maya_url_hook1(item_id)
    else:
        maya_url = build_maya_url_hook2(item_id)

    actor_input = {"url": maya_url}

    async with httpx.AsyncClient(timeout=300.0) as client:
        headers = {"Authorization": f"Bearer {APIFY_API_TOKEN}"}

        run_url = f"https://api.apify.com/v2/acts/{APIFY_REPORT_SCRAPER_ACTOR}/runs"
        response = await client.post(
            run_url, json=actor_input, headers=headers, params={"timeout": 180}
        )

        if response.status_code != 201:
            raise Exception(f"Failed to start Apify actor: {response.text}")

        run_data = response.json()
        run_id = run_data["data"]["id"]
        status = run_data["data"]["status"]

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
            raise Exception(f"Apify actor failed with status: {status}")

        kv_store_id = run_data["data"]["defaultKeyValueStoreId"]

        # Latest month report
        latest_url = f"https://api.apify.com/v2/key-value-stores/{kv_store_id}/records/report_latest_month.csv"
        latest_response = await client.get(latest_url, headers=headers)

        if latest_response.status_code != 200:
            raise Exception(f"No report found for manager {manager_name}")

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


async def run_k303_apify_scraper(manager_name: str) -> tuple[bytes, bytes]:
    """
    Run Apify actor to download K.303 disclosure reports.

    Returns:
        (current_month_content, previous_month_content) as bytes
    """
    if manager_name not in FUND_MANAGERS:
        raise ValueError(f"Unknown manager: {manager_name}")

    manager_config = FUND_MANAGERS[manager_name]
    item_id = manager_config["item_id"]

    maya_url = build_maya_url_hook5(item_id)
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

        if status not in ["SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"]:
            for _ in range(120):
                await asyncio.sleep(5)
                status_url = f"https://api.apify.com/v2/actor-runs/{run_id}"
                status_response = await client.get(status_url, headers=headers)
                run_data = status_response.json()
                status = run_data["data"]["status"]

                if status in ["SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"]:
                    break

        if status != "SUCCEEDED":
            raise Exception(f"K.303 actor failed with status: {status}")

        kv_store_id = run_data["data"]["defaultKeyValueStoreId"]

        # Current month
        latest_url = f"https://api.apify.com/v2/key-value-stores/{kv_store_id}/records/report_latest_month.csv"
        latest_response = await client.get(latest_url, headers=headers)

        if latest_response.status_code != 200:
            raise Exception(f"No K.303 report found for manager {manager_name}")

        current_content = latest_response.content

        # Previous month
        previous_content = b""
        previous_url = f"https://api.apify.com/v2/key-value-stores/{kv_store_id}/records/report_previous_month.csv"
        previous_response = await client.get(previous_url, headers=headers)
        if previous_response.status_code == 200:
            previous_content = previous_response.content

        return current_content, previous_content


# =======================
# Hook Processors
# =======================


def run_hook1(
    manager_name: str,
    output_dir: Path,
) -> Optional[Path]:
    """
    Run Hook 1 (Monthly Report) for a manager.

    Uses fund_automation_complete.py via subprocess.

    Returns:
        Path to output XLSX or None on failure
    """
    log_info(f"Running Hook 1 for {manager_name}...")

    cmd = [
        sys.executable,
        str(HOOK1_SCRIPT),
        "--fund-name",
        manager_name,
        "--output-dir",
        str(output_dir),
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600,
            cwd=str(SCRIPTS_DIR),
        )

        if result.returncode != 0:
            log_error(f"Hook 1 failed for {manager_name}: {result.stderr[:500]}")
            return None

        # Find the output file (pattern: דוח_*.xlsx)
        for f in output_dir.glob(f"דוח_{manager_name}*.xlsx"):
            log_success(f"Hook 1 completed: {f.name}")
            return f

        # Also check for any xlsx file
        for f in output_dir.glob("*.xlsx"):
            if "hook1" in f.name.lower() or "דוח" in f.name:
                log_success(f"Hook 1 completed: {f.name}")
                return f

        log_error(f"Hook 1: No output file found for {manager_name}")
        return None

    except subprocess.TimeoutExpired:
        log_error(f"Hook 1 timed out for {manager_name}")
        return None
    except Exception as e:
        log_error(f"Hook 1 error for {manager_name}: {e}")
        return None


def run_hook2(
    manager_name: str,
    funds_list_path: Path,
    report_csv_path: Path,
    output_dir: Path,
    skip_tase_prices: bool = True,
) -> Optional[Path]:
    """
    Run Hook 2 (Special Transactions) for a manager.

    Uses mizrahi_special_transactions.py via subprocess.

    Returns:
        Path to output XLSX or None on failure
    """
    log_info(f"Running Hook 2 for {manager_name}...")

    output_xlsx = output_dir / f"hook2_{manager_name}_עסקאות_מיוחדות.xlsx"
    email_json = output_dir / f"hook2_{manager_name}_email.json"

    cmd = [
        sys.executable,
        str(HOOK2_SCRIPT),
        "--mutual-funds-list",
        str(funds_list_path),
        "--input-report",
        str(report_csv_path),
        "--output-xlsx",
        str(output_xlsx),
        "--email-json",
        str(email_json),
        "--manager-name",
        manager_name,
    ]

    if skip_tase_prices:
        cmd.append("--skip-tase-prices")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600,
            cwd=str(SCRIPTS_DIR),
        )

        if result.returncode != 0:
            log_error(f"Hook 2 failed for {manager_name}: {result.stderr[:500]}")
            return None

        if output_xlsx.exists():
            log_success(f"Hook 2 completed: {output_xlsx.name}")
            return output_xlsx

        log_error(f"Hook 2: No output file found for {manager_name}")
        return None

    except subprocess.TimeoutExpired:
        log_error(f"Hook 2 timed out for {manager_name}")
        return None
    except Exception as e:
        log_error(f"Hook 2 error for {manager_name}: {e}")
        return None


def run_hook5(
    manager_name: str,
    funds_list_path: Path,
    current_csv_path: Path,
    previous_csv_path: Path,
    output_dir: Path,
    report_month: str,
) -> Optional[Path]:
    """
    Run Hook 5 (K.303 Disclosure) for a manager.

    Uses disclosure_k303_validator.py via subprocess.

    Returns:
        Path to output XLSX or None on failure
    """
    log_info(f"Running Hook 5 for {manager_name}...")

    output_xlsx = output_dir / f"hook5_{manager_name}_גילוי_נאות_ק303.xlsx"

    cmd = [
        sys.executable,
        str(HOOK5_SCRIPT),
        "--mutual-funds-list",
        str(funds_list_path),
        "--current-report",
        str(current_csv_path),
        "--previous-report",
        str(previous_csv_path),
        "--output-xlsx",
        str(output_xlsx),
        "--report-month",
        report_month,
        "--manager-name",
        manager_name,
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600,
            cwd=str(SCRIPTS_DIR),
        )

        if result.returncode != 0:
            log_error(f"Hook 5 failed for {manager_name}: {result.stderr[:500]}")
            return None

        if output_xlsx.exists():
            log_success(f"Hook 5 completed: {output_xlsx.name}")
            return output_xlsx

        log_error(f"Hook 5: No output file found for {manager_name}")
        return None

    except subprocess.TimeoutExpired:
        log_error(f"Hook 5 timed out for {manager_name}")
        return None
    except Exception as e:
        log_error(f"Hook 5 error for {manager_name}: {e}")
        return None


# =======================
# HTML Email Template
# =======================


def build_unified_email_html(
    manager_name: str,
    hook1_filename: Optional[str],
    hook2_filename: Optional[str],
    hook5_filename: Optional[str],
    created_date: str,
    created_time: str,
) -> str:
    """
    Build unified HTML email with results from all 3 hooks.

    Based on the n8n workflow template from source_of_truth.
    """
    # Count successful hooks
    attachment_count = sum(
        1 for f in [hook1_filename, hook2_filename, hook5_filename] if f
    )

    # Build file list for info card
    files_list = []
    if hook1_filename:
        files_list.append(hook1_filename)
    if hook2_filename:
        files_list.append(hook2_filename)
    if hook5_filename:
        files_list.append(hook5_filename)

    files_html = "<br>".join(files_list) if files_list else "אין קבצים"

    # Hook 1 section
    hook1_section = ""
    if hook1_filename:
        hook1_section = f"""
                            <!-- Hook 1 Section - Blue -->
                            <table cellpadding="0" cellspacing="0" border="0" width="100%" style="margin-top: 25px; background-color: #eff6ff; border-radius: 8px; border-right: 4px solid #3B82F6;">
                                <tr>
                                    <td style="padding: 20px;">
                                        <h3 style="color: #1e40af; margin: 0 0 10px 0; font-size: 16px; font-weight: 600;">&#128202; Hook 1 - דוח בקרה חודשי</h3>
                                        <p style="color: #1e40af; font-size: 13px; margin: 0;">&#10004; הושלם בהצלחה</p>
                                        <p style="color: #64748b; font-size: 12px; margin: 5px 0 0 0;">קובץ: {hook1_filename}</p>
                                    </td>
                                </tr>
                            </table>"""
    else:
        hook1_section = """
                            <!-- Hook 1 Section - Failed -->
                            <table cellpadding="0" cellspacing="0" border="0" width="100%" style="margin-top: 25px; background-color: #fef2f2; border-radius: 8px; border-right: 4px solid #ef4444;">
                                <tr>
                                    <td style="padding: 20px;">
                                        <h3 style="color: #991b1b; margin: 0 0 10px 0; font-size: 16px; font-weight: 600;">&#128202; Hook 1 - דוח בקרה חודשי</h3>
                                        <p style="color: #991b1b; font-size: 13px; margin: 0;">&#10008; לא הושלם</p>
                                    </td>
                                </tr>
                            </table>"""

    # Hook 2 section
    hook2_section = ""
    if hook2_filename:
        hook2_section = f"""
                            <!-- Hook 2 Section - Yellow -->
                            <table cellpadding="0" cellspacing="0" border="0" width="100%" style="margin-top: 15px; background-color: #fefce8; border-radius: 8px; border-right: 4px solid #eab308;">
                                <tr>
                                    <td style="padding: 20px;">
                                        <h3 style="color: #854d0e; margin: 0 0 10px 0; font-size: 16px; font-weight: 600;">&#128260; Hook 2 - עסקאות מיוחדות</h3>
                                        <p style="color: #854d0e; font-size: 13px; margin: 0;">&#10004; הושלם בהצלחה</p>
                                        <p style="color: #64748b; font-size: 12px; margin: 5px 0 0 0;">קובץ: {hook2_filename}</p>
                                        <p style="color: #64748b; font-size: 11px; margin: 5px 0 0 0; font-style: italic;">בדיקות: עסקאות בין-קרנות, תאריכים, אופן החלטה, דגימות, מחירים, ני"ע בעייתיים</p>
                                    </td>
                                </tr>
                            </table>"""
    else:
        hook2_section = """
                            <!-- Hook 2 Section - Failed -->
                            <table cellpadding="0" cellspacing="0" border="0" width="100%" style="margin-top: 15px; background-color: #fef2f2; border-radius: 8px; border-right: 4px solid #ef4444;">
                                <tr>
                                    <td style="padding: 20px;">
                                        <h3 style="color: #991b1b; margin: 0 0 10px 0; font-size: 16px; font-weight: 600;">&#128260; Hook 2 - עסקאות מיוחדות</h3>
                                        <p style="color: #991b1b; font-size: 13px; margin: 0;">&#10008; לא הושלם</p>
                                    </td>
                                </tr>
                            </table>"""

    # Hook 5 section
    hook5_section = ""
    if hook5_filename:
        hook5_section = f"""
                            <!-- Hook 5 Section - Green -->
                            <table cellpadding="0" cellspacing="0" border="0" width="100%" style="margin-top: 15px; background-color: #f0fdf4; border-radius: 8px; border-right: 4px solid #10B981;">
                                <tr>
                                    <td style="padding: 20px;">
                                        <h3 style="color: #166534; margin: 0 0 10px 0; font-size: 16px; font-weight: 600;">&#128203; Hook 5 - גילוי נאות ק.303</h3>
                                        <p style="color: #166534; font-size: 13px; margin: 0;">&#10004; הושלם בהצלחה</p>
                                        <p style="color: #64748b; font-size: 12px; margin: 5px 0 0 0;">קובץ: {hook5_filename}</p>
                                        <p style="color: #64748b; font-size: 11px; margin: 5px 0 0 0; font-style: italic;">בדיקות: שלמות קרנות, תאריכים, סבירות, הצלבות קודים</p>
                                    </td>
                                </tr>
                            </table>"""
    else:
        hook5_section = """
                            <!-- Hook 5 Section - Failed -->
                            <table cellpadding="0" cellspacing="0" border="0" width="100%" style="margin-top: 15px; background-color: #fef2f2; border-radius: 8px; border-right: 4px solid #ef4444;">
                                <tr>
                                    <td style="padding: 20px;">
                                        <h3 style="color: #991b1b; margin: 0 0 10px 0; font-size: 16px; font-weight: 600;">&#128203; Hook 5 - גילוי נאות ק.303</h3>
                                        <p style="color: #991b1b; font-size: 13px; margin: 0;">&#10008; לא הושלם</p>
                                    </td>
                                </tr>
                            </table>"""

    # Determine status text
    if attachment_count == 3:
        status_text = "3 בדיקות הושלמו בהצלחה"
        status_icon = "&#10004;"
    elif attachment_count > 0:
        status_text = f"{attachment_count} מתוך 3 בדיקות הושלמו"
        status_icon = "&#9888;"
    else:
        status_text = "הבדיקות נכשלו"
        status_icon = "&#10008;"

    html = f"""<!DOCTYPE html>
<html dir="rtl" lang="he">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>דוחות בקרה חודשיים - {manager_name}</title>
</head>
<body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f6f8; direction: rtl; line-height: 1.7;">

    <table cellpadding="0" cellspacing="0" border="0" width="100%" style="background-color: #f4f6f8; padding: 40px 20px;">
        <tr>
            <td align="center">

                <table cellpadding="0" cellspacing="0" border="0" width="600" style="max-width: 600px; background-color: #ffffff; border-radius: 12px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06); overflow: hidden;">

                    <!-- Header with Logo -->
                    <tr>
                        <td style="background-color: #ffffff; padding: 30px 40px; border-bottom: 1px solid #eef1f4; text-align: center;">
                            <img src="https://storage.bhol.co.il/articles/35167_tumb_700X500.png" alt="מזרחי טפחות" style="max-height: 100px; max-width: 420px;">
                        </td>
                    </tr>

                    <!-- Status Banner -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%); padding: 45px 40px; text-align: center;">
                            <div style="width: 70px; height: 70px; background-color: rgba(255,255,255,0.2); border-radius: 50%; margin: 0 auto 20px; line-height: 70px;">
                                <span style="font-size: 32px; color: white;">&#128202;</span>
                            </div>
                            <h1 style="color: #ffffff; margin: 0 0 8px 0; font-size: 24px; font-weight: 600;">דוחות בקרה חודשיים</h1>
                            <p style="color: rgba(255,255,255,0.9); margin: 0; font-size: 18px; font-weight: 500;">{manager_name}</p>
                            <p style="color: rgba(255,255,255,0.8); margin: 10px 0 0 0; font-size: 15px; font-weight: 400;">{status_icon} {status_text}</p>
                        </td>
                    </tr>

                    <!-- Main Content -->
                    <tr>
                        <td style="padding: 40px;">

                            <!-- Info Card -->
                            <table cellpadding="0" cellspacing="0" border="0" width="100%" style="background-color: #f8fafc; border-radius: 8px; border-right: 4px solid #3B82F6;">
                                <tr>
                                    <td style="padding: 25px;">
                                        <h2 style="color: #1e293b; margin: 0 0 15px 0; font-size: 17px; font-weight: 600;">פרטי הדוח</h2>

                                        <table cellpadding="0" cellspacing="0" border="0" width="100%">
                                            <tr>
                                                <td style="padding: 8px 0; color: #64748b; font-size: 14px; width: 120px;">מנהל קרן:</td>
                                                <td style="padding: 8px 0; color: #1e293b; font-size: 14px; font-weight: 500;">{manager_name}</td>
                                            </tr>
                                            <tr>
                                                <td style="padding: 8px 0; color: #64748b; font-size: 14px;">תאריך יצירה:</td>
                                                <td style="padding: 8px 0; color: #1e293b; font-size: 14px; font-weight: 500;">{created_date}</td>
                                            </tr>
                                            <tr>
                                                <td style="padding: 8px 0; color: #64748b; font-size: 14px;">שעת יצירה:</td>
                                                <td style="padding: 8px 0; color: #1e293b; font-size: 14px; font-weight: 500;">{created_time}</td>
                                            </tr>
                                            <tr>
                                                <td style="padding: 8px 0; color: #64748b; font-size: 14px;">קבצים מצורפים:</td>
                                                <td style="padding: 8px 0; color: #1e293b; font-size: 14px; font-weight: 500;">{attachment_count}</td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>

                            {hook1_section}
                            {hook2_section}
                            {hook5_section}

                            <!-- Attachment Notice -->
                            <table cellpadding="0" cellspacing="0" border="0" width="100%" style="margin-top: 25px;">
                                <tr>
                                    <td style="background-color: #eff6ff; border-radius: 8px; padding: 18px 20px; text-align: center;">
                                        <span style="color: #3b82f6; font-size: 18px; margin-left: 8px;">&#128206;</span>
                                        <span style="color: #1e40af; font-size: 14px;">הדוחות המלאים מצורפים למייל זה כקבצי Excel</span>
                                    </td>
                                </tr>
                            </table>

                        </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #f8fafc; padding: 20px 40px; text-align: center; border-top: 1px solid #e2e8f0;">
                            <p style="margin: 0; color: #94a3b8; font-size: 12px;">
                                Powered by <a href="https://82labs.com" target="_blank" style="color: #64748b; text-decoration: none; font-weight: 600;">82Labs</a>
                            </p>
                        </td>
                    </tr>

                </table>

            </td>
        </tr>
    </table>

</body>
</html>"""

    return html


# =======================
# Email Sending
# =======================


def send_unified_email(
    to_emails: List[str],
    manager_name: str,
    hook1_xlsx: Optional[Path],
    hook2_xlsx: Optional[Path],
    hook5_xlsx: Optional[Path],
) -> Dict[str, Any]:
    """Send unified email with up to 3 XLSX attachments via Resend."""

    if not RESEND_API_KEY:
        return {"status": "skipped", "reason": "No RESEND_API_KEY configured"}

    if resend is None:
        return {"status": "skipped", "reason": "resend package not installed"}

    resend.api_key = RESEND_API_KEY

    now = datetime.now()
    created_date = now.strftime("%d/%m/%Y")
    created_time = now.strftime("%H:%M")

    # Get filenames for email body
    hook1_filename = hook1_xlsx.name if hook1_xlsx else None
    hook2_filename = hook2_xlsx.name if hook2_xlsx else None
    hook5_filename = hook5_xlsx.name if hook5_xlsx else None

    html_body = build_unified_email_html(
        manager_name,
        hook1_filename,
        hook2_filename,
        hook5_filename,
        created_date,
        created_time,
    )

    # Build attachments list
    attachments = []
    for xlsx_path in [hook1_xlsx, hook2_xlsx, hook5_xlsx]:
        if xlsx_path and xlsx_path.exists():
            with open(xlsx_path, "rb") as f:
                content = base64.b64encode(f.read()).decode("utf-8")
            attachments.append(
                {
                    "filename": xlsx_path.name,
                    "content": content,
                }
            )

    if not attachments:
        return {"status": "skipped", "reason": "No attachments to send"}

    params = {
        "from": FROM_EMAIL,
        "to": to_emails,
        "subject": f"דוחות בקרה חודשיים - {manager_name}",
        "html": html_body,
        "attachments": attachments,
    }

    try:
        response = resend.Emails.send(params)
        log_success(
            f"Email sent to {', '.join(to_emails)} with {len(attachments)} attachments"
        )
        return {"status": "sent", "response": response}
    except Exception as e:
        log_error(f"Email sending failed: {e}")
        return {"status": "failed", "error": str(e)}


# =======================
# Main Processing
# =======================


async def process_manager(
    manager_name: str,
    output_dir: Path,
    funds_list_path: Path,
    skip_tase_prices: bool = True,
) -> Dict[str, Any]:
    """Process all hooks for a single manager."""

    log(f"\n{'=' * 60}")
    log(f"Processing manager: {manager_name}")
    log(f"{'=' * 60}")

    results = {
        "manager_name": manager_name,
        "status": "pending",
        "hook1": {"status": "pending", "xlsx": None},
        "hook2": {"status": "pending", "xlsx": None},
        "hook5": {"status": "pending", "xlsx": None},
    }

    manager_dir = output_dir / manager_name
    manager_dir.mkdir(parents=True, exist_ok=True)

    # Get current report month
    report_month = datetime.now().strftime("%Y-%m")

    # Process Hook 1
    try:
        log_info(f"Fetching Hook 1 data for {manager_name}...")
        current, previous, _ = await run_apify_scraper(manager_name, "hook1")

        # Save temp files
        current_path = manager_dir / f"hook1_{manager_name}_current.csv"
        previous_path = manager_dir / f"hook1_{manager_name}_previous.csv"
        current_path.write_bytes(current)
        if previous:
            previous_path.write_bytes(previous)

        # Run Hook 1
        hook1_xlsx = run_hook1(manager_name, manager_dir)
        results["hook1"]["status"] = "success" if hook1_xlsx else "failed"
        results["hook1"]["xlsx"] = hook1_xlsx

    except Exception as e:
        log_error(f"Hook 1 error for {manager_name}: {e}")
        results["hook1"]["status"] = "failed"
        results["hook1"]["error"] = str(e)

    # Process Hook 2
    try:
        log_info(f"Fetching Hook 2 data for {manager_name}...")
        current, _, _ = await run_apify_scraper(manager_name, "hook2")

        # Save temp file
        report_path = manager_dir / f"hook2_{manager_name}_report.csv"
        report_path.write_bytes(current)

        # Run Hook 2
        hook2_xlsx = run_hook2(
            manager_name,
            funds_list_path,
            report_path,
            manager_dir,
            skip_tase_prices,
        )
        results["hook2"]["status"] = "success" if hook2_xlsx else "failed"
        results["hook2"]["xlsx"] = hook2_xlsx

    except Exception as e:
        log_error(f"Hook 2 error for {manager_name}: {e}")
        results["hook2"]["status"] = "failed"
        results["hook2"]["error"] = str(e)

    # Process Hook 5
    try:
        log_info(f"Fetching Hook 5 data for {manager_name}...")
        current, previous = await run_k303_apify_scraper(manager_name)

        # Save temp files
        current_path = manager_dir / f"hook5_{manager_name}_current.csv"
        previous_path = manager_dir / f"hook5_{manager_name}_previous.csv"
        current_path.write_bytes(current)
        if previous:
            previous_path.write_bytes(previous)
        else:
            # Create empty previous file if not available
            previous_path.write_bytes(b"")

        # Run Hook 5
        hook5_xlsx = run_hook5(
            manager_name,
            funds_list_path,
            current_path,
            previous_path,
            manager_dir,
            report_month,
        )
        results["hook5"]["status"] = "success" if hook5_xlsx else "failed"
        results["hook5"]["xlsx"] = hook5_xlsx

    except Exception as e:
        log_error(f"Hook 5 error for {manager_name}: {e}")
        results["hook5"]["status"] = "failed"
        results["hook5"]["error"] = str(e)

    # Determine overall status
    statuses = [
        results["hook1"]["status"],
        results["hook2"]["status"],
        results["hook5"]["status"],
    ]
    if all(s == "success" for s in statuses):
        results["status"] = "success"
    elif any(s == "success" for s in statuses):
        results["status"] = "partial"
    else:
        results["status"] = "failed"

    return results


async def main_async(args: argparse.Namespace) -> int:
    """Async main function."""

    log("=" * 60)
    log("UNIFIED BATCH PROCESSOR - ALL HOOKS")
    log("=" * 60)

    # Validate environment
    if not APIFY_API_TOKEN:
        log_error("APIFY_API_TOKEN environment variable is required")
        return 1

    if args.send_email and not RESEND_API_KEY:
        log_error("RESEND_API_KEY environment variable is required for --send-email")
        return 1

    # Determine managers to process
    if args.managers:
        manager_names = [m.strip() for m in args.managers.split(",")]
        managers = {n: FUND_MANAGERS[n] for n in manager_names if n in FUND_MANAGERS}
        invalid = [n for n in manager_names if n not in FUND_MANAGERS]
        if invalid:
            log_error(f"Unknown managers: {invalid}")
            log_info(f"Valid managers: {list(FUND_MANAGERS.keys())}")
            return 1
    else:
        managers = FUND_MANAGERS

    log_info(f"Processing {len(managers)} managers: {list(managers.keys())}")
    log_info(f"Email recipient: {args.email}")
    log_info(f"Send email: {args.send_email}")

    # Create output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    batch_dir = args.output_dir / timestamp
    batch_dir.mkdir(parents=True, exist_ok=True)
    log_info(f"Output directory: {batch_dir}")

    # Download shared funds list
    try:
        funds_content = await download_main_funds_list()
        funds_list_path = batch_dir / "Mutual_Funds_List.xlsx"
        funds_list_path.write_bytes(funds_content)
        log_success(f"Saved funds list to {funds_list_path.name}")
    except Exception as e:
        log_error(f"Failed to download funds list: {e}")
        return 1

    # Process each manager
    all_results = []
    for manager_name in managers.keys():
        try:
            result = await process_manager(
                manager_name,
                batch_dir,
                funds_list_path,
                args.skip_tase_prices,
            )
            all_results.append(result)

            # Send email if requested
            if args.send_email and result["status"] in ("success", "partial"):
                email_result = send_unified_email(
                    [args.email],
                    manager_name,
                    result["hook1"].get("xlsx"),
                    result["hook2"].get("xlsx"),
                    result["hook5"].get("xlsx"),
                )
                result["email"] = email_result

        except Exception as e:
            log_error(f"Error processing {manager_name}: {e}")
            all_results.append(
                {
                    "manager_name": manager_name,
                    "status": "failed",
                    "error": str(e),
                }
            )

    # Save summary
    summary = {
        "processing_date": datetime.now().isoformat(),
        "total_managers": len(managers),
        "successful": sum(1 for r in all_results if r["status"] == "success"),
        "partial": sum(1 for r in all_results if r["status"] == "partial"),
        "failed": sum(1 for r in all_results if r["status"] == "failed"),
        "results": [
            {
                "manager": r["manager_name"],
                "status": r["status"],
                "hook1": r.get("hook1", {}).get("status"),
                "hook2": r.get("hook2", {}).get("status"),
                "hook5": r.get("hook5", {}).get("status"),
            }
            for r in all_results
        ],
    }

    summary_path = batch_dir / "batch_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    # Print summary
    log("\n" + "=" * 60)
    log("BATCH PROCESSING COMPLETE")
    log("=" * 60)
    log(f"Total managers: {summary['total_managers']}")
    log(f"Successful: {summary['successful']}")
    log(f"Partial: {summary['partial']}")
    log(f"Failed: {summary['failed']}")
    log(f"Output directory: {batch_dir}")
    log(f"Summary file: {summary_path}")

    return 0


def main() -> int:
    """Main entry point."""

    parser = argparse.ArgumentParser(
        description="Unified batch processor for all hooks (Hook 1, 2, 5)"
    )
    parser.add_argument(
        "--managers",
        help="Comma-separated list of manager names (default: all 10)",
        default=None,
    )
    parser.add_argument(
        "--email",
        default=DEFAULT_EMAIL,
        help=f"Email recipient (default: {DEFAULT_EMAIL})",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("./output/batch_all"),
        help="Output directory (default: ./output/batch_all)",
    )
    parser.add_argument(
        "--skip-tase-prices",
        action="store_true",
        default=True,
        help="Skip TASE price checks in Hook 2 (default: True)",
    )
    parser.add_argument(
        "--send-email",
        action="store_true",
        help="Send emails after processing",
    )

    args = parser.parse_args()

    return asyncio.run(main_async(args))


if __name__ == "__main__":
    sys.exit(main())
