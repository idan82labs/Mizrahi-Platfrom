"""
Check #1: Completeness (בדיקת שלמות)

Cross-reference funds between Magna list and Manager reports to ensure
all expected funds are present in the report.
"""

import time
import logging
from typing import Any, Dict, List

from mizrahi_shared.models import CheckResult

logger = logging.getLogger(__name__)

CHECK_ID = "completeness"
CHECK_NAME_HE = "בדיקת שלמות"


async def check_completeness(data: Dict[str, Any]) -> CheckResult:
    """
    Verify that all funds in the Magna list appear in the manager's report.

    Args:
        data: Dictionary containing:
            - funds_list: List of funds from Magna
            - current_report: Current month's report data
            - manager_name: Manager name

    Returns:
        CheckResult with missing funds as findings
    """
    start_time = time.time()
    findings: List[Dict[str, Any]] = []

    try:
        funds_list = data.get("funds_list", [])
        current_report = data.get("current_report", [])
        manager_name = data.get("manager_name", "")

        if not funds_list:
            return CheckResult(
                check_id=CHECK_ID,
                check_name=CHECK_ID,
                check_name_he=CHECK_NAME_HE,
                status="warning",
                message="No funds list available for comparison",
                duration_ms=int((time.time() - start_time) * 1000),
            )

        # Extract fund IDs from Magna list (filter by manager if possible)
        magna_fund_ids = set()
        for fund in funds_list:
            fund_manager = fund.get("manager_name", "") or fund.get("מנהל", "")
            if manager_name in fund_manager or not manager_name:
                fund_id = fund.get("fund_id") or fund.get("מספר קרן")
                if fund_id:
                    magna_fund_ids.add(str(fund_id))

        # Extract fund IDs from report
        report_fund_ids = set()
        for row in current_report:
            fund_id = row.get("fund_id") or row.get("מספר קרן")
            if fund_id:
                report_fund_ids.add(str(fund_id))

        # Find missing funds
        missing_funds = magna_fund_ids - report_fund_ids

        for fund_id in missing_funds:
            # Find fund details from Magna list
            fund_details = next(
                (f for f in funds_list if str(f.get("fund_id") or f.get("מספר קרן")) == fund_id),
                {}
            )
            findings.append({
                "מספר קרן": fund_id,
                "שם קרן": fund_details.get("fund_name") or fund_details.get("שם קרן", ""),
                "סטטוס": "חסר בדוח",
            })

        # Determine status
        if findings:
            status = "fail"
            message = f"נמצאו {len(findings)} קרנות חסרות בדוח"
        else:
            status = "pass"
            message = "כל הקרנות מופיעות בדוח"

        logger.info(f"Completeness check: {len(magna_fund_ids)} expected, {len(report_fund_ids)} found, {len(findings)} missing")

        return CheckResult(
            check_id=CHECK_ID,
            check_name=CHECK_ID,
            check_name_he=CHECK_NAME_HE,
            status=status,
            message=message,
            findings_count=len(findings),
            findings=findings,
            duration_ms=int((time.time() - start_time) * 1000),
        )

    except Exception as e:
        logger.exception(f"Completeness check error: {e}")
        return CheckResult(
            check_id=CHECK_ID,
            check_name=CHECK_ID,
            check_name_he=CHECK_NAME_HE,
            status="fail",
            message=f"שגיאה בבדיקה: {str(e)}",
            duration_ms=int((time.time() - start_time) * 1000),
        )
