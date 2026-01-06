"""Custom exceptions."""

from typing import Any, Dict, List, Optional


class AppException(Exception):
    """Base app exception."""
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        """Init."""
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """To dict."""
        response = {
            "error": {
                "code": self.error_code,
                "message": self.message,
            }
        }
        if self.details:
            response["error"]["details"] = self.details
        return response


class NotFoundException(AppException):
    """404 Not found."""
    
    def __init__(
        self,
        resource: str = "Resource",
        resource_id: Optional[str] = None,
        message: Optional[str] = None,
    ):
        """Init."""
        if message is None:
            if resource_id:
                message = f"{resource} with ID '{resource_id}' not found"
            else:
                message = f"{resource} not found"
        
        super().__init__(
            message=message,
            status_code=404,
            error_code="NOT_FOUND",
            details={"resource": resource, "resource_id": resource_id},
        )


class ConflictException(AppException):
    """409 Conflict."""
    
    def __init__(
        self,
        message: str = "Resource already exists",
        field: Optional[str] = None,
        value: Optional[str] = None,
    ):
        """
        Initialize conflict exception.
        
        Args:
            message: Error message
            field: Field that caused the conflict
            value: Value that caused the conflict
        """
        details = {}
        if field:
            details["field"] = field
        if value:
            details["value"] = value
        
        super().__init__(
            message=message,
            status_code=409,
            error_code="CONFLICT",
            details=details,
        )


class ValidationException(AppException):
    """422 Validation error."""
    
    def __init__(
        self,
        message: str = "Validation error",
        errors: Optional[List[Dict[str, Any]]] = None,
    ):
        """Init."""
        super().__init__(
            message=message,
            status_code=422,
            error_code="VALIDATION_ERROR",
            details={"errors": errors or []},
        )


class UnauthorizedException(AppException):
    """401 Unauthorized."""
    
    def __init__(self, message: str = "Authentication required"):
        """Init."""
        super().__init__(
            message=message,
            status_code=401,
            error_code="UNAUTHORIZED",
        )


class ForbiddenException(AppException):
    """403 Forbidden."""
    
    def __init__(self, message: str = "Access denied"):
        """Init."""
        super().__init__(
            message=message,
            status_code=403,
            error_code="FORBIDDEN",
        )


class DatabaseException(AppException):
    """500 Database error."""
    
    def __init__(
        self,
        message: str = "Database operation failed",
        operation: Optional[str] = None,
    ):
        """Init."""
        details = {}
        if operation:
            details["operation"] = operation
        
        super().__init__(
            message=message,
            status_code=500,
            error_code="DATABASE_ERROR",
            details=details,
        )


class ExternalServiceException(AppException):
    """502 External service error."""
    
    def __init__(
        self,
        message: str = "External service unavailable",
        service: Optional[str] = None,
    ):
        """Init."""
        details = {}
        if service:
            details["service"] = service
        
        super().__init__(
            message=message,
            status_code=502,
            error_code="EXTERNAL_SERVICE_ERROR",
            details=details,
        )
