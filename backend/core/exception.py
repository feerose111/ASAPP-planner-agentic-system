from fastapi import HTTPException, status, FastAPI , Request
from http import HTTPStatus
from fastapi.responses import JSONResponse


class CustomException(HTTPException):
    def __init__(
            self,
            message: str | None = None ,
            status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
            success: bool = False,
    ) -> None:
        if not message:
            message = HTTPStatus(status_code).description

        self.success = success
        super().__init__(status_code = status_code , detail= message  )


class NotFoundException(CustomException):
    def __init__(self, message: str | None = None) -> None:
        super().__init__(
            message = message ,
            status_code = status.HTTP_404_NOT_FOUND,
            success = False
        )

class FailedException(CustomException):
    def __init__(self, message: str | None = None) -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            success=False
        )

class UnauthorizedException(CustomException):
    def __init__(self, message: str | None = None) -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            success=False
        )

def register_exception_handlers(app : FastAPI):
    """register exception handler in fastapi app"""
    @app.exception_handler(CustomException)
    async def custom_exception_handlers(request: Request, exc: CustomException):
        return JSONResponse(
            status_code = exc.status_code,
            content = {
                'success' : getattr(exc, "success", False),
                'message' : exc.detail,
                 'data' : None,
            },
        )