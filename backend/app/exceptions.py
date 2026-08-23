"""
TRACE custom application exceptions.
"""


class TraceException(Exception):
    """
    Base exception for TRACE.
    """

    status_code: int = 500
    error_code: str = "TRACE_ERROR"

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        error_code: str | None = None,
    ) -> None:

        self.message = message

        if status_code is not None:
            self.status_code = status_code

        if error_code is not None:
            self.error_code = error_code

        super().__init__(message)


class PipelineInputError(TraceException):
    """
    Raised when upstream pipeline data is invalid.
    """

    status_code = 400
    error_code = "PIPELINE_INPUT_ERROR"


class PipelineStateError(TraceException):
    """
    Raised when the pipeline is missing required state.
    """

    status_code = 409
    error_code = "PIPELINE_STATE_ERROR"


class IncidentNotFoundError(TraceException):
    """
    Raised when a requested incident doesn't exist.
    """

    status_code = 404
    error_code = "INCIDENT_NOT_FOUND"


class PipelineExecutionError(TraceException):
    """
    Raised when pipeline execution fails unexpectedly.
    """

    status_code = 500
    error_code = "PIPELINE_EXECUTION_ERROR"