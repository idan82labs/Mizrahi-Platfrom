"""
Special Transactions Validation Hook implementation.

This hook validates coordinated/off-exchange trades against
regulatory requirements.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import logging

from mizrahi_hooks.base import BaseHook
from mizrahi_hooks.registry import register_hook
from mizrahi_shared.models import CheckResult, HookConfig
from mizrahi_shared.apify import ApifyClient
from mizrahi_shared.excel import ExcelGenerator, generate_report
from mizrahi_shared.config import get_manager_by_name_he

from .checks import (
    check_duplicates,
    check_dates,
    check_decision_method,
    check_sampling,
    check_prices,
    check_problematic_securities,
)

logger = logging.getLogger(__name__)


@register_hook("special_transactions")
class SpecialTransactionsHook(BaseHook):
    """
    Hook #2: Special Transactions Validation

    Validates coordinated/off-exchange trades by running 6 validation checks:
    1. Duplicates - Inter-fund transactions (buy/sell pairs)
    2. Dates - Transaction dates within report month
    3. Decision Method - Decision method and דחצ voting rules
    4. Sampling - Random samples for manual verification
    5. Prices - Cross-check with TASE market data
    6. Problematic Securities - Securities on warning/halt/restricted lists
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
            "chk7_problematic",
        ]

    async def validate_input(
        self, input_data: Dict[str, Any]
    ) -> Tuple[bool, Optional[str]]:
        """Validate required input fields."""
        if not input_data.get("manager_name"):
            return False, "manager_name is required"

        if not input_data.get("email"):
            return False, "email is required"

        # Validate manager exists
        manager = get_manager_by_name_he(input_data["manager_name"])
        if not manager:
            return False, f"Unknown manager: {input_data['manager_name']}"

        return True, None

    async def fetch_data(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch transaction data from Apify actors."""
        manager_name = input_data["manager_name"]
        manager = get_manager_by_name_he(manager_name)

        self.logger.info(f"Fetching data for manager: {manager_name}")

        async with ApifyClient() as client:
            # Fetch mutual funds list
            self.logger.debug("Fetching mutual funds list...")
            funds_list_run = await client.run_actor(
                self.get_parameter("funds_list_actor", "K9WppTziYC3n2vxTu"),
                input_data={},
            )

            # Fetch special transactions report
            self.logger.debug("Fetching special transactions report...")
            event_id = self.get_parameter("event_id", 5618)
            transactions_run = await client.run_actor(
                self.get_parameter("reports_actor", "5lhI6O39Qbgv9O0gs"),
                input_data={
                    "itemId": manager.id if manager else input_data.get("manager_id"),
                    "eventId": event_id,
                },
            )

            # Get dataset items
            funds_list = await client.get_dataset_items(
                funds_list_run.get("defaultDatasetId", "")
            )
            transactions = await client.get_dataset_items(
                transactions_run.get("defaultDatasetId", "")
            )

        return {
            "funds_list": funds_list,
            "transactions": transactions,
            "manager_name": manager_name,
            "manager_id": manager.id if manager else input_data.get("manager_id"),
            "report_month": input_data.get("report_month"),
            "parameters": self.config.parameters,
        }

    async def run_checks(self, data: Dict[str, Any]) -> List[CheckResult]:
        """Execute all validation checks."""
        results: List[CheckResult] = []

        check_functions = [
            ("chk1_duplicates", check_duplicates, "עסקאות כפולות"),
            ("chk3_dates", check_dates, "חריגות תאריך"),
            ("chk4_decision", check_decision_method, "שיטת ההחלטה"),
            ("chk5_sampling", check_sampling, "דגימות"),
            ("chk6_prices", check_prices, "בדיקות מחיר"),
            ("chk7_problematic", check_problematic_securities, "ניירות בעייתיים"),
        ]

        for check_id, check_func, check_name_he in check_functions:
            if not self.is_check_enabled(check_id):
                self.logger.info(f"Skipping disabled check: {check_id}")
                results.append(
                    CheckResult(
                        check_id=check_id,
                        check_name=check_id,
                        check_name_he=check_name_he,
                        status="skipped",
                        message="Check disabled in configuration",
                    )
                )
                continue

            # Skip price check if configured
            if check_id == "chk6_prices" and self.get_parameter("skip_tase_prices", True):
                self.logger.info("Skipping TASE price check (configured to skip)")
                results.append(
                    CheckResult(
                        check_id=check_id,
                        check_name=check_id,
                        check_name_he=check_name_he,
                        status="skipped",
                        message="בדיקת מחירי בורסה מושבתת",
                    )
                )
                continue

            self.logger.info(f"Running check: {check_id}")
            try:
                result = await check_func(data)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Check {check_id} failed with error: {e}")
                results.append(
                    CheckResult(
                        check_id=check_id,
                        check_name=check_id,
                        check_name_he=check_name_he,
                        status="fail",
                        message=f"Check error: {str(e)}",
                    )
                )

        return results

    async def generate_report(
        self,
        input_data: Dict[str, Any],
        results: List[CheckResult],
    ) -> Path:
        """Generate Excel report with all findings."""
        manager_name = input_data.get("manager_name", "unknown")

        # Prepare output directory
        output_dir = Path("output") / manager_name
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / f"{manager_name}_special_transactions_report.xlsx"

        # Collect findings by check
        findings_by_check = {
            result.check_id: result.findings
            for result in results
            if result.findings
        }

        # Generate report
        await generate_report(
            output_path=output_file,
            hook_name=self.config.name_he,
            manager_name=manager_name,
            check_results=[
                {
                    "check_id": r.check_id,
                    "check_name_he": r.check_name_he,
                    "status": r.status,
                    "findings_count": r.findings_count,
                    "message": r.message,
                    "duration_ms": r.duration_ms,
                }
                for r in results
            ],
            findings_by_check=findings_by_check,
            include_review_columns=True,
        )

        self.logger.info(f"Report generated: {output_file}")
        return output_file
