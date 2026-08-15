from pathlib import Path

from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from app.core.config import settings
from app.exceptions.handlers import register_exception_handlers
from app.routers.auth import auth_router
from app.routers.cart_item import cart_item_router
from app.routers.product import product_router
from app.routers.user import user_router

Path(settings.media_root).mkdir(
    parents=True,
    exist_ok=True
)

app = FastAPI()

app.mount(
    path="/media",
    app=StaticFiles(directory=settings.media_root),
    name="media"
)

register_exception_handlers(app)

app.include_router(user_router)
app.include_router(product_router)
app.include_router(cart_item_router)
app.include_router(auth_router)