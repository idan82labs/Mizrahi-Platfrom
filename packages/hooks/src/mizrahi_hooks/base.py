"""
Base hook class and related models.

All validation hooks must extend BaseHook and implement its abstract methods.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import time
import logging

from mizrahi_shared.models import CheckResult, HookResult, HookConfig
from mizrahi_shared.email import EmailService
from mizrahi_shared.logging import LogContext, log_check_start, log_check_end


# Re-export for convenience
__all__ = ["BaseHook", "HookConfig", "CheckResult", "HookResult"]


class BaseHook(ABC):
    """
    Abstract base class for all validation hooks.

    To create a new hook:
    1. Create a new directory under packages/hooks/src/mizrahi_hooks/
    2. Implement a class that extends BaseHook
    3. Register the hook using @register_hook decorator
    4. Add configuration to config/hooks.yaml

    Example:
        @register_hook("my_hook")
        class MyHook(BaseHook):
            @property
            def hook_id(self) -> str:
                return "my_hook"

            @property
            def version(self) -> str:
                return "1.0.0"

            @property
            def checks(self) -> List[str]:
                return ["check_1", "check_2"]

            async def validate_input(self, input_data):
                # Validate input
                return True, None

            async def fetch_data(self, input_data):
                # Fetch required data
                return {}

            async def run_checks(self, data):
                # Run validation checks
                return []

            async def generate_report(self, input_data, results):
                # Generate Excel report
                return Path("report.xlsx")
    """

    def __init__(self, config: HookConfig):
        """
        Initialize the hook with configuration.

        Args:
            config: Hook configuration loaded from hooks.yaml
        """
        self.config = config
        self.logger = logging.getLogger(f"hook.{self.hook_id}")

    @property
    @abstractmethod
    def hook_id(self) -> str:
        """
        Unique identifier for the hook.

        This should match the key in hooks.yaml.
        """
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """
        Hook version string (e.g., "1.0.0").

        Increment when making changes to hook logic.
        """
        pass

    @property
    @abstractmethod
    def checks(self) -> List[str]:
        """
        List of check IDs this hook performs.

        These should match the check IDs in hooks.yaml.
        """
        pass

    @abstractmethod
    async def validate_input(
        self, input_data: Dict[str, Any]
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate input data before processing.

        Args:
            input_data: Dictionary containing:
                - manager_name: Hebrew name of fund manager
                - manager_id: Manager item ID
                - email: Recipient email(s)
                - Additional hook-specific fields

        Returns:
            Tuple of (is_valid, error_message)
            If valid, error_message is None.
        """
        pass

    @abstractmethod
    async def fetch_data(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fetch required data from external sources.

        This typically involves:
        - Calling Apify actors to scrape TASE Maya
        - Loading uploaded files
        - Fetching from other APIs

        Args:
            input_data: Validated input data

        Returns:
            Dictionary with fetched data to be used by checks.
        """
        pass

    @abstractmethod
    async def run_checks(self, data: Dict[str, Any]) -> List[CheckResult]:
        """
        Execute all validation checks.

        Args:
            data: Data returned from fetch_data()

        Returns:
            List of CheckResult objects for each check.
        """
        pass

    @abstractmethod
    async def generate_report(
        self,
        input_data: Dict[str, Any],
        results: List[CheckResult],
    ) -> Path:
        """
        Generate Excel report with findings.

        Args:
            input_data: Original input data
            results: List of check results

        Returns:
            Path to the generated Excel file.
        """
        pass

    async def execute(self, input_data: Dict[str, Any]) -> HookResult:
        """
        Main execution flow - template method pattern.

        This method orchestrates the entire hook execution:
        1. Validate input
        2. Fetch data
        3. Run checks
        4. Generate report
        5. Send email

        Subclasses should NOT override this method.

        Args:
            input_data: Input data for hook execution

        Returns:
            HookResult with execution outcome
        """
        started_at = datetime.utcnow()
        start_time = time.time()

        manager_name = input_data.get("manager_name", "Unknown")
        manager_id = input_data.get("manager_id", "")

        with LogContext(hook_id=self.hook_id, manager_name=manager_name):
            self.logger.info(f"Starting hook execution for {manager_name}")

            try:
                # Step 1: Validate input
                self.logger.debug("Validating input...")
                is_valid, error = await self.validate_input(input_data)
                if not is_valid:
                    self.logger.error(f"Input validation failed: {error}")
                    return HookResult(
                        hook_id=self.hook_id,
                        manager_name=manager_name,
                        manager_id=manager_id,
                        status="failed",
                        message=f"Validation failed: {error}",
                        checks=[],
                        output_file=None,
                        email_sent=False,
                        email_recipients=[],
                        started_at=started_at,
                        completed_at=datetime.utcnow(),
                        duration_seconds=time.time() - start_time,
                        error=error,
                    )

                # Step 2: Fetch data
                self.logger.info("Fetching data...")
                data = await self.fetch_data(input_data)

                # Step 3: Run checks
                self.logger.info(f"Running {len(self.checks)} checks...")
                check_results = await self.run_checks(data)

                # Step 4: Generate report
                self.logger.info("Generating report...")
                output_file = await self.generate_report(input_data, check_results)

                # Step 5: Send email
                email_sent = False
                email_recipients: List[str] = []

                if self.config.email_enabled:
                    self.logger.info("Sending email...")
                    email_sent, email_recipients = await self._send_email(
                        input_data, check_results, output_file
                    )

                # Determine overall status
                failed_checks = [c for c in check_results if c.status == "fail"]
                warning_checks = [c for c in check_results if c.status == "warning"]

                if failed_checks:
                    status = "partial"
                    message = f"{len(failed_checks)} check(s) failed"
                elif warning_checks:
                    status = "success"
                    message = f"Completed with {len(warning_checks)} warning(s)"
                else:
                    status = "success"
                    message = "All checks passed"

                self.logger.info(f"Hook execution completed: {status}")

                return HookResult(
                    hook_id=self.hook_id,
                    manager_name=manager_name,
                    manager_id=manager_id,
                    status=status,
                    message=message,
                    checks=check_results,
                    output_file=output_file,
                    email_sent=email_sent,
                    email_recipients=email_recipients,
                    started_at=started_at,
                    completed_at=datetime.utcnow(),
                    duration_seconds=time.time() - start_time,
                )

            except Exception as e:
                self.logger.exception(f"Hook execution failed: {e}")
                return HookResult(
                    hook_id=self.hook_id,
                    manager_name=manager_name,
                    manager_id=manager_id,
                    status="failed",
                    message=str(e),
                    checks=[],
                    output_file=None,
                    email_sent=False,
                    email_recipients=[],
                    started_at=started_at,
                    completed_at=datetime.utcnow(),
                    duration_seconds=time.time() - start_time,
                    error=str(e),
                )

    async def _send_email(
        self,
        input_data: Dict[str, Any],
        results: List[CheckResult],
        output_file: Path,
    ) -> Tuple[bool, List[str]]:
        """
        Send email notification with report attachment.

        Args:
            input_data: Original input data
            results: Check results
            output_file: Path to report file

        Returns:
            Tuple of (success, recipients_list)
        """
        try:
            email_service = EmailService()
            recipients = self._parse_recipients(input_data.get("email", ""))
            recipients.extend(self.config.email_cc)

            # Remove duplicates while preserving order
            recipients = list(dict.fromkeys(recipients))

            if not recipients:
                self.logger.warning("No email recipients specified")
                return False, []

            success = await email_service.send_report(
                recipients=recipients,
                subject=self._build_email_subject(input_data),
                template=self.config.email_template,
                context={
                    "manager_name": input_data.get("manager_name"),
                    "hook_name": self.config.name_he,
                    "checks": [
                        {
                            "check_name_he": c.check_name_he,
                            "status": c.status,
                            "findings_count": c.findings_count,
                        }
                        for c in results
                    ],
                    "timestamp": datetime.now().isoformat(),
                },
                attachment=output_file,
            )

            return success, recipients if success else []

        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")
            return False, []

    def _parse_recipients(self, email_str: str) -> List[str]:
        """Parse semicolon or comma separated email string."""
        if not email_str:
            return []

        # Try different separators
        for sep in [";", ","]:
            if sep in email_str:
                return [e.strip() for e in email_str.split(sep) if e.strip()]

        # Single email
        return [email_str.strip()] if email_str.strip() else []

    def _build_email_subject(self, input_data: Dict[str, Any]) -> str:
        """Build email subject line."""
        manager = input_data.get("manager_name", "")
        return f"{self.config.name_he} - {manager}"

    def get_check_config(self, check_id: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific check."""
        for check in self.config.checks:
            if check.id == check_id:
                return {
                    "id": check.id,
                    "name_he": check.name_he,
                    "description": check.description,
                    "enabled": check.enabled,
                }
        return None

    def is_check_enabled(self, check_id: str) -> bool:
        """Check if a specific check is enabled."""
        config = self.get_check_config(check_id)
        return config is not None and config.get("enabled", True)

    def get_parameter(self, key: str, default: Any = None) -> Any:
        """Get a parameter value from hook configuration."""
        return self.config.parameters.get(key, default)
