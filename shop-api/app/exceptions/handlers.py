from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.exceptions.base import ShopException

async def shop_exception_handler(request: Request, exc: ShopException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
        headers=exc.headers, # Inject the headers here
    )

def register_exception_handlers(app: FastAPI):
    app.add_exception_handler(ShopException, shop_exception_handler) # type: ignore