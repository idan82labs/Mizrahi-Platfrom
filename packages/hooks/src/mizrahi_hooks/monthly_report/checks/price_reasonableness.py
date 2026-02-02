"""
Check #7: Price Reasonableness (סבירות מחירים)

Validate price ratios are within acceptable variance.
"""

import time
import logging
from typing import Any, Dict, List

from mizrahi_shared.models import CheckResult

logger = logging.getLogger(__name__)

CHECK_ID = "price_reasonableness"
CHECK_NAME_HE = "סבירות מחירים"


async def check_price_reasonableness(data: Dict[str, Any]) -> CheckResult:
    """
    Validate that prices are reasonable compared to calculated values.

    Args:
        data: Dictionary containing:
            - current_report: Current month's report data
            - parameters: Hook parameters including price_variance_threshold

    Returns:
        CheckResult with price discrepancies as findings
    """
    start_time = time.time()
    findings: List[Dict[str, Any]] = []

    try:
        current_report = data.get("current_report", [])
        parameters = data.get("parameters", {})

        # Get threshold from parameters (default 7.5%)
        threshold_pct = parameters.get("price_variance_threshold", 7.5)

        for row in current_report:
            quantity = row.get("quantity") or row.get("כמות", 0)
            price = row.get("price") or row.get("מחיר", 0)
            value = row.get("value") or row.get("שווי", 0)

            try:
                quantity = float(quantity) if quantity else 0
                price = float(price) if price else 0
                value = float(value) if value else 0
            except (ValueError, TypeError):
                continue

            # Skip if missing data
            if quantity == 0 or price == 0:
                continue

            # Calculate expected value
            expected_value = quantity * price

            # Calculate variance
            if expected_value != 0:
                variance_pct = abs((value - expected_value) / expected_value) * 100
            else:
                variance_pct = 0

            # Flag if variance exceeds threshold
            if variance_pct > threshold_pct:
                findings.append({
                    "מספר קרן": row.get("fund_id") or row.get("מספר קרן", ""),
                    "שם קרן": row.get("fund_name") or row.get("שם קרן", ""),
                    "מספר נכס": row.get("asset_id") or row.get("מספר נכס", ""),
                    "שם נכס": row.get("asset_name") or row.get("שם נכס", ""),
                    "כמות": quantity,
                    "מחיר": price,
                    "שווי מדווח": value,
                    "שווי מחושב": round(expected_value, 2),
                    "סטייה %": round(variance_pct, 2),
                })

        # Determine status
        if findings:
            status = "warning"
            message = f"נמצאו {len(findings)} סטיות מחיר מעל {threshold_pct}%"
        else:
            status = "pass"
            message = "כל המחירים סבירים"

        logger.info(f"Price reasonableness check: {len(findings)} price discrepancies found")

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
        logger.exception(f"Price reasonableness check error: {e}")
        return CheckResult(
            check_id=CHECK_ID,
            check_name=CHECK_ID,
            check_name_he=CHECK_NAME_HE,
            status="fail",
            message=f"שגיאה בבדיקה: {str(e)}",
            duration_ms=int((time.time() - start_time) * 1000),
        )
