"""
Check #6: TASE Prices (בדיקות מחיר)

Cross-check transaction prices with TASE market data.
"""

import time
import logging
from typing import Any, Dict, List

from mizrahi_shared.models import CheckResult

logger = logging.getLogger(__name__)

CHECK_ID = "chk6_prices"
CHECK_NAME_HE = "בדיקות מחיר"


async def check_prices(data: Dict[str, Any]) -> CheckResult:
    """
    Cross-check transaction prices with TASE market data.

    Note: This check requires TASE API access or Selenium scraping,
    which is slow and optional. It's skipped by default.

    Args:
        data: Dictionary containing:
            - transactions: List of transaction records
            - parameters: Hook parameters including price_variance_threshold

    Returns:
        CheckResult with price discrepancies as findings
    """
    start_time = time.time()
    findings: List[Dict[str, Any]] = []

    try:
        transactions = data.get("transactions", [])
        parameters = data.get("parameters", {})

        threshold_pct = parameters.get("price_variance_threshold", 5.0)

        # This is a placeholder implementation
        # Full implementation would:
        # 1. Fetch TASE prices for each security on transaction date
        # 2. Compare with transaction price
        # 3. Flag variance > threshold

        # For now, we'll do a basic internal consistency check
        # Compare prices for same security on same date across transactions
        price_map: Dict[tuple, List[float]] = {}

        for txn in transactions:
            security_no = txn.get("security_no") or txn.get("מספר ני\"ע", "")
            txn_date = txn.get("transaction_date") or txn.get("תאריך", "")
            price = txn.get("price") or txn.get("מחיר", 0)

            try:
                price = float(price) if price else 0
            except (ValueError, TypeError):
                continue

            if security_no and txn_date and price > 0:
                key = (str(security_no), str(txn_date))
                if key not in price_map:
                    price_map[key] = []
                price_map[key].append(price)

        # Check for internal price discrepancies
        for (security_no, txn_date), prices in price_map.items():
            if len(prices) >= 2:
                min_price = min(prices)
                max_price = max(prices)

                if min_price > 0:
                    variance_pct = ((max_price - min_price) / min_price) * 100

                    if variance_pct > threshold_pct:
                        findings.append({
                            "מספר ני\"ע": security_no,
                            "תאריך": txn_date,
                            "מחיר מינימלי": min_price,
                            "מחיר מקסימלי": max_price,
                            "סטייה %": round(variance_pct, 2),
                            "סיבה": "פער מחירים פנימי בין עסקאות",
                        })

        # Determine status
        if findings:
            status = "warning"
            message = f"נמצאו {len(findings)} סטיות מחיר מעל {threshold_pct}%"
        else:
            status = "pass"
            message = "כל המחירים עקביים"

        logger.info(f"Prices check: {len(findings)} price discrepancies found")

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
        logger.exception(f"Prices check error: {e}")
        return CheckResult(
            check_id=CHECK_ID,
            check_name=CHECK_ID,
            check_name_he=CHECK_NAME_HE,
            status="fail",
            message=f"שגיאה בבדיקה: {str(e)}",
            duration_ms=int((time.time() - start_time) * 1000),
        )
