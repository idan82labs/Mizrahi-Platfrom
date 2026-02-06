#!/usr/bin/env python3
"""
Shared utilities for Mizrahi Compliance Platform batch hooks.

Provides common constants, logging, Apify integration, and email helpers
used by all batch_hook*_with_email.py scripts.
"""

import os
import sys
import time
import base64
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
import resend
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

# ============================================================================
# CONSTANTS
# ============================================================================

FUND_MANAGERS = {
    "מגדל": "10040",
    "קסם": "10047",
    "סיגמא": "10048",
    "הראל": "10031",
    "אנליסט": "10019",
    "מיטב": "10083",
    "איביאי": "10068",
    "אלטשולר-שחם": "10017",
}

SCRIPTS_DIR = Path(__file__).parent.resolve()

RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@notifications.82labs.io")
APIFY_API_TOKEN = os.getenv("APIFY_API_TOKEN", "")

FUNDS_LIST_ACTOR_ID = "K9WppTziYC3n2vxTu"

MIZRAHI_LOGO_URL = (
    "https://raw.githubusercontent.com/idan82labs/"
    "Mizrahi-Automations/special-transactions/assets/mizrahi_logo.png"
)
MIZRAHI_LOGO_IMG = (
    f'<img src="{MIZRAHI_LOGO_URL}" alt="מזרחי טפחות" '
    f'width="180" height="68" style="display: block; margin: 0 auto;" />'
)


# ============================================================================
# LOGGING
# ============================================================================


