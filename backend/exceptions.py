class ApiError(Exception):
    status_code = 400

    def __init__(self, message, *, error_messages=None):
        super().__init__(message)
        self.error_messages = error_messages or [message]


class BadRequestError(ApiError):
    status_code = 400


class NotFoundError(ApiError):
    status_code = 404


class ConflictError(ApiError):
    status_code = 409


class ServiceUnavailableError(ApiError):
    status_code = 503
