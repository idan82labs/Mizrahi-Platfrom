# Hook Plugin System

This document describes the hook plugin architecture, including the BaseHook
abstract class, hook registry, and example implementations.

**Related Documents:**

- [System Design](./SYSTEM_DESIGN.md) - Overall architecture
- [Configuration](./CONFIGURATION.md) - Hook configuration format
- [Hooks Development Guide](../guides/HOOKS_DEVELOPMENT.md) - Creating new hooks

---

## Table of Contents

1. [Overview](#overview)
2. [BaseHook Abstract Class](#basehook-abstract-class)
3. [Hook Registry](#hook-registry)
4. [Example Hook Implementation](#example-hook-implementation)

---

## Overview

Hooks are self-contained validation modules that follow the Template Method
pattern:

1. **validate_input()** - Validate request parameters
2. **fetch_data()** - Call Apify/APIs for data
3. **run_checks()** - Execute validation checks
4. **generate_report()** - Create Excel output
5. **send_email()** - Notify recipients

The `execute()` method in `BaseHook` orchestrates this flow automatically.

---

## BaseHook Abstract Class

```python
# packages/hooks/src/mizrahi_hooks/base.py

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, List, Optional, Dict
from pathlib import Path
from datetime import datetime
import time
import logging

@dataclass
class HookConfig:
    """Configuration loaded from hooks.yaml"""
    id: str
    name: str
    name_he: str
    description: str
    status: str  # "active" | "development" | "specification"
    schedule_enabled: bool
    schedule_cron: Optional[str]
    schedule_timezone: str
    parameters: Dict[str, Any]
    checks: List[Dict[str, Any]]
    email_enabled: bool
    email_template: str
    email_cc: List[str] = field(default_factory=list)

@dataclass
class CheckResult:
    """Result of a single validation check"""
    check_id: str
    check_name: str
    check_name_he: str
    status: str  # "pass" | "fail" | "warning" | "skipped"
    message: str
    findings_count: int
    findings: List[Dict[str, Any]]
    duration_ms: int

@dataclass
class HookResult:
    """Result of complete hook execution"""
    hook_id: str
    manager_name: str
    manager_id: str
    status: str  # "success" | "partial" | "failed"
    message: str
    checks: List[CheckResult]
    output_file: Optional[Path]
    email_sent: bool
    email_recipients: List[str]
    started_at: datetime
    completed_at: datetime
    duration_seconds: float
    error: Optional[str] = None

class BaseHook(ABC):
    """
    Abstract base class for all validation hooks.

    To create a new hook:
    1. Create a new directory under packages/hooks/src/mizrahi_hooks/
    2. Implement a class that extends BaseHook
    3. Register the hook in registry.py
    4. Add configuration to config/hooks.yaml
    """

    def __init__(self, config: HookConfig):
        self.config = config
        self.logger = logging.getLogger(f"hook.{self.hook_id}")

    @property
    @abstractmethod
    def hook_id(self) -> str:
        """Unique identifier for the hook (e.g., 'monthly_report')"""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Hook version (e.g., '1.0.0')"""
        pass

    @property
    @abstractmethod
    def checks(self) -> List[str]:
        """List of check IDs this hook performs"""
        pass

    @abstractmethod
    async def validate_input(self, input_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        Validate input before processing.

        Args:
            input_data: Dictionary with manager_name, email, etc.

        Returns:
            Tuple of (is_valid, error_message)
        """
        pass

    @abstractmethod
    async def fetch_data(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fetch required data from external sources.

        Args:
            input_data: Validated input data

        Returns:
            Dictionary with fetched data (dataframes, files, etc.)
        """
        pass

    @abstractmethod
    async def run_checks(self, data: Dict[str, Any]) -> List[CheckResult]:
        """
        Execute all validation checks.

        Args:
            data: Data returned from fetch_data()

        Returns:
            List of CheckResult objects
        """
        pass

    @abstractmethod
    async def generate_report(
        self,
        input_data: Dict[str, Any],
        results: List[CheckResult]
    ) -> Path:
        """
        Generate Excel report with findings.

        Args:
            input_data: Original input data
            results: List of check results

        Returns:
            Path to generated Excel file
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
        """
        started_at = datetime.utcnow()
        start_time = time.time()

        manager_name = input_data.get("manager_name", "Unknown")
        manager_id = input_data.get("manager_id", "")

        try:
            # Step 1: Validate input
            self.logger.info(f"Validating input for {manager_name}")
            is_valid, error = await self.validate_input(input_data)
            if not is_valid:
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
                    error=error
                )

            # Step 2: Fetch data
            self.logger.info(f"Fetching data for {manager_name}")
            data = await self.fetch_data(input_data)

            # Step 3: Run checks
            self.logger.info(f"Running {len(self.checks)} checks for {manager_name}")
            check_results = await self.run_checks(data)

            # Step 4: Generate report
            self.logger.info(f"Generating report for {manager_name}")
            output_file = await self.generate_report(input_data, check_results)

            # Step 5: Send email
            email_sent = False
            email_recipients = []
            if self.config.email_enabled:
                self.logger.info(f"Sending email for {manager_name}")
                email_sent, email_recipients = await self._send_email(
                    input_data, check_results, output_file
                )

            # Determine overall status
            failed_checks = [c for c in check_results if c.status == "fail"]
            warning_checks = [c for c in check_results if c.status == "warning"]

            if failed_checks:
                status = "partial"
                message = f"{len(failed_checks)} checks failed"
            elif warning_checks:
                status = "success"
                message = f"Completed with {len(warning_checks)} warnings"
            else:
                status = "success"
                message = "All checks passed"

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
                duration_seconds=time.time() - start_time
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
                error=str(e)
            )

    async def _send_email(
        self,
        input_data: Dict[str, Any],
        results: List[CheckResult],
        output_file: Path
    ) -> tuple[bool, List[str]]:
        """Send email notification with report attachment."""
        from mizrahi_shared.email import EmailService

        email_service = EmailService()
        recipients = self._parse_recipients(input_data.get("email", ""))
        recipients.extend(self.config.email_cc)

        success = await email_service.send_report(
            template=self.config.email_template,
            recipients=recipients,
            subject=self._build_email_subject(input_data),
            context={
                "manager_name": input_data.get("manager_name"),
                "hook_name": self.config.name_he,
                "results": results,
                "timestamp": datetime.now().isoformat()
            },
            attachment=output_file
        )

        return success, recipients if success else []

    def _parse_recipients(self, email_str: str) -> List[str]:
        """Parse semicolon or comma separated email string."""
        if not email_str:
            return []
        separators = [";", ","]
        for sep in separators:
            if sep in email_str:
                return [e.strip() for e in email_str.split(sep) if e.strip()]
        return [email_str.strip()] if email_str.strip() else []

    def _build_email_subject(self, input_data: Dict[str, Any]) -> str:
        """Build email subject line."""
        manager = input_data.get("manager_name", "")
        return f"{self.config.name_he} - {manager}"
```

---

## Hook Registry

```python
# packages/hooks/src/mizrahi_hooks/registry.py

from typing import Dict, Type, Optional
from .base import BaseHook, HookConfig

# Registry of all available hooks
_HOOK_REGISTRY: Dict[str, Type[BaseHook]] = {}

def register_hook(hook_id: str):
    """Decorator to register a hook class."""
    def decorator(cls: Type[BaseHook]):
        _HOOK_REGISTRY[hook_id] = cls
        return cls
    return decorator

def get_hook(hook_id: str, config: HookConfig) -> Optional[BaseHook]:
    """Get an instance of a hook by ID."""
    hook_class = _HOOK_REGISTRY.get(hook_id)
    if hook_class is None:
        return None
    return hook_class(config)

def list_hooks() -> list[str]:
    """List all registered hook IDs."""
    return list(_HOOK_REGISTRY.keys())

# Auto-import all hooks to trigger registration
from .monthly_report import MonthlyReportHook
from .special_transactions import SpecialTransactionsHook
```

---

## Example Hook Implementation

```python
# packages/hooks/src/mizrahi_hooks/special_transactions/hook.py

from typing import Any, Dict, List, Optional
from pathlib import Path

from mizrahi_hooks.base import BaseHook, HookConfig, CheckResult
from mizrahi_hooks.registry import register_hook
from mizrahi_shared.apify import ApifyClient
from mizrahi_shared.excel import ExcelGenerator

from .checks import (
    check_duplicates,
    check_dates,
    check_decision_method,
    check_sampling,
    check_prices,
    check_problematic_securities
)

@register_hook("special_transactions")
class SpecialTransactionsHook(BaseHook):
    """
    Hook #2: Special Transactions Validation

    Validates coordinated/off-exchange trades including:
    - Inter-fund transactions (duplicates)
    - Date validation
    - Decision method compliance
    - Price verification with TASE
    - Problematic securities flagging
    """

    @property
    def hook_id(self) -> str:
        return "special_transactions"

    @property
    def version(self) -> str:
        return "2.0.0"

    @property
    def checks(self) -> List[str]:
        return [
            "chk1_duplicates",
            "chk3_dates",
            "chk4_decision",
            "chk5_sampling",
            "chk6_prices",
            "chk7_problematic"
        ]

    async def validate_input(self, input_data: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Validate required input fields."""
        if not input_data.get("manager_name"):
            return False, "manager_name is required"
        if not input_data.get("email"):
            return False, "email is required"
        return True, None

    async def fetch_data(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch data from Apify actors."""
        apify = ApifyClient()

        # Fetch mutual funds list
        funds_list = await apify.run_actor(
            actor_id=self.config.parameters.get("funds_list_actor"),
            input_data={}
        )

        # Fetch special transactions report
        manager_id = input_data.get("manager_id")
        transactions = await apify.run_actor(
            actor_id=self.config.parameters.get("reports_actor"),
            input_data={"manager_id": manager_id, "event_id": 5618}
        )

        return {
            "funds_list": funds_list,
            "transactions": transactions,
            "manager_name": input_data.get("manager_name"),
            "report_month": input_data.get("report_month")
        }

    async def run_checks(self, data: Dict[str, Any]) -> List[CheckResult]:
        """Execute all validation checks."""
        results = []

        # CHK_1: Duplicates
        results.append(await check_duplicates(
            data["transactions"],
            data["funds_list"]
        ))

        # CHK_3: Date validation
        results.append(await check_dates(
            data["transactions"],
            data["report_month"]
        ))

        # CHK_4: Decision method
        results.append(await check_decision_method(
            data["transactions"],
            self.config.parameters
        ))

        # CHK_5: Sampling
        results.append(await check_sampling(
            data["transactions"],
            sample_size=self.config.parameters.get("sample_size", 5)
        ))

        # CHK_6: Price checks
        if not self.config.parameters.get("skip_tase_prices", True):
            results.append(await check_prices(
                data["transactions"],
                threshold=self.config.parameters.get("price_variance_threshold", 5.0)
            ))

        # CHK_7: Problematic securities
        results.append(await check_problematic_securities(
            data["transactions"]
        ))

        return results

    async def generate_report(
        self,
        input_data: Dict[str, Any],
        results: List[CheckResult]
    ) -> Path:
        """Generate multi-sheet Excel report."""
        generator = ExcelGenerator()

        output_dir = Path("output") / input_data.get("manager_name", "unknown")
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / f"special_transactions_report.xlsx"

        await generator.create_report(
            output_path=output_file,
            sheets=[
                ("סיכום", self._build_summary_sheet(results)),
                ("סטטוס בדיקות", self._build_status_sheet(results)),
                *[(r.check_name_he, r.findings) for r in results if r.findings]
            ]
        )

        return output_file
```

---

**Next:** [Configuration](./CONFIGURATION.md)
