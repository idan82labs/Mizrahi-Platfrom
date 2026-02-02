"""
Shared data models for Mizrahi Compliance Platform.

These models are used across the platform for consistent data representation.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pathlib import Path


# ============================================
# Fund Manager Models
# ============================================

@dataclass
class Manager:
    """Fund manager definition."""
    key: str
    id: str
    name_he: str
    name_en: str
    enabled: bool = True
    contact_email: Optional[str] = None


# ============================================
# Hook Configuration Models
# ============================================

@dataclass
class CheckConfig:
    """Configuration for a single validation check."""
    id: str
    name_he: str
    description: str
    enabled: bool = True


@dataclass
class HookConfig:
    """Configuration for a validation hook."""
    id: str
    name: str
    name_he: str
    description: str
    status: str  # "active" | "development" | "specification"
    schedule_enabled: bool
    schedule_cron: Optional[str]
    schedule_timezone: str
    parameters: Dict[str, Any]
    checks: List[CheckConfig]
    email_enabled: bool
    email_template: str
    email_cc: List[str] = field(default_factory=list)


# ============================================
# Check Result Models
# ============================================

@dataclass
class CheckResult:
    """Result of a single validation check."""
    check_id: str
    check_name: str
    check_name_he: str
    status: str  # "pass" | "fail" | "warning" | "skipped"
    message: str
    findings_count: int = 0
    findings: List[Dict[str, Any]] = field(default_factory=list)
    duration_ms: int = 0

    @property
    def is_pass(self) -> bool:
        return self.status == "pass"

    @property
    def is_fail(self) -> bool:
        return self.status == "fail"

    @property
    def is_warning(self) -> bool:
        return self.status == "warning"


@dataclass
class HookResult:
    """Result of complete hook execution."""
    hook_id: str
    manager_name: str
    manager_id: str
    status: str  # "success" | "partial" | "failed"
    message: str
    checks: List[CheckResult]
    output_file: Optional[Path] = None
    email_sent: bool = False
    email_recipients: List[str] = field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: float = 0.0
    error: Optional[str] = None

    @property
    def is_success(self) -> bool:
        return self.status == "success"

    @property
    def passed_checks(self) -> List[CheckResult]:
        return [c for c in self.checks if c.is_pass]

    @property
    def failed_checks(self) -> List[CheckResult]:
        return [c for c in self.checks if c.is_fail]

    @property
    def warning_checks(self) -> List[CheckResult]:
        return [c for c in self.checks if c.is_warning]

    def to_summary_dict(self) -> Dict[str, Any]:
        """Convert to summary dictionary for API responses."""
        return {
            "hook_id": self.hook_id,
            "manager_name": self.manager_name,
            "status": self.status,
            "message": self.message,
            "checks_total": len(self.checks),
            "checks_passed": len(self.passed_checks),
            "checks_failed": len(self.failed_checks),
            "checks_warning": len(self.warning_checks),
            "email_sent": self.email_sent,
            "duration_seconds": self.duration_seconds,
        }


# ============================================
# Job Status Models
# ============================================

class JobStatus(str, Enum):
    """Job execution status."""
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobTrigger(str, Enum):
    """How the job was triggered."""
    SCHEDULED = "scheduled"
    MANUAL = "manual"
    API = "api"


@dataclass
class JobProgress:
    """Current progress of a running job."""
    current_check: Optional[str] = None
    checks_completed: int = 0
    checks_total: int = 0
    message: str = ""

    @property
    def percent(self) -> int:
        if self.checks_total == 0:
            return 0
        return int((self.checks_completed / self.checks_total) * 100)


# ============================================
# Transaction Models (for Special Transactions hook)
# ============================================

@dataclass
class TransactionRow:
    """Represents a single transaction from special transactions report."""
    row_index: int
    fund_id: Optional[int] = None
    fund_name: Optional[str] = None
    security_no: Optional[int] = None
    security_name: Optional[str] = None
    quantity: Optional[float] = None
    price: Optional[float] = None
    total_value: Optional[float] = None
    transaction_date: Optional[datetime] = None
    transaction_time: Optional[str] = None
    transaction_type: Optional[int] = None
    decision_method: Optional[int] = None
    counterparty_fund_id: Optional[int] = None
    counterparty_fund_name: Optional[str] = None

    # דחצ (External Director) votes
    dachatz_votes: List[int] = field(default_factory=list)

    @property
    def has_any_dachatz_vote_1(self) -> bool:
        """Check if any דחצ voted 1."""
        return 1 in self.dachatz_votes

    @property
    def has_any_dachatz_vote_2(self) -> bool:
        """Check if any דחצ voted 2."""
        return 2 in self.dachatz_votes

    @property
    def is_buy(self) -> bool:
        """Check if this is a buy transaction."""
        return self.transaction_type in {1, 3, 5}  # Adjust based on actual codes

    @property
    def is_sell(self) -> bool:
        """Check if this is a sell transaction."""
        return self.transaction_type in {2, 4, 6}  # Adjust based on actual codes


@dataclass
class ExceptionRow:
    """Represents an exception/finding from validation."""
    txn_id: str
    check_id: str
    check_name: str
    severity: str  # "error" | "warning" | "info"
    message: str
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PriceCheckResult:
    """Result of TASE price validation."""
    txn_id: str
    security_no: str
    security_name: str
    txn_price: float
    tase_price: Optional[float]
    variance_pct: Optional[float]
    status: str  # "pass" | "fail" | "no_data"

    @property
    def is_within_threshold(self) -> bool:
        return self.status == "pass"


@dataclass
class SampleTransaction:
    """Transaction selected for sampling/manual review."""
    txn_id: str
    fund_name: str
    security_no: int
    security_name: str
    quantity: float
    price: float
    transaction_date: str
    decision_method: int
    status: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "txn_id": self.txn_id,
            "fund_name": self.fund_name,
            "security_no": self.security_no,
            "security_name": self.security_name,
            "quantity": self.quantity,
            "price": self.price,
            "transaction_date": self.transaction_date,
            "decision_method": self.decision_method,
            "status": self.status,
        }
