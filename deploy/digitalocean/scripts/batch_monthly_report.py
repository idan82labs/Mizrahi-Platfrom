#!/usr/bin/env python3
"""
Batch Monthly Report Processor
Processes monthly reports for all fund managers and sends results via email.

Usage:
    python batch_monthly_report.py
    python batch_monthly_report.py --managers "מגדל,איילון"
    python batch_monthly_report.py --send-email
"""

import os
import sys
import subprocess
import smtplib
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import argparse

# ============================================================================
# CONFIGURATION
# ============================================================================

# Fund Manager Names
FUND_MANAGERS = [
    "מגדל",
    "איילון",
    "קסם",
    "סיגמא",
    "פורסט",
    "הראל",
    "אנליסט",
    "מיטב",
    "איביאי",
    "אלטשולר-שחם",
]

# Email configuration - TEST EMAIL
EMAIL_RECIPIENT = "alexandrf539@gmail.com"

# ============================================================================
# LOGGING
# ============================================================================


def log(msg, level="INFO"):
    """Log message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {msg}")


def log_error(msg):
    log(msg, "ERROR")


def log_success(msg):
    log(msg, "SUCCESS")


# ============================================================================
# PROCESSING FUNCTIONS
# ============================================================================


def process_manager(manager_name: str, output_dir: Path, keep_temp: bool = False) -> Dict:
    """Process monthly report for a single manager"""
    log(f"\n{'=' * 60}")
    log(f"Processing manager: {manager_name}")
    log(f"{'=' * 60}")

    # Build command
    script_dir = Path(__file__).parent
    cmd = [
        sys.executable,
        str(script_dir / "fund_automation_complete.py"),
        "--fund-name",
        manager_name,
        "--output-dir",
        str(output_dir),
    ]

    if keep_temp:
        cmd.append("--keep-temp")

    log(f"Running: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

        if result.returncode == 0:
            log_success(f"Processing completed for {manager_name}")

            # Find output file
            output_files = list(output_dir.glob(f"דוח_{manager_name}_*.xlsx"))
            if output_files:
                return {
                    "manager_name": manager_name,
                    "status": "success",
                    "output_file": output_files[0],
                    "log_output": result.stdout,
                }
            else:
                return {
                    "manager_name": manager_name,
                    "status": "failed",
                    "error": "Output file not found",
                }
        else:
            log_error(f"Processing failed for {manager_name}")
            log_error(f"stderr: {result.stderr}")
            return {"manager_name": manager_name, "status": "failed", "error": result.stderr}

    except subprocess.TimeoutExpired:
        log_error(f"Processing timeout for {manager_name}")
        return {
            "manager_name": manager_name,
            "status": "failed",
            "error": "Processing timeout (>10 minutes)",
        }
    except Exception as e:
        log_error(f"Processing exception for {manager_name}: {e}")
        return {"manager_name": manager_name, "status": "failed", "error": str(e)}


# ============================================================================
# EMAIL FUNCTIONS
# ============================================================================


def send_email_with_attachments(
    sender_email, sender_password, recipient_email, subject, body, attachments
):
    """Send email with attachments via Gmail SMTP"""
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = recipient_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain", "utf-8"))

    for file_path in attachments:
        if not file_path.exists():
            log(f"Warning: Attachment not found: {file_path}")
            continue

        with open(file_path, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())

        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename= {file_path.name}")
        msg.attach(part)

    log(f"Connecting to Gmail SMTP...")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        log(f"Logging in as {sender_email}...")
        server.login(sender_email, sender_password)
        log(f"Sending email to {recipient_email}...")
        server.send_message(msg)
        log_success(f"Email sent successfully!")


def send_results_email(
    results: List[Dict], recipient: str, output_dir: Path, gmail_user=None, gmail_password=None
):
    """Send consolidated email with all results"""
    log(f"\n{'=' * 60}")
    log(f"Preparing email to {recipient}")
    log(f"{'=' * 60}")

    successful = [r for r in results if r.get("status") == "success"]
    failed = [r for r in results if r.get("status") == "failed"]

    email_body = f"""
Mizrahi Monthly Report - Batch Processing Results
{"=" * 60}

Processing Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Total Managers: {len(results)}
Successful: {len(successful)}
Failed: {len(failed)}

