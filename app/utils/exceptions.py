"""
Custom Exceptions Module

Defines application-specific exceptions with proper HTTP status code mapping.
All exceptions inherit from a base AppException for consistent handling.
"""

from typing import Any, Dict, List, Optional


class AppException(Exception):
    """
    Base exception for all application-specific errors.
    
    Provides a consistent interface for error responses including
    HTTP status codes, error codes, and detailed messages.
    """
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the exception.
        
        Args:
            message: Human-readable error message
            status_code: HTTP status code for the response
            error_code: Machine-readable error code
            details: Additional error details
        """
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert exception to dictionary for JSON response.
        
        Returns:
            Dictionary representation of the error
        """
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
    """
    Exception for resource not found errors.
    
    HTTP Status: 404
    """
    
    def __init__(
        self,
        resource: str = "Resource",
        resource_id: Optional[str] = None,
        message: Optional[str] = None,
    ):
        """
        Initialize not found exception.
        
        Args:
            resource: Type of resource that wasn't found
            resource_id: ID of the resource (if applicable)
            message: Custom message (overrides default)
        """
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
    """
    Exception for resource conflict errors.
    
    Used when a resource already exists or conflicts with current state.
    HTTP Status: 409
    """
    
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
    """
    Exception for validation errors.
    
    Used when input data fails validation rules.
    HTTP Status: 422
    """
    
    def __init__(
        self,
        message: str = "Validation error",
        errors: Optional[List[Dict[str, Any]]] = None,
    ):
        """
        Initialize validation exception.
        
        Args:
            message: General error message
            errors: List of specific validation errors
        """
        super().__init__(
            message=message,
            status_code=422,
            error_code="VALIDATION_ERROR",
            details={"errors": errors or []},
        )


class UnauthorizedException(AppException):
    """
    Exception for authentication errors.
    
    Used when user is not authenticated.
    HTTP Status: 401
    """
    
    def __init__(self, message: str = "Authentication required"):
        """
        Initialize unauthorized exception.
        
        Args:
            message: Error message
        """
        super().__init__(
            message=message,
            status_code=401,
            error_code="UNAUTHORIZED",
        )


class ForbiddenException(AppException):
    """
    Exception for authorization errors.
    
    Used when user doesn't have permission to access a resource.
    HTTP Status: 403
    """
    
    def __init__(self, message: str = "Access denied"):
        """
        Initialize forbidden exception.
        
        Args:
            message: Error message
        """
        super().__init__(
            message=message,
            status_code=403,
            error_code="FORBIDDEN",
        )


class DatabaseException(AppException):
    """
    Exception for database errors.
    
    Used when a database operation fails.
    HTTP Status: 500
    """
    
    def __init__(
        self,
        message: str = "Database operation failed",
        operation: Optional[str] = None,
    ):
        """
        Initialize database exception.
        
        Args:
            message: Error message
            operation: Database operation that failed
        """
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
    """
    Exception for external service errors.
    
    Used when an external API or service call fails.
    HTTP Status: 502
    """
    
    def __init__(
        self,
        message: str = "External service unavailable",
        service: Optional[str] = None,
    ):
        """
        Initialize external service exception.
        
        Args:
            message: Error message
            service: Name of the external service
        """
        details = {}
        if service:
            details["service"] = service
        
        super().__init__(
            message=message,
            status_code=502,
            error_code="EXTERNAL_SERVICE_ERROR",
            details=details,
        )
