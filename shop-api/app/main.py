from fastapi import FastAPI

from app.core.database import init_models
from app.exceptions.handlers import register_exception_handlers
from app.routers.auth import auth as auth_router
from app.routers.cart_item import cart_item as cart_item_router
from app.routers.order import order as order_router
from app.routers.payment import payment as payment_router
from app.routers.product import product as product_router
from app.routers.user import user as user_router

app = FastAPI()

init_models()

register_exception_handlers(app)

app.include_router(user_router)
app.include_router(product_router)
app.include_router(cart_item_router)
app.include_router(order_router)
app.include_router(payment_router)
app.include_router(auth_router)