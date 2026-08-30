from fastapi import APIRouter, Depends
from starlette import status

from app.core.dependencies import get_product_service, require_admin
from app.schemas.product import (
    ProductCreateRequest,
    ProductResponse,
    ProductUpdateRequest,
)
from app.services.product import ProductService

from ..models.product import Products

product_router = APIRouter(prefix="/products", tags=["Products"])

# Admin Only
@product_router.post(
    path="/",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new product",
    dependencies=[Depends(require_admin)],
)
def create_product(
    request: ProductCreateRequest,
    product_service : ProductService = Depends(get_product_service)
) -> Products:
    return product_service.add_product(request)


# Public Route
@product_router.get(
    path="/",
    response_model=list[ProductResponse],
    status_code=status.HTTP_200_OK,
    summary="Get all products",
)
def get_all_products(
    product_service : ProductService = Depends(get_product_service)

) -> list[Products]:
    return product_service.get_all_products()


# Public Route
@product_router.get(
    path="/{product_id}",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a product",
)
def get_product(
        product_id: int,
        product_service : ProductService = Depends(get_product_service)
) -> Products:
    return product_service.get_product_by_id(product_id)


# Admin Only
@product_router.patch(
    path="/{product_id}",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a product",
    dependencies=[Depends(require_admin)],
)
def update_product(
    product_id: int,
    request: ProductUpdateRequest,
    product_service : ProductService = Depends(get_product_service)
) -> Products:
    return product_service.update_product(
        product_id=product_id,
        request=request
    )


# Admin Only
@product_router.delete(
    path="/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a product",
    dependencies=[Depends(require_admin)],
)
def delete_product(
    product_id: int,
    product_service : ProductService = Depends(get_product_service)
) -> None:
    product_service.remove_product(product_id)
