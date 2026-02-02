"""
Check #5: Sampling (דגימות)

Generate random samples for manual verification.
"""

import time
import random
import logging
from typing import Any, Dict, List

from mizrahi_shared.models import CheckResult

logger = logging.getLogger(__name__)

CHECK_ID = "chk5_sampling"
CHECK_NAME_HE = "דגימות"


async def check_sampling(data: Dict[str, Any]) -> CheckResult:
    """
    Generate random sample of transactions for manual verification.

    Args:
        data: Dictionary containing:
            - transactions: List of transaction records
            - parameters: Hook parameters including sample_size

    Returns:
        CheckResult with sampled transactions as findings
    """
    start_time = time.time()
    findings: List[Dict[str, Any]] = []

    try:
        transactions = data.get("transactions", [])
        parameters = data.get("parameters", {})

        sample_size = parameters.get("sample_size", 5)

        # Filter valid transactions for sampling
        valid_transactions = [
            txn for txn in transactions
            if txn.get("security_no") or txn.get("מספר ני\"ע")
        ]

        # Sample transactions
        if len(valid_transactions) <= sample_size:
            samples = valid_transactions
        else:
            # Use deterministic seed based on data for reproducibility
            seed = hash(str(len(valid_transactions)))
            random.seed(seed)
            samples = random.sample(valid_transactions, sample_size)

        # Format samples as findings
        for i, txn in enumerate(samples, 1):
            findings.append({
                "מספר דגימה": i,
                "מספר ני\"ע": txn.get("security_no") or txn.get("מספר ני\"ע", ""),
                "שם ני\"ע": txn.get("security_name") or txn.get("שם ני\"ע", ""),
                "תאריך": txn.get("transaction_date") or txn.get("תאריך", ""),
                "כמות": txn.get("quantity") or txn.get("כמות", 0),
                "מחיר": txn.get("price") or txn.get("מחיר", 0),
                "מספר קרן": txn.get("fund_id") or txn.get("מספר קרן", ""),
                "שם קרן": txn.get("fund_name") or txn.get("שם קרן", ""),
                "שיטת החלטה": txn.get("decision_method") or txn.get("שיטת החלטה", ""),
                "סטטוס בדיקה": "",  # For manual verification
            })

        # Determine status (samples are always informational)
        status = "pass"
        message = f"נדגמו {len(findings)} עסקאות לבדיקה ידנית"

        logger.info(f"Sampling check: {len(findings)} transactions sampled")

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
        logger.exception(f"Sampling check error: {e}")
        return CheckResult(
            check_id=CHECK_ID,
            check_name=CHECK_ID,
            check_name_he=CHECK_NAME_HE,
            status="fail",
            message=f"שגיאה בבדיקה: {str(e)}",
            duration_ms=int((time.time() - start_time) * 1000),
        )
