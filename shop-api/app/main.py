from app.database import init_models
from app.presentation.routers.cart_item_router import cart_item_router
from app.presentation.routers.customer_router import customer_router
from app.presentation.routers.order_router import order_router
from app.presentation.routers.payment_router import payment_router
from app.presentation.routers.product_router import product_router
from fastapi import FastAPI

app = FastAPI()

init_models()

app.include_router(customer_router)
app.include_router(product_router)
app.include_router(cart_item_router)
app.include_router(order_router)
app.include_router(payment_router)
