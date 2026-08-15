from fastapi import APIRouter, Query, Depends, UploadFile
from starlette import status

from app.core.config import settings
from app.core.dependencies import require_admin, get_product_service
from app.exceptions.image import FileTooLarge
from app.schemas.product import (
    PaginatedProductResponse,
    ProductCreateRequest,
    ProductUpdateRequest,
    ProductResponse,
)
from app.services.product import ProductService

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
):
    return product_service.add_product(request)


# Public Route
@product_router.get(
    path="/",
    response_model=PaginatedProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Get all products",
)
def get_all_products(
    page: int = Query(default=1, ge=1, description="Page number"),
    size: int = Query(default=10, ge=1, le=100, description="Items per page"),
    product_service : ProductService = Depends(get_product_service)

): 
    return product_service.get_all_products(
        page=page,
        size=size)


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
):
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
):
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
):
    return product_service.remove_product(product_id)


# Admin Only
@product_router.patch(
    path="/{product_id}/picture",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_admin)]
)
def upload_product_picture(
        product_id: int,
        file: UploadFile,
        product_service: ProductService = Depends(get_product_service),
):
    if file.size and file.size > settings.max_upload_size_bytes:
        raise FileTooLarge()

    content = file.file.read()
    return product_service.upload_product_image(product_id, content)

# Admin Only
@product_router.delete(
    path="/{product_id}/picture",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_admin)]
)
def delete_product_picture(
        product_id: int,
        product_service: ProductService = Depends(get_product_service),
):
    product_service.remove_product_image(product_id)