class FarmBaseApiError(Exception):
    """base exception class"""

    def __init__(self, message: str, name: str = "FarmBase"):
        self.message = message
        self.name = name
        super().__init__(self.message, self.name)


class FarmbasePluginError(FarmBaseApiError):
    pass


class ServiceError(FarmBaseApiError):
    """failures in external services or APIs, like a database or a third-party service"""

    pass


class EntityDoesNotExistError(FarmBaseApiError):
    """database returns nothing"""

    pass


class EntityAlreadyExistsError(FarmBaseApiError):
    """conflict detected, like trying to create a resource that already exists"""

    pass


class InvalidOperationError(FarmBaseApiError):
    """invalid operations like trying to delete a non-existing entity, etc."""

    pass


class AuthenticationFailed(FarmBaseApiError):
    """invalid authentication credentials"""

    pass


class InvalidTokenError(FarmBaseApiError):
    """invalid token"""

    pass


class InvalidInputError(Exception):
    error_code = "INVALID_INPUT"
    error_message = "Invalid input error"


class NotFoundError(ValueError):
    code = "not_found"
    msg_template = "{msg}"


class FieldNotFoundError(ValueError):
    code = "not_found.field"
    msg_template = "{msg}"


class ModelNotFoundError(ValueError):
    code = "not_found.model"
    msg_template = "{msg}"


class ExistsError(ValueError):
    code = "exists"
    msg_template = "{msg}"


class InvalidConfigurationError(ValueError):
    code = "invalid.configuration"
    msg_template = "{msg}"


class InvalidFilterError(ValueError):
    code = "invalid.filter"
    msg_template = "{msg}"


class InvalidUsernameError(ValueError):
    code = "invalid.username"
    msg_template = "{msg}"


class InvalidPasswordError(ValueError):
    code = "invalid.password"
    msg_template = "{msg}"
