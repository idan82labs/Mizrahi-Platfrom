"""
Email service for sending notifications and reports.

Supports multiple providers:
- resend: Production email via Resend API
- smtp: Gmail SMTP for development
- console: Print to console for testing
"""

import os
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from typing import Any, Dict, List, Optional
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class EmailProvider(ABC):
    """Abstract base class for email providers."""

    @abstractmethod
    async def send(
        self,
        to: List[str],
        subject: str,
        html_body: str,
        attachments: Optional[List[Path]] = None,
    ) -> bool:
        """Send an email."""
        pass


class ResendProvider(EmailProvider):
    """Email provider using Resend API."""

    def __init__(self, api_key: Optional[str] = None, from_email: Optional[str] = None):
        self.api_key = api_key or os.environ.get("RESEND_API_KEY")
        self.from_email = from_email or os.environ.get("EMAIL_FROM", "notifications@82labs.io")

        if not self.api_key:
            raise ValueError("RESEND_API_KEY not set")

    async def send(
        self,
        to: List[str],
        subject: str,
        html_body: str,
        attachments: Optional[List[Path]] = None,
    ) -> bool:
        try:
            import resend
            resend.api_key = self.api_key

            email_params: Dict[str, Any] = {
                "from": self.from_email,
                "to": to,
                "subject": subject,
                "html": html_body,
            }

            if attachments:
                email_params["attachments"] = [
                    {
                        "filename": att.name,
                        "content": att.read_bytes(),
                    }
                    for att in attachments
                    if att.exists()
                ]

            resend.Emails.send(email_params)
            logger.info(f"Email sent via Resend to: {', '.join(to)}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email via Resend: {e}")
            return False


class SMTPProvider(EmailProvider):
    """Email provider using Gmail SMTP."""

    def __init__(
        self,
        smtp_user: Optional[str] = None,
        smtp_password: Optional[str] = None,
        smtp_server: str = "smtp.gmail.com",
        smtp_port: int = 465,
    ):
        self.smtp_user = smtp_user or os.environ.get("GMAIL_USER")
        self.smtp_password = smtp_password or os.environ.get("GMAIL_APP_PASSWORD")
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port

        if not self.smtp_user or not self.smtp_password:
            raise ValueError("GMAIL_USER and GMAIL_APP_PASSWORD must be set")

    async def send(
        self,
        to: List[str],
        subject: str,
        html_body: str,
        attachments: Optional[List[Path]] = None,
    ) -> bool:
        try:
            msg = MIMEMultipart()
            msg["From"] = self.smtp_user
            msg["To"] = ", ".join(to)
            msg["Subject"] = subject

            msg.attach(MIMEText(html_body, "html", "utf-8"))

            if attachments:
                for att_path in attachments:
                    if not att_path.exists():
                        continue

                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(att_path.read_bytes())
                    encoders.encode_base64(part)
                    part.add_header(
                        "Content-Disposition",
                        f"attachment; filename={att_path.name}",
                    )
                    msg.attach(part)

            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.smtp_user, to, msg.as_string())

            logger.info(f"Email sent via SMTP to: {', '.join(to)}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email via SMTP: {e}")
            return False


class ConsoleProvider(EmailProvider):
    """Email provider that prints to console (for testing)."""

    async def send(
        self,
        to: List[str],
        subject: str,
        html_body: str,
        attachments: Optional[List[Path]] = None,
    ) -> bool:
        print("\n" + "=" * 60)
        print("EMAIL (Console Provider)")
        print("=" * 60)
        print(f"To: {', '.join(to)}")
        print(f"Subject: {subject}")
        print("-" * 60)
        print(f"Body:\n{html_body[:500]}..." if len(html_body) > 500 else f"Body:\n{html_body}")
        if attachments:
            print(f"Attachments: {[str(a) for a in attachments]}")
        print("=" * 60 + "\n")

        logger.info(f"Email printed to console for: {', '.join(to)}")
        return True


