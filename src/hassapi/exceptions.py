"""Host custom module exceptions."""


class HassapiBaseException(Exception):
    """Base HASS API Exception."""


class ClientError(HassapiBaseException):
    """HASS API Client Exception."""


class BadRequest(ClientError):
    """400 Bad Request Error."""


class Unauthorised(ClientError):
    """401 Unauthorised Error."""


class Forbidden(ClientError):
    """403 Forbidden Error."""


class NotFound(ClientError):
    """404 Not Found Error."""


class MethodNotAllowed(ClientError):
    """405 Method Not Allowed Error."""


class TooManyRequests(ClientError):
    """429 Too Many Requests Error."""


class InternalServerError(ClientError):
    """500 Internal Server Error."""


class BadGateway(ClientError):
    """502 BadGateway Error."""


class ServiceUnavailable(ClientError):
    """503 Service Unavailable Error."""


class ModelError(HassapiBaseException):
    """HASS API Model Exception."""


_errors = {
    400: BadRequest,
    401: Unauthorised,
    403: Forbidden,
    404: NotFound,
    405: MethodNotAllowed,
    429: TooManyRequests,
    500: InternalServerError,
    502: BadGateway,
    503: ServiceUnavailable,
}


def get_error(status_code: int) -> HassapiBaseException:
    """Get error by HTTP response status code."""
    return _errors.get(status_code, HassapiBaseException)  # type: ignore
