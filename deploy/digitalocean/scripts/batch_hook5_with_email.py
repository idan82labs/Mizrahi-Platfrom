#!/usr/bin/env python3
"""
Batch Hook 5 - K.303 Disclosure Validation
Runs Hook 5 for all fund managers and sends individual branded emails.

Usage:
    python batch_hook5_with_email.py --email "idan.t@82labs.io,elay.g@82labs.io"
    python batch_hook5_with_email.py --managers "מגדל,הראל" --email "test@test.com"
    python batch_hook5_with_email.py --email "test@test.com" --report-month "2025-12"
"""

import re
import sys
import argparse
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Tuple

import requests

from hook_utils import (
    FUND_MANAGERS, SCRIPTS_DIR, log, extract_error,
    apify_request, run_actor_and_wait, fetch_funds_list,
    send_hook_email, send_failure_alert, save_batch_summary,
)

HOOK5_SCRIPT = SCRIPTS_DIR / "disclosure_k303_validator.py"
SPEC_FILE = SCRIPTS_DIR / "k303_spec.xlsx"
K303_REPORTS_ACTOR_ID = "iTpNz9ixbdQCmH43C"

HOOK5_COLOR = "#10B981"
HOOK5_COLOR_LIGHT = "#d1fae5"

HEBREW_MONTHS = {
    "ינואר": 1, "פברואר": 2, "מרץ": 3, "אפריל": 4,
    "מאי": 5, "יוני": 6, "יולי": 7, "אוגוסט": 8,
    "ספטמבר": 9, "אוקטובר": 10, "נובמבר": 11, "דצמבר": 12,
}


def build_maya_url_k303(item_id: str) -> str:
    """Build Maya URL for K.303 disclosure reports."""
    today = datetime.now()
    one_year_ago = today - timedelta(days=365)
    return (
        f"https://maya.tase.co.il/he/reports/etfs?"
        f"fromDate={one_year_ago.strftime('%Y-%m-%d')}"
        f"&toDate={today.strftime('%Y-%m-%d')}"
        f"&noMeetings=false&isPriority=false&isSingle=false"
        f"&isIntendToTaseMember=false"
        f"&by=group&formId=%D7%A7303&groupId=7&itemId={item_id}"
    )


def _extract_report_month(report_name: str) -> Optional[str]:
    """Extract YYYY-MM from Hebrew report name."""
    for heb_month, num_month in HEBREW_MONTHS.items():
        if heb_month in report_name:
            year_match = re.search(r'20\d{2}', report_name)
            if year_match:
                month_str = f"{year_match.group()}-{num_month:02d}"
                log(f"Extracted report month: {month_str}")
                return month_str
    return None


def fetch_k303_reports(
    manager_name: str, manager_dir: Path,
) -> Tuple[Path, Path, Optional[str]]:
    """Fetch K.303 current and previous month CSVs for a manager."""
    item_id = FUND_MANAGERS[manager_name]
    maya_url = build_maya_url_k303(item_id)

    log(f"Fetching K.303 reports for {manager_name} (code: {item_id})...")

    run_data = run_actor_and_wait(
        K303_REPORTS_ACTOR_ID, {"url": maya_url}, timeout=600,
    )
    kv_store_id = run_data["defaultKeyValueStoreId"]
    dataset_id = run_data["defaultDatasetId"]

    report_month = None
    try:
        resp = apify_request("GET", f"/datasets/{dataset_id}/items")
        items = resp.json()
        if items and items[0].get("downloadedFiles"):
            report_name = items[0]["downloadedFiles"][0].get("reportName", "")
            log(f"Report name: {report_name}")
            report_month = _extract_report_month(report_name)
    except Exception as e:
        log(f"Warning: Could not extract report month: {e}")

    current_path = manager_dir / "report_current.csv"
    resp = apify_request(
        "GET", f"/key-value-stores/{kv_store_id}/records/report_latest_month.csv",
    )
    current_path.write_bytes(resp.content)
    log(f"Saved current report: {current_path} ({len(resp.content)} bytes)")

    previous_path = manager_dir / "report_previous.csv"
    try:
        resp = apify_request(
            "GET", f"/key-value-stores/{kv_store_id}/records/report_previous_month.csv",
        )
        previous_path.write_bytes(resp.content)
        log(f"Saved previous report: {previous_path} ({len(resp.content)} bytes)")
    except requests.exceptions.HTTPError as e:
        if e.response is not None and e.response.status_code == 404:
            previous_path.write_bytes(b"")
            log("No previous month report available (empty file created)")
        else:
            raise

    return current_path, previous_path, report_month


