"""
Check #4: Decision Method (שיטת ההחלטה)

Validate decision method codes and דחצ voting rules.
"""

import time
import logging
from typing import Any, Dict, List

from mizrahi_shared.models import CheckResult
from mizrahi_shared.constants import DECISION_TYPES_REQUIRING_1, DECISION_TYPES_REQUIRING_1_OR_2

logger = logging.getLogger(__name__)

CHECK_ID = "chk4_decision"
CHECK_NAME_HE = "שיטת ההחלטה"


async def check_decision_method(data: Dict[str, Any]) -> CheckResult:
    """
    Validate decision method compliance and דחצ voting rules.

    Rules:
    - Transaction types {12, 22} require decision method 1
    - Transaction types {31-36} require decision method 1 or 2
    - If decision method = 1, at least one דחצ must have vote = 1
    - Flag any דחצ with vote = 2

    Args:
        data: Dictionary containing:
            - transactions: List of transaction records
            - parameters: Hook parameters

    Returns:
        CheckResult with decision method exceptions as findings
    """
    start_time = time.time()
    findings: List[Dict[str, Any]] = []

    try:
        transactions = data.get("transactions", [])
        parameters = data.get("parameters", {})

        types_requiring_1 = set(
            parameters.get("decision_types_requiring_1", DECISION_TYPES_REQUIRING_1)
        )
        types_requiring_1_or_2 = set(
            parameters.get("decision_types_requiring_1_or_2", DECISION_TYPES_REQUIRING_1_OR_2)
        )

        for txn in transactions:
            txn_type = txn.get("transaction_type") or txn.get("סוג עסקה")
            decision_method = txn.get("decision_method") or txn.get("שיטת החלטה")

            try:
                txn_type = int(txn_type) if txn_type else None
                decision_method = int(decision_method) if decision_method else None
            except (ValueError, TypeError):
                continue

            if txn_type is None:
                continue

            # Check if decision method is required but missing/invalid
            if txn_type in types_requiring_1:
                if decision_method != 1:
                    findings.append({
                        "מספר ני\"ע": txn.get("security_no") or txn.get("מספר ני\"ע", ""),
                        "שם ני\"ע": txn.get("security_name") or txn.get("שם ני\"ע", ""),
                        "סוג עסקה": txn_type,
                        "שיטת החלטה": decision_method,
                        "נדרש": "1",
                        "מספר קרן": txn.get("fund_id") or txn.get("מספר קרן", ""),
                        "סיבה": "סוג עסקה זה מחייב שיטת החלטה 1",
                    })

            elif txn_type in types_requiring_1_or_2:
                if decision_method not in (1, 2):
                    findings.append({
                        "מספר ני\"ע": txn.get("security_no") or txn.get("מספר ני\"ע", ""),
                        "שם ני\"ע": txn.get("security_name") or txn.get("שם ני\"ע", ""),
                        "סוג עסקה": txn_type,
                        "שיטת החלטה": decision_method,
                        "נדרש": "1 או 2",
                        "מספר קרן": txn.get("fund_id") or txn.get("מספר קרן", ""),
                        "סיבה": "סוג עסקה זה מחייב שיטת החלטה 1 או 2",
                    })

            # Check דחצ voting rules
            dachatz_votes = []
            for i in range(1, 5):  # Check up to 4 דחצ votes
                vote_key = f"dachatz_vote_{i}" if f"dachatz_vote_{i}" in txn else f"הצבעת דח\"צ {i}"
                vote = txn.get(vote_key)
                if vote is not None:
                    try:
                        dachatz_votes.append(int(vote))
                    except (ValueError, TypeError):
                        pass

            # Rule 4ג: If decision method = 1, need at least one דחצ with vote = 1
            if decision_method == 1 and dachatz_votes:
                if 1 not in dachatz_votes:
                    findings.append({
                        "מספר ני\"ע": txn.get("security_no") or txn.get("מספר ני\"ע", ""),
                        "שם ני\"ע": txn.get("security_name") or txn.get("שם ני\"ע", ""),
                        "סוג עסקה": txn_type,
                        "שיטת החלטה": decision_method,
                        "הצבעות דח\"צ": str(dachatz_votes),
                        "מספר קרן": txn.get("fund_id") or txn.get("מספר קרן", ""),
                        "סיבה": "שיטת החלטה 1 מחייבת לפחות דח\"צ אחד עם הצבעה 1",
                    })

            # Rule 4ד: Flag any דחצ with vote = 2
            if 2 in dachatz_votes:
                findings.append({
                    "מספר ני\"ע": txn.get("security_no") or txn.get("מספר ני\"ע", ""),
                    "שם ני\"ע": txn.get("security_name") or txn.get("שם ני\"ע", ""),
                    "סוג עסקה": txn_type,
                    "שיטת החלטה": decision_method,
                    "הצבעות דח\"צ": str(dachatz_votes),
                    "מספר קרן": txn.get("fund_id") or txn.get("מספר קרן", ""),
                    "סיבה": "דח\"צ הצביע 2 - נדרשת בדיקה",
                })

        # Determine status
        if findings:
            status = "fail"
            message = f"נמצאו {len(findings)} חריגות בשיטת החלטה"
        else:
            status = "pass"
            message = "כל שיטות ההחלטה תקינות"

        logger.info(f"Decision method check: {len(findings)} exceptions found")

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
        logger.exception(f"Decision method check error: {e}")
        return CheckResult(
            check_id=CHECK_ID,
            check_name=CHECK_ID,
            check_name_he=CHECK_NAME_HE,
            status="fail",
            message=f"שגיאה בבדיקה: {str(e)}",
            duration_ms=int((time.time() - start_time) * 1000),
        )
