#!/usr/bin/env python3
"""
Batch Hook 2 - Special Transactions Validation
Runs Hook 2 for all fund managers and sends individual branded emails.

Usage:
    python batch_hook2_with_email.py --email "idan.t@82labs.io,elay.g@82labs.io"
    python batch_hook2_with_email.py --managers "מגדל,הראל" --email "test@test.com"
    python batch_hook2_with_email.py --email "test@test.com" --spec-file spec-file.xlsx
"""

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

HOOK2_SCRIPT = SCRIPTS_DIR / "mizrahi_special_transactions.py"
HOOK2_COLOR = "#F5821F"
HOOK2_COLOR_LIGHT = "#fff3e0"
FUND_REPORTS_ACTOR_ID = "5lhI6O39Qbgv9O0gs"


def build_maya_url_hook2(fund_code: str) -> str:
    """Build Maya URL for special transactions reports (eventsId=5615)."""
    today = datetime.now()
    one_year_ago = today - timedelta(days=365)
    return (
        f"https://maya.tase.co.il/he/reports/funds?"
        f"fromDate={one_year_ago.strftime('%Y-%m-%d')}"
        f"&toDate={today.strftime('%Y-%m-%d')}"
        f"&noMeetings=false&isSingle=false&isIntendToTaseMember=false"
        f"&by=group&groupId=7&itemId={fund_code}&eventsIds%5B%5D=5615"
    )


def fetch_manager_report(
    manager_name: str, fund_code: str, manager_dir: Path,
) -> Optional[Path]:
    """Fetch special transactions CSV from Apify."""
    log(f"Fetching special transactions for {manager_name} (code: {fund_code})...")

    maya_url = build_maya_url_hook2(fund_code)
    run_data = run_actor_and_wait(
        FUND_REPORTS_ACTOR_ID, {"url": maya_url}, timeout=300,
    )

    kv_store_id = run_data["defaultKeyValueStoreId"]
    for key in ["report_latest_month.csv", "special_transactions.csv", "report.csv"]:
        try:
            resp = apify_request(
                "GET", f"/key-value-stores/{kv_store_id}/records/{key}",
            )
            if resp.status_code == 200:
                report_path = manager_dir / f"{manager_name}_special_transactions.csv"
                report_path.write_bytes(resp.content)
                log(f"Saved report: {report_path} ({len(resp.content)} bytes)")
                return report_path
        except requests.exceptions.HTTPError:
            continue

    log(f"No report found in key-value store for {manager_name}")
    return None


def run_hook2_for_manager(
    manager_name: str,
    output_dir: Path,
    funds_list_path: Path,
    spec_file: Optional[Path] = None,
    skip_tase_prices: bool = True,
    max_retries: int = 3,
    retry_delay: int = 30,
) -> Tuple[Optional[Path], str]:
    """Run Hook 2 for a single manager with retry logic."""
    manager_dir = output_dir / manager_name
    manager_dir.mkdir(parents=True, exist_ok=True)

    fund_code = FUND_MANAGERS[manager_name]
    last_error = ""

    for attempt in range(1, max_retries + 1):
        if attempt > 1:
            log(f"Retry {attempt}/{max_retries} for {manager_name} (waiting {retry_delay}s)...")
            time.sleep(retry_delay)
        else:
            log(f"Running Hook 2 for {manager_name}...")

        try:
            report_path = fetch_manager_report(manager_name, fund_code, manager_dir)
            if not report_path:
                last_error = "No report available from Apify"
                continue

            output_xlsx = manager_dir / f"{manager_name}_special_transactions_report.xlsx"
            email_json = manager_dir / f"{manager_name}_email.json"

            cmd = [
                sys.executable, str(HOOK2_SCRIPT),
                "--mutual-funds-list", str(funds_list_path),
                "--input-report", str(report_path),
                "--output-xlsx", str(output_xlsx),
                "--email-json", str(email_json),
                "--manager-name", manager_name,
            ]

            if skip_tase_prices:
                cmd.append("--skip-tase-prices")
            if spec_file and spec_file.exists():
                cmd.extend(["--spec-file", str(spec_file)])

            result = subprocess.run(
                cmd, capture_output=True, text=True,
                timeout=900, cwd=str(SCRIPTS_DIR),
            )

            if result.returncode != 0:
                last_error = extract_error(result.stderr)
                log(f"Hook 2 failed for {manager_name} (attempt {attempt}): {last_error}")
                continue

            if output_xlsx.exists():
                log(f"Hook 2 completed: {output_xlsx.name}")
                return output_xlsx, ""

            last_error = "No output file generated"
            log(f"No output file found for {manager_name} (attempt {attempt})")

        except subprocess.TimeoutExpired:
            last_error = "Process timed out (15 min)"
            log(f"Hook 2 timed out for {manager_name} (attempt {attempt})")
        except requests.exceptions.HTTPError as e:
            last_error = f"Apify HTTP error: {e}"
            log(f"Apify error for {manager_name} (attempt {attempt}): {e}")
        except Exception as e:
            last_error = str(e)
            log(f"Hook 2 error for {manager_name} (attempt {attempt}): {e}")

    log(f"Hook 2 FAILED for {manager_name} after {max_retries} attempts")
    return None, last_error


def main():
    parser = argparse.ArgumentParser(description="Batch Hook 2 - Special Transactions")
    parser.add_argument(
        "--managers", default=",".join(FUND_MANAGERS.keys()),
        help=f"Comma-separated managers (default: all {len(FUND_MANAGERS)})",
    )
    parser.add_argument("--email", required=True, help="Comma-separated email addresses")
    parser.add_argument("--output-dir", default="output/batch_hook2", help="Output directory")
    parser.add_argument("--spec-file", type=Path, help="Specification table Excel file")
    parser.add_argument(
        "--skip-tase-prices", action="store_true", default=True,
        help="Skip TASE price checks (default: True)",
    )

    args = parser.parse_args()
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
    log("BATCH HOOK 2 - SPECIAL TRANSACTIONS VALIDATION")
    log("=" * 60)
    log(f"Managers: {len(managers)}")
    log(f"Emails: {', '.join(emails)}")
    log(f"Output: {output_dir}")
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
        xlsx_path, error_msg = run_hook2_for_manager(
            manager, output_dir, funds_list_path, args.spec_file, args.skip_tase_prices,
        )

        if xlsx_path:
            results.append({"manager": manager, "status": "success", "filename": xlsx_path.name})
            subject = f"דוח עסקאות מיוחדות - {manager}"
            if send_hook_email(
                emails, manager, xlsx_path, subject,
                HOOK2_COLOR, HOOK2_COLOR_LIGHT, "דוח עסקאות מיוחדות",
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
        output_dir, "hook2", "Special Transactions Validation",
        managers, results, emails_sent,
    )
    log(f"Summary saved to: {summary_path}")

    failed_managers = [r for r in results if r["status"] == "failed"]
    if failed_managers:
        log("")
        log("Sending failure alert email...")
        send_failure_alert(
            emails, "Hook 2 - Special Transactions",
            failed_managers, successful, len(managers),
        )

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