class EmailService:
    """
    Email service with provider abstraction.

    Usage:
        service = EmailService()  # Auto-selects provider based on environment
        await service.send_report(
            recipients=["user@example.com"],
            subject="Report",
            template="monthly_report",
            context={"manager_name": "מגדל"},
            attachment=Path("report.xlsx"),
        )
    """

    def __init__(self, provider: Optional[str] = None):
        """
        Initialize email service.

        Args:
            provider: Provider name ("resend", "smtp", "console").
                     If not provided, auto-selects based on available credentials.
        """
        self.provider = self._create_provider(provider)

    def _create_provider(self, provider_name: Optional[str]) -> EmailProvider:
        """Create the appropriate email provider."""
        if provider_name is None:
            # Auto-select based on environment
            if os.environ.get("RESEND_API_KEY"):
                provider_name = "resend"
            elif os.environ.get("GMAIL_USER") and os.environ.get("GMAIL_APP_PASSWORD"):
                provider_name = "smtp"
            else:
                provider_name = "console"

        if provider_name == "resend":
            return ResendProvider()
        elif provider_name == "smtp":
            return SMTPProvider()
        elif provider_name == "console":
            return ConsoleProvider()
        else:
            raise ValueError(f"Unknown email provider: {provider_name}")

    async def send(
        self,
        to: List[str],
        subject: str,
        html_body: str,
        attachments: Optional[List[Path]] = None,
    ) -> bool:
        """
        Send an email.

        Args:
            to: List of recipient email addresses.
            subject: Email subject.
            html_body: HTML body content.
            attachments: Optional list of file paths to attach.

        Returns:
            True if email was sent successfully.
        """
        return await self.provider.send(to, subject, html_body, attachments)

    async def send_report(
        self,
        recipients: List[str],
        subject: str,
        template: str,
        context: Dict[str, Any],
        attachment: Optional[Path] = None,
    ) -> bool:
        """
        Send a report email using a template.

        Args:
            recipients: List of recipient email addresses.
            subject: Email subject.
            template: Template name to use.
            context: Context dictionary for template rendering.
            attachment: Optional report file to attach.

        Returns:
            True if email was sent successfully.
        """
        html_body = self._render_template(template, context)
        attachments = [attachment] if attachment else None
        return await self.send(recipients, subject, html_body, attachments)

    def _render_template(self, template: str, context: Dict[str, Any]) -> str:
        """Render an email template with context."""
        # Simple template rendering - can be extended with Jinja2
        templates = {
            "monthly_report": self._monthly_report_template,
            "special_transactions": self._special_transactions_template,
            "error": self._error_template,
        }

        template_func = templates.get(template, self._default_template)
        return template_func(context)

    def _default_template(self, context: Dict[str, Any]) -> str:
        """Default email template."""
        return f"""
        <!DOCTYPE html>
        <html dir="rtl" lang="he">
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; direction: rtl; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #1e40af; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background: #f8fafc; }}
                .footer {{ text-align: center; padding: 10px; color: #64748b; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>מערכת בקרה - מזרחי טפחות</h1>
                </div>
                <div class="content">
                    <p>{context.get('message', 'דוח מצורף')}</p>
                </div>
                <div class="footer">
                    <p>82Labs - Mizrahi Compliance Platform</p>
                </div>
            </div>
        </body>
        </html>
        """

    def _monthly_report_template(self, context: Dict[str, Any]) -> str:
        """Monthly report email template."""
        manager = context.get("manager_name", "")
        timestamp = context.get("timestamp", "")
        checks = context.get("checks", [])

        checks_html = ""
        for check in checks:
            status_color = "#22c55e" if check.get("status") == "pass" else "#ef4444"
            checks_html += f"""
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #e2e8f0;">{check.get('check_name_he', '')}</td>
                <td style="padding: 8px; border-bottom: 1px solid #e2e8f0; color: {status_color};">
                    {check.get('status', '')}
                </td>
                <td style="padding: 8px; border-bottom: 1px solid #e2e8f0;">{check.get('findings_count', 0)}</td>
            </tr>
            """

        return f"""
        <!DOCTYPE html>
        <html dir="rtl" lang="he">
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; direction: rtl; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #1e40af; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background: #f8fafc; }}
                .info-card {{ background: white; padding: 15px; border-radius: 8px; margin: 10px 0; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th {{ background: #e2e8f0; padding: 10px; text-align: right; }}
                .footer {{ text-align: center; padding: 10px; color: #64748b; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>בקרה אוטומטית על דוח חודשי</h1>
                </div>
                <div class="content">
                    <div class="info-card">
                        <strong>מנהל הקרן:</strong> {manager}<br>
                        <strong>תאריך:</strong> {timestamp}
                    </div>

                    <h3>תוצאות הבדיקות:</h3>
                    <table>
                        <tr>
                            <th>בדיקה</th>
                            <th>סטטוס</th>
                            <th>ממצאים</th>
                        </tr>
                        {checks_html}
                    </table>

                    <p style="margin-top: 20px;">הדוח המלא מצורף כקובץ Excel.</p>
                </div>
                <div class="footer">
                    <p>82Labs - Mizrahi Compliance Platform</p>
                </div>
            </div>
        </body>
        </html>
        """

    def _special_transactions_template(self, context: Dict[str, Any]) -> str:
        """Special transactions email template."""
        manager = context.get("manager_name", "")
        timestamp = context.get("timestamp", "")
        samples = context.get("samples", [])

        samples_html = ""
        for sample in samples[:5]:
            samples_html += f"""
            <tr>
                <td style="padding: 8px; border-bottom: 1px solid #e2e8f0;">{sample.get('security_no', '')}</td>
                <td style="padding: 8px; border-bottom: 1px solid #e2e8f0;">{sample.get('security_name', '')}</td>
                <td style="padding: 8px; border-bottom: 1px solid #e2e8f0;">{sample.get('quantity', '')}</td>
                <td style="padding: 8px; border-bottom: 1px solid #e2e8f0;">{sample.get('price', '')}</td>
            </tr>
            """

        return f"""
        <!DOCTYPE html>
        <html dir="rtl" lang="he">
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; direction: rtl; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #1e40af; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background: #f8fafc; }}
                .info-card {{ background: white; padding: 15px; border-radius: 8px; margin: 10px 0; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th {{ background: #e2e8f0; padding: 10px; text-align: right; }}
                .footer {{ text-align: center; padding: 10px; color: #64748b; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>בקרה על עסקאות מיוחדות</h1>
                </div>
                <div class="content">
                    <div class="info-card">
                        <strong>מנהל הקרן:</strong> {manager}<br>
                        <strong>תאריך:</strong> {timestamp}
                    </div>

                    <h3>דגימות לבדיקה ידנית:</h3>
                    <table>
                        <tr>
                            <th>מספר נייר</th>
                            <th>שם נייר</th>
                            <th>כמות</th>
                            <th>מחיר</th>
                        </tr>
                        {samples_html if samples_html else '<tr><td colspan="4">אין דגימות</td></tr>'}
                    </table>

                    <p style="margin-top: 20px;">הדוח המלא מצורף כקובץ Excel.</p>
                </div>
                <div class="footer">
                    <p>82Labs - Mizrahi Compliance Platform</p>
                </div>
            </div>
        </body>
        </html>
        """

    def _error_template(self, context: Dict[str, Any]) -> str:
        """Error notification email template."""
        hook_name = context.get("hook_name", "")
        error = context.get("error", "Unknown error")
        timestamp = context.get("timestamp", "")

        return f"""
        <!DOCTYPE html>
        <html dir="rtl" lang="he">
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; direction: rtl; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #dc2626; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background: #fef2f2; }}
                .error-box {{ background: white; padding: 15px; border-radius: 8px; border-left: 4px solid #dc2626; }}
                .footer {{ text-align: center; padding: 10px; color: #64748b; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>שגיאה בהרצת בקרה</h1>
                </div>
                <div class="content">
                    <p><strong>בקרה:</strong> {hook_name}</p>
                    <p><strong>זמן:</strong> {timestamp}</p>

                    <div class="error-box">
                        <strong>שגיאה:</strong><br>
                        <code>{error}</code>
                    </div>
                </div>
                <div class="footer">
                    <p>82Labs - Mizrahi Compliance Platform</p>
                </div>
            </div>
        </body>
        </html>
        """
