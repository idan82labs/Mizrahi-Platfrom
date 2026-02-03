#!/usr/bin/env python3
"""
Test email sending functionality.

Usage:
    python test_email.py --gmail-user YOUR_EMAIL --gmail-password YOUR_APP_PASSWORD

Or set environment variables:
    export GMAIL_USER=your@gmail.com
    export GMAIL_APP_PASSWORD=your_app_password
    python test_email.py
"""

import os
import sys
import argparse
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Test recipient
TEST_EMAIL = "alexandrf539@gmail.com"


def send_test_email(gmail_user: str, gmail_password: str, recipient: str = TEST_EMAIL):
    """Send a simple test email"""

    print(f"Sending test email...")
    print(f"  From: {gmail_user}")
    print(f"  To: {recipient}")

    # Create message
    msg = MIMEMultipart()
    msg["From"] = gmail_user
    msg["To"] = recipient
    msg["Subject"] = f"Mizrahi Test Email - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    body = f"""
This is a test email from the Mizrahi Compliance Platform.

Timestamp: {datetime.now().isoformat()}
Sender: {gmail_user}
Recipient: {recipient}

If you received this email, your email configuration is working correctly.

---
Mizrahi Compliance Platform
Digital Ocean Hosting
"""

    msg.attach(MIMEText(body, "plain", "utf-8"))

    try:
        print(f"  Connecting to smtp.gmail.com:465...")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            print(f"  Logging in as {gmail_user}...")
            server.login(gmail_user, gmail_password)
            print(f"  Sending message...")
            server.send_message(msg)

        print(f"\n✅ SUCCESS! Test email sent to {recipient}")
        print(f"   Check your inbox (and spam folder)")
        return True

    except smtplib.SMTPAuthenticationError as e:
        print(f"\n❌ AUTHENTICATION ERROR!")
        print(f"   The Gmail credentials are invalid.")
        print(f"   Make sure you're using an App Password (not your regular password)")
        print(f"   Get one at: https://myaccount.google.com/apppasswords")
        print(f"   Error: {e}")
        return False

    except Exception as e:
        print(f"\n❌ ERROR sending email: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Test email sending")
    parser.add_argument("--gmail-user", help="Gmail address")
    parser.add_argument("--gmail-password", help="Gmail App Password")
    parser.add_argument(
        "--recipient", default=TEST_EMAIL, help=f"Recipient email (default: {TEST_EMAIL})"
    )

    args = parser.parse_args()

    # Get credentials from args or environment
    gmail_user = args.gmail_user or os.environ.get("GMAIL_USER")
    gmail_password = args.gmail_password or os.environ.get("GMAIL_APP_PASSWORD")

    if not gmail_user or not gmail_password:
        print("ERROR: Gmail credentials not provided")
        print()
        print("Either provide via command line:")
        print("  python test_email.py --gmail-user YOUR_EMAIL --gmail-password YOUR_APP_PASSWORD")
        print()
        print("Or set environment variables:")
        print("  export GMAIL_USER=your@gmail.com")
        print("  export GMAIL_APP_PASSWORD=your_app_password")
        print()
        print("To get an App Password:")
        print("  1. Go to https://myaccount.google.com/apppasswords")
        print("  2. Enable 2FA if not already enabled")
        print("  3. Generate an App Password for 'Mail'")
        sys.exit(1)

    success = send_test_email(gmail_user, gmail_password, args.recipient)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
