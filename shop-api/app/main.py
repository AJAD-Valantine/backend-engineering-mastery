from fastapi import FastAPI

from app.core.database import init_models
from app.exceptions.handlers import register_exception_handlers
from app.routers.auth_router import auth_router
from app.routers.cart_item_router import cart_item_router
from app.routers.order_router import order_router
from app.routers.payment_router import payment_router
from app.routers.product_router import product_router
from app.routers.user_router import user_router

app = FastAPI()

init_models()

register_exception_handlers(app)

app.include_router(user_router)
app.include_router(product_router)
app.include_router(cart_item_router)
app.include_router(order_router)
app.include_router(payment_router)
app.include_router(auth_router)