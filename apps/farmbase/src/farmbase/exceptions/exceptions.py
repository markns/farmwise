from fastapi_problem import error



# fastapi_problem.error.ServerProblem provides status 500 errors
class ServiceError(error.ServerProblem):
    """failures in external services or APIs, like a database or a third-party service"""

    pass

# fastapi_problem.error.NotFoundProblem provides status 404 errors
class EntityDoesNotExistError(error.NotFoundProblem):
    """database returns nothing"""

    pass

# fastapi_problem.error.ConflictProblem provides status 409 errors
class EntityAlreadyExistsError(error.ConflictProblem):
    """conflict detected, like trying to create a resource that already exists"""

    pass


#     "BadRequestProblem",
#     "ForbiddenProblem", TODO:
#     "RedirectProblem",
#     "UnauthorisedProblem",
#     "UnprocessableProblem",




class AuthenticationFailed(error.UnauthorisedProblem):
    """invalid authentication credentials"""

    pass


class InvalidTokenError(error.UnauthorisedProblem):
    """invalid token"""

    pass

