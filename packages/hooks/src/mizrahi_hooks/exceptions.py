"""
Custom exceptions for Mizrahi hooks.
"""


class HookError(Exception):
    """Base exception for hook errors."""
    pass


class ValidationError(HookError):
    """Raised when input validation fails."""
    pass


class DataFetchError(HookError):
    """Raised when data fetching fails."""
    pass


class CheckError(HookError):
    """Raised when a check execution fails."""

    def __init__(self, check_id: str, message: str):
        self.check_id = check_id
        super().__init__(f"Check '{check_id}' failed: {message}")


class ReportGenerationError(HookError):
    """Raised when report generation fails."""
    pass


class ConfigurationError(HookError):
    """Raised when hook configuration is invalid."""
    pass
