from fastapi import FastAPI

from app.exceptions.handlers import register_exception_handlers
from app.routers.auth import auth_router
from app.routers.cart_item import cart_item_router
from app.routers.order import order_router
from app.routers.payment import payment_router
from app.routers.product import product_router
from app.routers.user import user_router

app = FastAPI()

register_exception_handlers(app)

app.include_router(user_router)
app.include_router(product_router)
app.include_router(cart_item_router)
app.include_router(order_router)
app.include_router(payment_router)
app.include_router(auth_router)