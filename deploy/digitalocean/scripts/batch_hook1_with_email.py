#!/usr/bin/env python3
"""
Batch Hook 1 - Monthly Report Validation
Runs Hook 1 for all fund managers and sends individual branded emails.

Usage:
    python batch_hook1_with_email.py --email "idan.t@82labs.io,elay.g@82labs.io"
    python batch_hook1_with_email.py --managers "סיגמא,מגדל" --email "test@test.com"
"""

import re
import sys
import argparse
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

from hook_utils import (
    FUND_MANAGERS, SCRIPTS_DIR, log, extract_error,
    send_hook_email, send_failure_alert, save_batch_summary,
)

HOOK1_SCRIPT = SCRIPTS_DIR / "fund_automation_complete.py"
HOOK1_COLOR = "#4a9d7c"
HOOK1_COLOR_LIGHT = "#e3f1f4"


def _extract_month_from_filename(filename: str) -> str:
    """Extract 'נובמבר 2025' from 'דוח_מגדל_דוח_חודשי-נובמבר_2025.xlsx'."""
    match = re.search(r'חודשי-(\S+)_(\d{4})', filename)
    if match:
        return f"{match.group(1)} {match.group(2)}"
    return ""


def run_hook1_for_manager(
    manager_name: str,
    output_dir: Path,
    max_retries: int = 3,
    retry_delay: int = 30,
) -> Tuple[Optional[Path], str]:
    """Run Hook 1 for a single manager with retry logic."""
    manager_dir = output_dir / manager_name
    manager_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        sys.executable, str(HOOK1_SCRIPT),
        "--fund-name", manager_name,
        "--output-dir", str(manager_dir),
    ]

    last_error = ""
    for attempt in range(1, max_retries + 1):
        if attempt > 1:
            log(f"Retry {attempt}/{max_retries} for {manager_name} (waiting {retry_delay}s)...")
            time.sleep(retry_delay)
        else:
            log(f"Running Hook 1 for {manager_name}...")

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True,
                timeout=900, cwd=str(SCRIPTS_DIR),
            )

            if result.returncode != 0:
                last_error = extract_error(result.stderr)
                log(f"Hook 1 failed for {manager_name} (attempt {attempt}): {last_error}")
                continue

            for f in manager_dir.glob("דוח_*.xlsx"):
                log(f"Hook 1 completed: {f.name}")
                return f, ""

            last_error = "No output file generated"
            log(f"No output file found for {manager_name} (attempt {attempt})")

        except subprocess.TimeoutExpired:
            last_error = "Process timed out (15 min)"
            log(f"Hook 1 timed out for {manager_name} (attempt {attempt})")
        except Exception as e:
            last_error = str(e)
            log(f"Hook 1 error for {manager_name} (attempt {attempt}): {e}")

    log(f"Hook 1 FAILED for {manager_name} after {max_retries} attempts")
    return None, last_error


def main():
    parser = argparse.ArgumentParser(description="Batch Hook 1 - Monthly Report")
    parser.add_argument(
        "--managers", default=",".join(FUND_MANAGERS.keys()),
        help=f"Comma-separated managers (default: all {len(FUND_MANAGERS)})",
    )
    parser.add_argument("--email", required=True, help="Comma-separated email addresses")
    parser.add_argument("--output-dir", default="output/batch_hook1", help="Output directory")

    args = parser.parse_args()
    managers = [m.strip() for m in args.managers.split(",") if m.strip()]
    emails = [e.strip() for e in args.email.split(",") if e.strip()]

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = (SCRIPTS_DIR / args.output_dir / timestamp).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    log("=" * 60)
    log("BATCH HOOK 1 - MONTHLY REPORT VALIDATION")
    log("=" * 60)
    log(f"Managers: {len(managers)}")
    log(f"Emails: {', '.join(emails)}")
    log(f"Output: {output_dir}")
    log("=" * 60)

    results = []
    emails_sent = 0

    for manager in managers:
        log("")
        xlsx_path, error_msg = run_hook1_for_manager(manager, output_dir)

        if xlsx_path:
            month_str = _extract_month_from_filename(xlsx_path.name)
            results.append({"manager": manager, "status": "success", "filename": xlsx_path.name})
            subject = f"דוח בקרת איכות נתונים - {manager} - {month_str}" if month_str else f"דוח בקרת איכות נתונים - {manager}"
            title = f"דוח בקרת איכות נתונים - {month_str}" if month_str else "דוח בקרת איכות נתונים"
            if send_hook_email(
                emails, manager, xlsx_path, subject,
                HOOK1_COLOR, HOOK1_COLOR_LIGHT, title,
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
        output_dir, "hook1", "Monthly Report Validation", managers, results, emails_sent,
    )
    log(f"Summary saved to: {summary_path}")

    failed_managers = [r for r in results if r["status"] == "failed"]
    if failed_managers:
        log("")
        log("Sending failure alert email...")
        send_failure_alert(
            emails, "Hook 1 - Monthly Report", failed_managers, successful, len(managers),
        )

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
