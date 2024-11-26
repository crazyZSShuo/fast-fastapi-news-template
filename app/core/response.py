from typing import Any, Optional
from fastapi.responses import JSONResponse
from fastapi import status

def success_response(*, data: Any = None, message: str = "Success") -> dict:
    return {
        "code": status.HTTP_200_OK,
        "message": message,
        "data": data
    }

def error_response(
    *,
    code: int = status.HTTP_400_BAD_REQUEST,
    message: str = "Error",
    data: Any = None
) -> dict:
    return {
        "code": code,
        "message": message,
        "data": data
    }

class CustomJSONResponse(JSONResponse):
    def __init__(
        self,
        content: Any,
        status_code: int = status.HTTP_200_OK,
        headers: Optional[dict] = None,
        media_type: Optional[str] = None,
        background: Optional[Any] = None,
    ) -> None:
        if isinstance(content, dict) and "code" in content:
            super().__init__(
                content=content,
                status_code=status_code,
                headers=headers,
                media_type=media_type,
                background=background,
            )
        else:
            super().__init__(
                content=success_response(data=content),
                status_code=status_code,
                headers=headers,
                media_type=media_type,
                background=background,
            )
