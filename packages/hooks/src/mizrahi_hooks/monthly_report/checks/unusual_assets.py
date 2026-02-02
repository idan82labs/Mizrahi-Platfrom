"""
Check #2: Unusual Asset Types (סוגי נכסים חריגים)

Flag assets with unusual type codes that have value > 0.
"""

import time
import logging
from typing import Any, Dict, List

from mizrahi_shared.models import CheckResult
from mizrahi_shared.constants import UNUSUAL_ASSET_TYPES

logger = logging.getLogger(__name__)

CHECK_ID = "unusual_assets"
CHECK_NAME_HE = "סוגי נכסים חריגים"


async def check_unusual_assets(data: Dict[str, Any]) -> CheckResult:
    """
    Check for unusual asset types with positive values.

    Args:
        data: Dictionary containing:
            - current_report: Current month's report data
            - parameters: Hook parameters including unusual_asset_types list

    Returns:
        CheckResult with unusual assets as findings
    """
    start_time = time.time()
    findings: List[Dict[str, Any]] = []

    try:
        current_report = data.get("current_report", [])
        parameters = data.get("parameters", {})

        # Get unusual asset types from parameters or use defaults
        unusual_types = set(
            parameters.get("unusual_asset_types", UNUSUAL_ASSET_TYPES)
        )

        for row in current_report:
            asset_type = row.get("asset_type") or row.get("סוג נכס")
            value = row.get("value") or row.get("שווי") or 0

            try:
                asset_type = int(asset_type) if asset_type else None
                value = float(value) if value else 0
            except (ValueError, TypeError):
                continue

            if asset_type in unusual_types and value > 0:
                findings.append({
                    "מספר קרן": row.get("fund_id") or row.get("מספר קרן", ""),
                    "שם קרן": row.get("fund_name") or row.get("שם קרן", ""),
                    "סוג נכס": asset_type,
                    "שם נכס": row.get("asset_name") or row.get("שם נכס", ""),
                    "שווי": value,
                })

        # Determine status
        if findings:
            status = "warning"
            message = f"נמצאו {len(findings)} נכסים מסוגים חריגים"
        else:
            status = "pass"
            message = "לא נמצאו נכסים מסוגים חריגים"

        logger.info(f"Unusual assets check: {len(findings)} unusual assets found")

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
        logger.exception(f"Unusual assets check error: {e}")
        return CheckResult(
            check_id=CHECK_ID,
            check_name=CHECK_ID,
            check_name_he=CHECK_NAME_HE,
            status="fail",
            message=f"שגיאה בבדיקה: {str(e)}",
            duration_ms=int((time.time() - start_time) * 1000),
        )
