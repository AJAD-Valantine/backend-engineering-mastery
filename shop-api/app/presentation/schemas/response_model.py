from typing import Generic, TypeVar

from fastapi import status
from pydantic import BaseModel

T = TypeVar("T")


class ResponseModel(BaseModel, Generic[T]):
    status: bool
    data: T
    code: int
    message: str


def success_response(data, message):
    return ResponseModel(
        message=message, data=data, status=True, code=status.HTTP_200_OK
    )


def error_response(error, code=status.HTTP_400_BAD_REQUEST):
    return ResponseModel(status=False, data=None, code=code, message=error)
