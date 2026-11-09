"""
Global Exception Handlers cho Nyvora API (Python 3.14.x).
Chuẩn hóa phản hồi lỗi theo cấu trúc:
{ status, code, message, detail, errors, timestamp }
"""

from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class NyvoraAPIException( HTTPException ):
    """Ngoại lệ nghiệp vụ chuẩn hóa của Nyvora."""

    def __init__(
        self,
        status_code: int,
        message: str,
        code: str = "NYVORA_ERROR",
        errors: list[dict[str, Any]] | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=message, headers=headers)
        self.code = code
        self.message = message
        self.errors = errors or []


def build_error_payload(
    status_code: int,
    code: str,
    message: str,
    errors: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Đóng gói payload lỗi chuẩn hóa kèm trường `detail` để tương thích ngược."""
    return {
        "status": "error",
        "code": code,
        "message": message,
        "detail": message,
        "errors": errors or [],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def register_exception_handlers(app: FastAPI) -> None:
    """Đăng ký các Global Exception Handlers lên ứng dụng FastAPI."""

    @app.exception_handler(NyvoraAPIException)
    async def nyvora_exception_handler(request: Request, exc: NyvoraAPIException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=build_error_payload(
                status_code=exc.status_code,
                code=exc.code,
                message=exc.message,
                errors=exc.errors,
            ),
            headers=exc.headers,
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        detail_msg = exc.detail if isinstance(exc.detail, str) else "Yêu cầu không hợp lệ"
        code_map = {
            status.HTTP_400_BAD_REQUEST: "BAD_REQUEST",
            status.HTTP_401_UNAUTHORIZED: "UNAUTHORIZED",
            status.HTTP_403_FORBIDDEN: "FORBIDDEN",
            status.HTTP_404_NOT_FOUND: "NOT_FOUND",
            status.HTTP_409_CONFLICT: "CONFLICT",
            status.HTTP_422_UNPROCESSABLE_ENTITY: "VALIDATION_ERROR",
        }
        return JSONResponse(
            status_code=exc.status_code,
            content=build_error_payload(
                status_code=exc.status_code,
                code=code_map.get(exc.status_code, f"HTTP_{exc.status_code}"),
                message=detail_msg,
            ),
            headers=exc.headers,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        formatted_errors = [
            {
                "loc": [str(item) for item in err.get("loc", [])],
                "msg": err.get("msg", "Invalid value"),
                "type": err.get("type", "value_error"),
            }
            for err in exc.errors()
        ]
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=build_error_payload(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                code="VALIDATION_ERROR",
                message="Dữ liệu đầu vào không hợp lệ",
                errors=formatted_errors,
            ),
        )
