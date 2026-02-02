"""
Monthly Report Validation Hook implementation.

This hook validates monthly fund holdings reports against the Magna list
and performs various compliance checks.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import logging

from mizrahi_hooks.base import BaseHook
from mizrahi_hooks.registry import register_hook
from mizrahi_shared.models import CheckResult, HookConfig
from mizrahi_shared.apify import ApifyClient, fetch_funds_list
from mizrahi_shared.excel import ExcelGenerator, generate_report
from mizrahi_shared.config import get_manager_by_name_he

from .checks import (
    check_completeness,
    check_unusual_assets,
    check_new_assets,
    check_quantity_changes,
    check_clause_328,
    check_required_combinations,
    check_price_reasonableness,
)

logger = logging.getLogger(__name__)


@register_hook("monthly_report")
class MonthlyReportHook(BaseHook):
    """
    Hook #1: Monthly Report Validation

    Validates monthly fund holdings reports by running 7 validation checks:
    1. Completeness - Cross-reference Magna vs Manager reports
    2. Unusual Assets - Flag unusual asset types
    3. New Assets - Detect new assets since previous month
    4. Quantity Changes - Identify unusual quantity changes
    5. Clause 328 - Borrowed quantity consistency
    6. Required Combinations - Asset type combination rules
    7. Price Reasonableness - Price ratio validation
    """

    @property
    def hook_id(self) -> str:
        return "monthly_report"

    @property
    def version(self) -> str:
        return "2.0.0"

    @property
    def checks(self) -> List[str]:
        return [
            "completeness",
            "unusual_assets",
            "new_assets",
            "quantity_changes",
            "clause_328",
            "required_combinations",
            "price_reasonableness",
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
        """Fetch fund data from Apify actors."""
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

            # Fetch current month report
            self.logger.debug("Fetching current month report...")
            current_report_run = await client.run_actor(
                self.get_parameter("reports_actor", "5lhI6O39Qbgv9O0gs"),
                input_data={
                    "itemId": manager.id if manager else input_data.get("manager_id"),
                    "reportType": "monthly_holdings",
                    "month": input_data.get("report_month", "current"),
                },
            )

            # Fetch previous month report for comparison
            self.logger.debug("Fetching previous month report...")
            previous_report_run = await client.run_actor(
                self.get_parameter("reports_actor", "5lhI6O39Qbgv9O0gs"),
                input_data={
                    "itemId": manager.id if manager else input_data.get("manager_id"),
                    "reportType": "monthly_holdings",
                    "month": input_data.get("previous_month", "previous"),
                },
            )

            # Get dataset items
            funds_list = await client.get_dataset_items(
                funds_list_run.get("defaultDatasetId", "")
            )
            current_data = await client.get_dataset_items(
                current_report_run.get("defaultDatasetId", "")
            )
            previous_data = await client.get_dataset_items(
                previous_report_run.get("defaultDatasetId", "")
            )

        return {
            "funds_list": funds_list,
            "current_report": current_data,
            "previous_report": previous_data,
            "manager_name": manager_name,
            "manager_id": manager.id if manager else input_data.get("manager_id"),
            "parameters": self.config.parameters,
        }

    async def run_checks(self, data: Dict[str, Any]) -> List[CheckResult]:
        """Execute all validation checks."""
        results: List[CheckResult] = []

        check_functions = [
            ("completeness", check_completeness, "בדיקת שלמות"),
            ("unusual_assets", check_unusual_assets, "סוגי נכסים חריגים"),
            ("new_assets", check_new_assets, "נכסים חדשים"),
            ("quantity_changes", check_quantity_changes, "שינויים בכמות"),
            ("clause_328", check_clause_328, "סעיף 328"),
            ("required_combinations", check_required_combinations, "שילובים נדרשים"),
            ("price_reasonableness", check_price_reasonableness, "סבירות מחירים"),
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

        output_file = output_dir / f"{manager_name}_monthly_report.xlsx"

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
            include_review_columns=self.config.parameters.get(
                "include_review_columns", True
            ),
        )

        self.logger.info(f"Report generated: {output_file}")
        return output_file
