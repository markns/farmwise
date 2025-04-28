class FarmbaseException(Exception):
    pass


class FarmbasePluginException(FarmbaseException):
    pass


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