def run_hook5_for_manager(
    manager_name: str,
    output_dir: Path,
    funds_list_path: Path,
    report_month: Optional[str] = None,
    max_retries: int = 3,
    retry_delay: int = 30,
) -> Tuple[Optional[Path], str]:
    """Run Hook 5 for a single manager with retry logic."""
    manager_dir = output_dir / manager_name
    manager_dir.mkdir(parents=True, exist_ok=True)

    last_error = ""
    for attempt in range(1, max_retries + 1):
        if attempt > 1:
            log(f"Retry {attempt}/{max_retries} for {manager_name} (waiting {retry_delay}s)...")
            time.sleep(retry_delay)
        else:
            log(f"Running Hook 5 for {manager_name}...")

        try:
            current_path, previous_path, scraped_month = fetch_k303_reports(
                manager_name, manager_dir,
            )

            effective_month = report_month or scraped_month
            if not effective_month:
                first_of_month = datetime.now().replace(day=1)
                effective_month = (first_of_month - timedelta(days=1)).strftime("%Y-%m")
                log(f"Fallback report month: {effective_month}")

            output_xlsx = (
                manager_dir / f"k303_validation_{manager_name}_{effective_month}.xlsx"
            )

            cmd = [
                sys.executable, str(HOOK5_SCRIPT),
                "--mutual-funds-list", str(funds_list_path),
                "--current-report", str(current_path),
                "--previous-report", str(previous_path),
                "--output-xlsx", str(output_xlsx),
                "--manager-name", manager_name,
                "--report-month", effective_month,
            ]

            if SPEC_FILE.exists():
                cmd.extend(["--spec-file", str(SPEC_FILE)])

            result = subprocess.run(
                cmd, capture_output=True, text=True,
                timeout=900, cwd=str(SCRIPTS_DIR),
            )

            if result.returncode != 0:
                last_error = extract_error(result.stderr)
                log(f"Hook 5 failed for {manager_name} (attempt {attempt}): {last_error}")
                continue

            if output_xlsx.exists():
                log(f"Hook 5 completed: {output_xlsx.name}")
                return output_xlsx, ""

            last_error = "No output file generated"
            log(f"No output file found for {manager_name} (attempt {attempt})")

        except subprocess.TimeoutExpired:
            last_error = "Process timed out (15 min)"
            log(f"Hook 5 timed out for {manager_name} (attempt {attempt})")
        except requests.exceptions.HTTPError as e:
            last_error = f"Apify HTTP error: {e}"
            log(f"Apify error for {manager_name} (attempt {attempt}): {e}")
        except Exception as e:
            last_error = str(e)
            log(f"Hook 5 error for {manager_name} (attempt {attempt}): {e}")

    log(f"Hook 5 FAILED for {manager_name} after {max_retries} attempts")
    return None, last_error


def _report_month_row(report_month: str) -> str:
    """Build extra HTML table row for report month."""
    return (
        f'\n                <tr style="border-bottom: 1px solid #f1f5f9;">'
        f'\n                    <td style="padding: 14px 0; font-size: 15px; '
        f'color: #6b7280; text-align: right;">חודש דיווח:</td>'
        f'\n                    <td style="padding: 14px 0; font-size: 15px; '
        f'color: #1f2937; font-weight: 500; text-align: left;">'
        f'{report_month}</td>'
        f'\n                </tr>'
    )


