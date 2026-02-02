"""
Check #6: Required Combinations (שילובים נדרשים)

Verify required asset type combinations per Clause 214.
"""

import time
import logging
from typing import Any, Dict, List, Set

from mizrahi_shared.models import CheckResult
from mizrahi_shared.constants import REQUIRED_COMBINATIONS

logger = logging.getLogger(__name__)

CHECK_ID = "required_combinations"
CHECK_NAME_HE = "שילובים נדרשים"


async def check_required_combinations(data: Dict[str, Any]) -> CheckResult:
    """
    Verify required asset type combinations exist.

    When certain asset types are present (with value >= threshold),
    other asset types must also be present.

    Args:
        data: Dictionary containing:
            - current_report: Current month's report data
            - parameters: Hook parameters

    Returns:
        CheckResult with missing combinations as findings
    """
    start_time = time.time()
    findings: List[Dict[str, Any]] = []

    try:
        current_report = data.get("current_report", [])
        parameters = data.get("parameters", {})

        # Get configuration
        required_combos = parameters.get("required_combinations", REQUIRED_COMBINATIONS)
        threshold = parameters.get("combination_threshold_ils", 100000)

        # Group assets by fund
        fund_assets: Dict[str, Dict[int, float]] = {}

        for row in current_report:
            fund_id = str(row.get("fund_id") or row.get("מספר קרן", ""))
            asset_type = row.get("asset_type") or row.get("סוג נכס")
            value = row.get("value") or row.get("שווי", 0)

            if not fund_id:
                continue

            try:
                asset_type = int(asset_type) if asset_type else None
                value = float(value) if value else 0
            except (ValueError, TypeError):
                continue

            if asset_type and value > 0:
                if fund_id not in fund_assets:
                    fund_assets[fund_id] = {}
                fund_assets[fund_id][asset_type] = fund_assets[fund_id].get(asset_type, 0) + value

        # Check each fund for required combinations
        for fund_id, assets in fund_assets.items():
            for required_type, triggering_types in required_combos.items():
                required_type = int(required_type)

                # Check if any triggering type exists with value >= threshold
                has_trigger = any(
                    assets.get(int(t), 0) >= threshold
                    for t in triggering_types
                )

                # If trigger exists but required type is missing
                if has_trigger and required_type not in assets:
                    # Find which triggers are present
                    present_triggers = [
                        t for t in triggering_types
                        if assets.get(int(t), 0) >= threshold
                    ]

                    findings.append({
                        "מספר קרן": fund_id,
                        "סוג נדרש": required_type,
                        "סוגים מפעילים": ", ".join(str(t) for t in present_triggers),
                        "ערך מפעיל": sum(assets.get(int(t), 0) for t in present_triggers),
                        "סיבה": f"סוג {required_type} חסר למרות נוכחות סוגים מפעילים",
                    })

        # Determine status
        if findings:
            status = "fail"
            message = f"נמצאו {len(findings)} שילובים חסרים"
        else:
            status = "pass"
            message = "כל השילובים הנדרשים קיימים"

        logger.info(f"Required combinations check: {len(findings)} missing combinations found")

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
        logger.exception(f"Required combinations check error: {e}")
        return CheckResult(
            check_id=CHECK_ID,
            check_name=CHECK_ID,
            check_name_he=CHECK_NAME_HE,
            status="fail",
            message=f"שגיאה בבדיקה: {str(e)}",
            duration_ms=int((time.time() - start_time) * 1000),
        )