{"=" * 60}
SUCCESSFUL MANAGERS:
"""

    for r in successful:
        email_body += f"\n✓ {r['manager_name']}"
        if r.get("output_file"):
            email_body += f"\n  - Output: {r['output_file'].name}"

    if failed:
        email_body += f"\n\n{'=' * 60}\nFAILED MANAGERS:"
        for r in failed:
            email_body += f"\n✗ {r['manager_name']}: {r.get('error', 'Unknown error')}"

    email_body += f"\n\n{'=' * 60}\nAll output files are attached to this email."

    log("Email body prepared:")
    log(email_body)

    # Save summary
    summary_file = output_dir / "batch_summary.txt"
    summary_file.write_text(email_body, encoding="utf-8")
    log_success(f"Email summary saved to: {summary_file}")

    # Save JSON summary
    json_summary = {
        "processing_date": datetime.now().isoformat(),
        "total_managers": len(results),
        "successful": len(successful),
        "failed": len(failed),
        "results": [
            {k: str(v) if isinstance(v, Path) else v for k, v in r.items()} for r in results
        ],
    }
    json_file = output_dir / "batch_summary.json"
    json_file.write_text(json.dumps(json_summary, ensure_ascii=False, indent=2), encoding="utf-8")

    # Send email if credentials provided
    if gmail_user and gmail_password:
        attachments = [summary_file]

        for r in successful:
            if r.get("output_file") and r["output_file"].exists():
                attachments.append(r["output_file"])

        subject = f"Mizrahi Monthly Report - Batch Results ({datetime.now().strftime('%Y-%m-%d')})"

        try:
            send_email_with_attachments(
                gmail_user, gmail_password, recipient, subject, email_body, attachments
            )
        except Exception as e:
            log_error(f"Failed to send email: {e}")
    else:
        log("\n" + "=" * 60)
        log("NOTE: Email credentials not provided. Skipping email send.")
        log(f"All results have been saved to: {output_dir}")
        log("=" * 60)


# ============================================================================
# MAIN
# ============================================================================


def parse_args():
    parser = argparse.ArgumentParser(
        description="Batch process monthly reports for all fund managers"
    )
    parser.add_argument(
        "--managers",
        help="Comma-separated list of manager names to process (default: all)",
        default=None,
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("./output/hook1"),
        help="Base output directory (default: ./output/hook1)",
    )
    parser.add_argument(
        "--email", default=EMAIL_RECIPIENT, help=f"Email recipient (default: {EMAIL_RECIPIENT})"
    )
    parser.add_argument("--gmail-user", help="Gmail address for sending email")
    parser.add_argument("--gmail-password", help="Gmail App Password")
    parser.add_argument("--send-email", action="store_true", help="Send email after processing")
    parser.add_argument("--keep-temp", action="store_true", help="Keep temporary files")

    return parser.parse_args()


def main():
    args = parse_args()

    # Get Gmail credentials
    gmail_user = args.gmail_user or os.environ.get("GMAIL_USER")
    gmail_password = args.gmail_password or os.environ.get("GMAIL_APP_PASSWORD")

    # Create output directory
    output_dir = args.output_dir / datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir.mkdir(parents=True, exist_ok=True)

    log("=" * 60)
    log("MIZRAHI MONTHLY REPORT - BATCH PROCESSOR")
    log("=" * 60)
    log(f"Output directory: {output_dir}")
    log(f"Email recipient: {args.email}")

    # Determine managers to process
    if args.managers:
        managers_to_process = [m.strip() for m in args.managers.split(",")]
    else:
        managers_to_process = FUND_MANAGERS

    log(f"Managers to process: {len(managers_to_process)}")
    for name in managers_to_process:
        log(f"  - {name}")

    # Process each manager
    results = []
    for manager_name in managers_to_process:
        result = process_manager(manager_name, output_dir, args.keep_temp)
        results.append(result)

    # Send results
    if args.send_email and gmail_user and gmail_password:
        send_results_email(results, args.email, output_dir, gmail_user, gmail_password)
    else:
        send_results_email(results, args.email, output_dir)

    # Final summary
    log(f"\n{'=' * 60}")
    log("BATCH PROCESSING COMPLETE")
    log("=" * 60)
    log(f"Total managers processed: {len(results)}")
    log(f"Successful: {len([r for r in results if r.get('status') == 'success'])}")
    log(f"Failed: {len([r for r in results if r.get('status') == 'failed'])}")
    log(f"Output directory: {output_dir}")
    log("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