def main():
    parser = argparse.ArgumentParser(description="Batch Hook 5 - K.303 Disclosure")
    parser.add_argument(
        "--managers", default=",".join(FUND_MANAGERS.keys()),
        help=f"Comma-separated managers (default: all {len(FUND_MANAGERS)})",
    )
    parser.add_argument("--email", required=True, help="Comma-separated email addresses")
    parser.add_argument("--output-dir", default="output/batch_hook5", help="Output directory")
    parser.add_argument(
        "--report-month", default=None,
        help="Report month YYYY-MM (default: auto-detected from Apify)",
    )

    args = parser.parse_args()

    if args.report_month and not re.match(r'^\d{4}-(0[1-9]|1[0-2])$', args.report_month):
        log(f"ERROR: Invalid --report-month format: '{args.report_month}' (expected YYYY-MM)")
        return 1

    managers = [m.strip() for m in args.managers.split(",") if m.strip()]
    emails = [e.strip() for e in args.email.split(",") if e.strip()]

    invalid = [m for m in managers if m not in FUND_MANAGERS]
    if invalid:
        log(f"ERROR: Unknown managers: {invalid}")
        return 1

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = (SCRIPTS_DIR / args.output_dir / timestamp).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    log("=" * 60)
    log("BATCH HOOK 5 - K.303 DISCLOSURE VALIDATION")
    log("=" * 60)
    log(f"Managers: {len(managers)}")
    log(f"Emails: {', '.join(emails)}")
    log(f"Output: {output_dir}")
    if args.report_month:
        log(f"Report month: {args.report_month}")
    log("=" * 60)

    log("")
    log("STEP 1: Fetching Mutual Funds List")
    log("-" * 40)
    try:
        funds_list_path = fetch_funds_list(output_dir)
    except Exception as e:
        log(f"FATAL: Failed to fetch funds list: {e}")
        return 1

    log("")
    log("STEP 2: Processing Managers")
    log("-" * 40)

    results = []
    emails_sent = 0

    for manager in managers:
        log("")
        xlsx_path, error_msg = run_hook5_for_manager(
            manager, output_dir, funds_list_path, args.report_month,
        )

        if xlsx_path:
            report_month_str = args.report_month or ""
            if not report_month_str:
                parts = xlsx_path.stem.split("_")
                if len(parts) >= 2:
                    report_month_str = parts[-1]

            results.append({
                "manager": manager, "status": "success",
                "filename": xlsx_path.name, "report_month": report_month_str,
            })

            title = f"דוח גילוי נאות ק.303 - {report_month_str}"
            subject = f"דוח גילוי נאות ק.303 - {manager} - {report_month_str}"
            extra_rows = _report_month_row(report_month_str)
            if send_hook_email(
                emails, manager, xlsx_path, subject,
                HOOK5_COLOR, HOOK5_COLOR_LIGHT, title, extra_rows,
            ):
                emails_sent += 1
        else:
            results.append({"manager": manager, "status": "failed", "error": error_msg})

    log("")
    log("=" * 60)
    log("BATCH PROCESSING COMPLETE")
    log("=" * 60)

    successful = len([r for r in results if r["status"] == "success"])
    failed = len([r for r in results if r["status"] == "failed"])
    log(f"Reports generated: {successful}/{len(managers)}")
    log(f"Emails sent: {emails_sent}/{successful}")
    log(f"Failed: {failed}/{len(managers)}")

    summary_path = save_batch_summary(
        output_dir, "hook5", "K.303 Disclosure Validation",
        managers, results, emails_sent,
    )
    log(f"Summary saved to: {summary_path}")

    failed_managers = [r for r in results if r["status"] == "failed"]
    if failed_managers:
        log("")
        log("Sending failure alert email...")
        send_failure_alert(
            emails, "Hook 5 - K.303 Disclosure",
            failed_managers, successful, len(managers),
        )

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
