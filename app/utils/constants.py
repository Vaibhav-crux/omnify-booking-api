class ErrorMessages:
    INVALID_REQUEST = "Invalid request data provided."
    NOT_FOUND = "Resource not found."
    CONFLICT = "Resource already exists."
    INTERNAL_SERVER_ERROR = "An unexpected error occurred."
    UNAUTHORIZED = "Unauthorized access."
    FORBIDDEN = "Access forbidden."
    INVALID_TOKEN = "Invalid or expired token."
    INVALID_PAGE = "Page number must be a positive integer."
    INVALID_LIMIT = "Limit must be a positive integer not exceeding 100."
    NO_CLASSES_FOUND = "No classes found for the given criteria."

class RoleConstants:
    MAX_NAME_LENGTH = 255
    DEFAULT_STATUS = "active"
    NAME_REQUIRED = "Role name is required."
    NAME_TOO_LONG = f"Role name must not exceed {MAX_NAME_LENGTH} characters."
    DUPLICATE_NAME = "A role with this name already exists."