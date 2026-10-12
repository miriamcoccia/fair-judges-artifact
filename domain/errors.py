"""
errors.py: This file handles specific errors that may arise when running the project. Domain errors include errors about the Item and Verdict.
"""

class DomainError(Exception):
    """Base class for all domain-layer errors."""
    pass

class ItemError(DomainError):
    """Raised when an Item does not match the correct format."""
    pass

class VerdictError(DomainError):
    """Raised when the verdict is not in the correct format."""
    pass

class InvalidRubricError(DomainError):
    """Raised when a rubric is missing or malformed for a given property."""
    pass