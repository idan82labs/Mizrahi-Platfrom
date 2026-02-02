"""
Check #7: Problematic Securities (ניירות בעייתיים)

Flag securities on warning/halt/restricted lists.
"""

import time
import logging
from typing import Any, Dict, List, Set

from mizrahi_shared.models import CheckResult

logger = logging.getLogger(__name__)

CHECK_ID = "chk7_problematic"
CHECK_NAME_HE = "ניירות בעייתיים"

# Known problematic security types/statuses
PROBLEMATIC_STATUSES = {
    "halted",
    "suspended",
    "warning",
    "restricted",
    "מושעה",
    "הקפאה",
    "אזהרה",
    "מוגבל",
}


async def check_problematic_securities(data: Dict[str, Any]) -> CheckResult:
    """
    Flag securities that are on warning, halt, or restricted lists.

    Args:
        data: Dictionary containing:
            - transactions: List of transaction records
            - funds_list: Mutual funds list (may contain security status info)

    Returns:
        CheckResult with problematic securities as findings
    """
    start_time = time.time()
    findings: List[Dict[str, Any]] = []

    try:
        transactions = data.get("transactions", [])

        # Build set of problematic securities from funds list or external source
        # This would typically be fetched from TASE or a dedicated API
        problematic_securities: Set[str] = set()

        # Check transactions against problematic list
        for txn in transactions:
            security_no = str(txn.get("security_no") or txn.get("מספר ני\"ע", ""))
            security_status = txn.get("security_status") or txn.get("סטטוס ני\"ע", "")

            # Check if security is in problematic list
            if security_no in problematic_securities:
                findings.append({
                    "מספר ני\"ע": security_no,
                    "שם ני\"ע": txn.get("security_name") or txn.get("שם ני\"ע", ""),
                    "תאריך": txn.get("transaction_date") or txn.get("תאריך", ""),
                    "מספר קרן": txn.get("fund_id") or txn.get("מספר קרן", ""),
                    "שם קרן": txn.get("fund_name") or txn.get("שם קרן", ""),
                    "סטטוס": "ברשימת ניירות בעייתיים",
                    "סיבה": "נייר ערך נמצא ברשימת מעקב",
                })

            # Check if status indicates problem
            if security_status and str(security_status).lower() in PROBLEMATIC_STATUSES:
                findings.append({
                    "מספר ני\"ע": security_no,
                    "שם ני\"ע": txn.get("security_name") or txn.get("שם ני\"ע", ""),
                    "תאריך": txn.get("transaction_date") or txn.get("תאריך", ""),
                    "מספר קרן": txn.get("fund_id") or txn.get("מספר קרן", ""),
                    "שם קרן": txn.get("fund_name") or txn.get("שם קרן", ""),
                    "סטטוס": security_status,
                    "סיבה": "סטטוס נייר ערך בעייתי",
                })

        # Remove duplicates (same security might appear multiple times)
        seen = set()
        unique_findings = []
        for finding in findings:
            key = (finding["מספר ני\"ע"], finding["מספר קרן"], finding["סיבה"])
            if key not in seen:
                seen.add(key)
                unique_findings.append(finding)
        findings = unique_findings

        # Determine status
        if findings:
            status = "warning"
            message = f"נמצאו {len(findings)} ניירות בעייתיים"
        else:
            status = "pass"
            message = "לא נמצאו ניירות בעייתיים"

        logger.info(f"Problematic securities check: {len(findings)} issues found")

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
        logger.exception(f"Problematic securities check error: {e}")
        return CheckResult(
            check_id=CHECK_ID,
            check_name=CHECK_ID,
            check_name_he=CHECK_NAME_HE,
            status="fail",
            message=f"שגיאה בבדיקה: {str(e)}",
            duration_ms=int((time.time() - start_time) * 1000),
        )
