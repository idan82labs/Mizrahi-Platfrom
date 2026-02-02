"""
Check #1: Duplicates (עסקאות כפולות)

Identify inter-fund transactions (buy/sell pairs with matching security, date, quantity).
"""

import time
import logging
from typing import Any, Dict, List
from collections import defaultdict

from mizrahi_shared.models import CheckResult

logger = logging.getLogger(__name__)

CHECK_ID = "chk1_duplicates"
CHECK_NAME_HE = "עסקאות כפולות"


async def check_duplicates(data: Dict[str, Any]) -> CheckResult:
    """
    Find inter-fund transactions (buy/sell pairs).

    A duplicate is identified when:
    - Same security number
    - Same date
    - Same quantity (one positive, one negative or both same sign but opposite funds)

    Args:
        data: Dictionary containing:
            - transactions: List of transaction records

    Returns:
        CheckResult with duplicate pairs as findings
    """
    start_time = time.time()
    findings: List[Dict[str, Any]] = []

    try:
        transactions = data.get("transactions", [])

        # Group transactions by (security_no, date, abs(quantity))
        groups: Dict[tuple, List[Dict]] = defaultdict(list)

        for txn in transactions:
            security_no = txn.get("security_no") or txn.get("מספר ני\"ע")
            txn_date = txn.get("transaction_date") or txn.get("תאריך")
            quantity = txn.get("quantity") or txn.get("כמות", 0)

            try:
                quantity = float(quantity) if quantity else 0
            except (ValueError, TypeError):
                quantity = 0

            if security_no and txn_date:
                key = (str(security_no), str(txn_date), abs(quantity))
                groups[key].append(txn)

        # Find groups with multiple transactions (potential duplicates)
        for key, txns in groups.items():
            if len(txns) >= 2:
                security_no, txn_date, quantity = key

                # Check if this looks like a buy/sell pair
                fund_ids = set()
                for txn in txns:
                    fund_id = txn.get("fund_id") or txn.get("מספר קרן", "")
                    fund_ids.add(str(fund_id))

                # If multiple funds involved, it's an inter-fund transaction
                if len(fund_ids) >= 2:
                    for txn in txns:
                        findings.append({
                            "מספר ני\"ע": security_no,
                            "שם ני\"ע": txn.get("security_name") or txn.get("שם ני\"ע", ""),
                            "תאריך": txn_date,
                            "כמות": txn.get("quantity") or txn.get("כמות", 0),
                            "מחיר": txn.get("price") or txn.get("מחיר", 0),
                            "מספר קרן": txn.get("fund_id") or txn.get("מספר קרן", ""),
                            "שם קרן": txn.get("fund_name") or txn.get("שם קרן", ""),
                            "סוג עסקה": txn.get("transaction_type") or txn.get("סוג עסקה", ""),
                        })

        # Determine status
        if findings:
            # Duplicates are informational, not failures
            status = "warning"
            message = f"נמצאו {len(findings)} עסקאות בין-קרנות"
        else:
            status = "pass"
            message = "לא נמצאו עסקאות כפולות בין קרנות"

        logger.info(f"Duplicates check: {len(findings)} inter-fund transactions found")

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
        logger.exception(f"Duplicates check error: {e}")
        return CheckResult(
            check_id=CHECK_ID,
            check_name=CHECK_ID,
            check_name_he=CHECK_NAME_HE,
            status="fail",
            message=f"שגיאה בבדיקה: {str(e)}",
            duration_ms=int((time.time() - start_time) * 1000),
        )
