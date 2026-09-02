from fastapi import FastAPI

from app.routers.auth import auth_router
from app.routers.cart_item import cart_item_router
from app.routers.product import product_router
from app.routers.user import user_router

app = FastAPI()

app.include_router(user_router)
app.include_router(product_router)
app.include_router(cart_item_router)
app.include_router(auth_router)