def log(msg: str) -> None:
    """Print timestamped log message."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}", flush=True)


# ============================================================================
# APIFY HELPERS
# ============================================================================


def apify_request(
    method: str,
    endpoint: str,
    json_data: Any = None,
    params: Any = None,
) -> requests.Response:
    """Make authenticated request to Apify API."""
    url = f"https://api.apify.com/v2{endpoint}"
    headers = {"Authorization": f"Bearer {APIFY_API_TOKEN}"}
    response = requests.request(
        method, url, headers=headers, json=json_data, params=params
    )
    response.raise_for_status()
    return response


def run_actor_and_wait(
    actor_id: str,
    input_data: Any = None,
    timeout: int = 300,
) -> Dict[str, Any]:
    """Run an Apify actor and poll until completion."""
    log(f"Starting Apify actor: {actor_id}")

    resp = apify_request(
        "POST",
        f"/acts/{actor_id}/runs",
        json_data=input_data or {},
        params={"timeout": timeout},
    )
    run_data = resp.json()["data"]
    run_id = run_data["id"]
    log(f"Run started: {run_id}")

    start = time.time()
    while time.time() - start < timeout:
        resp = apify_request("GET", f"/actor-runs/{run_id}")
        status = resp.json()["data"]["status"]

        if status == "SUCCEEDED":
            log(f"Actor run completed: {run_id}")
            return resp.json()["data"]
        if status in ("FAILED", "ABORTED", "TIMED-OUT"):
            raise RuntimeError(f"Actor failed with status: {status}")

        log(f"Status: {status}... waiting")
        time.sleep(5)

    raise TimeoutError("Timeout waiting for actor")


def fetch_funds_list(output_dir: Path) -> Path:
    """Fetch mutual funds list from Apify (once, shared across managers)."""
    log("Fetching Mutual Funds List from Apify...")

    run_data = run_actor_and_wait(FUNDS_LIST_ACTOR_ID, {})
    dataset_id = run_data["defaultDatasetId"]

    resp = apify_request("GET", f"/datasets/{dataset_id}/items")
    items = resp.json()

    if not items or not items[0].get("fileBase64"):
        raise RuntimeError("No fileBase64 in Apify response")

    funds_list_bytes = base64.b64decode(items[0]["fileBase64"])
    funds_list_path = output_dir / "Mutual_Funds_List.xlsx"
    funds_list_path.write_bytes(funds_list_bytes)

    log(f"Saved Mutual Funds List: {funds_list_path} ({len(funds_list_bytes)} bytes)")
    return funds_list_path


# ============================================================================
# EMAIL HELPERS
# ============================================================================


def build_hook_email_html(
    color: str,
    color_light: str,
    title: str,
    manager_name: str,
    report_filename: str,
    created_date: str,
    created_time: str,
    extra_rows: str = "",
) -> str:
    """Build branded HTML email for any hook. Parameterized by color and title."""
    return f'''<!DOCTYPE html>
<html dir="rtl" lang="he">
<head><meta charset="UTF-8"><title>{title}</title></head>
<body style="font-family: 'Segoe UI', Tahoma, Arial, sans-serif; direction: rtl; margin: 0; padding: 0; background: #f1f5f9;">
    <div style="max-width: 650px; margin: 0 auto; padding: 40px 20px;">
        <div style="text-align: center; margin-bottom: 30px;">{MIZRAHI_LOGO_IMG}</div>
        <div style="background: {color}; border-radius: 12px; padding: 50px 20px; text-align: center; margin-bottom: 25px;">
            <table align="center" border="0" cellpadding="0" cellspacing="0" style="margin: 0 auto 25px;">
                <tr><td style="width: 80px; height: 80px; background: rgba(255,255,255,0.25); border-radius: 50%; text-align: center; vertical-align: middle; font-size: 36px; color: white;">&#10003;</td></tr>
            </table>
            <h1 style="color: white; font-size: 28px; margin: 0 0 12px 0; font-weight: 600;">{title}</h1>
            <p style="color: rgba(255,255,255,0.85); font-size: 16px; margin: 0;">הדוח נוצר בהצלחה</p>
        </div>
        <div style="background: white; border-radius: 12px; padding: 30px 35px; margin-bottom: 20px; border-left: 4px solid {color}; box-shadow: 0 1px 3px rgba(0,0,0,0.08);">
            <h2 style="font-size: 20px; color: #1f2937; margin: 0 0 25px 0; font-weight: 600; text-align: right;">פרטי הדוח</h2>
            <table style="width: 100%; border-collapse: collapse;">
                <tr style="border-bottom: 1px solid #f1f5f9;">
                    <td style="padding: 14px 0; font-size: 15px; color: #6b7280; text-align: right; width: 120px;">מנהל קרן:</td>
                    <td style="padding: 14px 0; font-size: 15px; color: #1f2937; font-weight: 500; text-align: left;">{manager_name}</td>
                </tr>{extra_rows}
                <tr style="border-bottom: 1px solid #f1f5f9;">
                    <td style="padding: 14px 0; font-size: 15px; color: #6b7280; text-align: right;">שם הדוח:</td>
                    <td style="padding: 14px 0; font-size: 15px; color: #1f2937; font-weight: 500; text-align: left;">{report_filename}</td>
                </tr>
                <tr style="border-bottom: 1px solid #f1f5f9;">
                    <td style="padding: 14px 0; font-size: 15px; color: #6b7280; text-align: right;">תאריך יצירה:</td>
                    <td style="padding: 14px 0; font-size: 15px; color: #1f2937; font-weight: 500; text-align: left;">{created_date}</td>
                </tr>
                <tr>
                    <td style="padding: 14px 0; font-size: 15px; color: #6b7280; text-align: right;">שעת יצירה:</td>
                    <td style="padding: 14px 0; font-size: 15px; color: #1f2937; font-weight: 500; text-align: left;">{created_time}</td>
                </tr>
            </table>
        </div>
        <div style="background: {color_light}; border-radius: 12px; padding: 18px 25px; text-align: center; margin-bottom: 25px;">
            <span style="font-size: 15px; color: #1f2937;">&#128206; הדוח מצורף למייל זה כקובץ Excel</span>
        </div>
        <div style="text-align: center; padding-top: 15px; border-top: 1px solid #e5e7eb;">
            <span style="font-size: 13px; color: #9ca3af;">פותח על ידי <strong style="color: #6b7280;">82Labs</strong></span>
        </div>
    </div>
</body>
</html>'''


def build_failure_alert_html(
    hook_label: str,
    failed_managers: List[Dict[str, Any]],
    successful_count: int,
    total_count: int,
) -> str:
    """Build failure alert email HTML."""
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
    failure_rows = ""
    for f in failed_managers:
        failure_rows += (
            f'<tr><td style="padding: 12px; border-bottom: 1px solid #fecaca;">'
            f'{f["manager"]}</td>'
            f'<td style="padding: 12px; border-bottom: 1px solid #fecaca; color: #dc2626;">'
            f'{f.get("error", "Unknown error")[:100]}</td></tr>'
        )

    return f'''<!DOCTYPE html>
<html dir="rtl" lang="he">
<head><meta charset="UTF-8"><title>התראה - כשלון בעיבוד דוחות</title></head>
<body style="font-family: 'Segoe UI', Tahoma, Arial, sans-serif; direction: rtl; margin: 0; padding: 40px 20px; background: #fef2f2;">
    <div style="max-width: 600px; margin: 0 auto;">
        <div style="text-align: center; margin-bottom: 30px;">{MIZRAHI_LOGO_IMG}</div>
        <div style="background: #dc2626; border-radius: 16px; padding: 40px 20px; text-align: center; margin-bottom: 30px;">
            <table align="center" border="0" cellpadding="0" cellspacing="0" style="margin: 0 auto 20px;">
                <tr><td style="width: 60px; height: 60px; background: rgba(255,255,255,0.2); border-radius: 12px; text-align: center; vertical-align: middle; font-size: 28px; color: white;">&#9888;</td></tr>
            </table>
            <h1 style="color: white; font-size: 24px; margin: 0; font-weight: 600;">התראה - כשלון בעיבוד דוחות</h1>
            <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0;">{hook_label}</p>
        </div>
        <div style="background: white; border-radius: 12px; padding: 25px 30px; margin-bottom: 20px; border-right: 4px solid #dc2626;">
            <h2 style="font-size: 18px; color: #1f2937; margin: 0 0 20px 0; font-weight: 600;">סיכום</h2>
            <table style="width: 100%; border-collapse: collapse;">
                <tr style="border-bottom: 1px solid #f1f5f9;">
                    <td style="padding: 12px 0; font-size: 14px; color: #6b7280;">תאריך:</td>
                    <td style="padding: 12px 0; font-size: 14px; color: #1f2937; font-weight: 500;">{timestamp}</td>
                </tr>
                <tr style="border-bottom: 1px solid #f1f5f9;">
                    <td style="padding: 12px 0; font-size: 14px; color: #6b7280;">הצליחו:</td>
                    <td style="padding: 12px 0; font-size: 14px; color: #059669; font-weight: 500;">{successful_count}/{total_count}</td>
                </tr>
                <tr>
                    <td style="padding: 12px 0; font-size: 14px; color: #6b7280;">נכשלו:</td>
                    <td style="padding: 12px 0; font-size: 14px; color: #dc2626; font-weight: 500;">{len(failed_managers)}/{total_count}</td>
                </tr>
            </table>
        </div>
        <div style="background: white; border-radius: 12px; padding: 25px 30px; margin-bottom: 20px;">
            <h2 style="font-size: 18px; color: #dc2626; margin: 0 0 20px 0; font-weight: 600;">מנהלים שנכשלו</h2>
            <table style="width: 100%; border-collapse: collapse;">
                <thead><tr style="background: #fef2f2;">
                    <th style="padding: 12px; text-align: right; border-bottom: 2px solid #fecaca;">מנהל</th>
                    <th style="padding: 12px; text-align: right; border-bottom: 2px solid #fecaca;">שגיאה</th>
                </tr></thead>
                <tbody>{failure_rows}</tbody>
            </table>
        </div>
        <div style="background: #fef3c7; border-radius: 8px; padding: 15px 20px; text-align: right;">
            <span style="font-size: 14px; color: #92400e;">&#9888; כל מנהל נוסה 3 פעמים לפני שסומן ככשלון</span>
        </div>
    </div>
</body>
</html>'''


def send_email(
    to_emails: List[str],
    subject: str,
    html_body: str,
    attachments: Optional[List[Dict[str, str]]] = None,
) -> bool:
    """Send email via Resend API."""
    if not RESEND_API_KEY:
        log("RESEND_API_KEY not configured - skipping email")
        return False

    resend.api_key = RESEND_API_KEY

    params: Dict[str, Any] = {
        "from": FROM_EMAIL,
        "to": to_emails,
        "subject": subject,
        "html": html_body,
    }
    if attachments:
        params["attachments"] = attachments

    try:
        resend.Emails.send(params)
        log(f"Email sent to {', '.join(to_emails)}")
        return True
    except Exception as e:
        log(f"Email failed: {e}")
        return False


def send_hook_email(
    to_emails: List[str],
    manager_name: str,
    xlsx_path: Path,
    subject: str,
    color: str,
    color_light: str,
    title: str,
    extra_rows: str = "",
) -> bool:
    """Send branded email for a hook with XLSX attachment."""
    now = datetime.now()
    html_body = build_hook_email_html(
        color, color_light, title,
        manager_name, xlsx_path.name,
        now.strftime("%d/%m/%Y"), now.strftime("%H:%M"),
        extra_rows,
    )

    with open(xlsx_path, "rb") as f:
        content = base64.b64encode(f.read()).decode("utf-8")

    return send_email(
        to_emails, subject, html_body,
        [{"filename": xlsx_path.name, "content": content}],
    )


def send_failure_alert(
    to_emails: List[str],
    hook_label: str,
    failed_managers: List[Dict[str, Any]],
    successful_count: int,
    total_count: int,
) -> bool:
    """Send failure alert email for a hook."""
    if not failed_managers:
        return True

    html = build_failure_alert_html(
        hook_label, failed_managers, successful_count, total_count
    )
    subject = f"התראה - {len(failed_managers)} מנהלים נכשלו בעיבוד {hook_label}"
    return send_email(to_emails, subject, html)


def save_batch_summary(
    output_dir: Path,
    hook: str,
    hook_name: str,
    managers: List[str],
    results: List[Dict],
    emails_sent: int,
) -> Path:
    """Save batch processing summary JSON."""
    summary_path = output_dir / "batch_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "hook": hook,
            "hook_name": hook_name,
            "managers": managers,
            "results": results,
            "successful": len([r for r in results if r["status"] == "success"]),
            "failed": len([r for r in results if r["status"] == "failed"]),
            "emails_sent": emails_sent,
        }, f, ensure_ascii=False, indent=2)

    return summary_path


def extract_error(stderr: str) -> str:
    """Extract meaningful error message from subprocess stderr."""
    if not stderr:
        return "Process returned non-zero exit code"
    for line in reversed(stderr.strip().split('\n')):
        if 'ERROR' in line or 'Exception' in line:
            return line[:200]
    return "Process returned non-zero exit code"
