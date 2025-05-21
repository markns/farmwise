from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from farmbase.database.core import DbSession
from farmbase.models import PrimaryKey

from .filterset import ProductFilterSet, ProductQueryParams
from .models import (
    Product,
    ProductCreate,
    ProductPagination,
    ProductRead,
    ProductUpdate,
)
from .service import create, delete, get, update

router = APIRouter()


@router.get("", response_model=ProductPagination)
async def list_products(
    db_session: DbSession,
    query_params: Annotated[ProductQueryParams, Query()],
):
    """List products."""
    stmt = select(Product).options(selectinload(Product.manufacturer))
    filter_set = ProductFilterSet(db_session, stmt)
    params_d = query_params.model_dump(exclude_none=True)
    total = await filter_set.count(params_d)
    products = await filter_set.filter(params_d)
    return ProductPagination(
        items=products,
        items_per_page=query_params.items_per_page,
        page=query_params.page,
        total=total,
    )


@router.post("", response_model=ProductRead)
async def create_product(
    db_session: DbSession,
    product_in: ProductCreate,
):
    """Create a new product."""
    return await create(db_session=db_session, product_in=product_in)


@router.get("/{product_id}", response_model=ProductRead)
async def get_product(
    db_session: DbSession,
    product_id: PrimaryKey,
):
    """Get a product by ID."""
    product = await get(db_session=db_session, product_id=product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "Product not found."}],
        )
    return product


@router.put("/{product_id}", response_model=ProductRead)
async def update_product(
    db_session: DbSession,
    product_id: PrimaryKey,
    product_in: ProductUpdate,
):
    """Update an existing product."""
    product = await get(db_session=db_session, product_id=product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "Product not found."}],
        )
    return await update(db_session=db_session, product=product, product_in=product_in)


@router.delete("/{product_id}", response_model=None)
async def delete_product(
    db_session: DbSession,
    product_id: PrimaryKey,
):
    """Delete a product by ID."""
    product = await get(db_session=db_session, product_id=product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "Product not found."}],
        )
    await delete(db_session=db_session, product_id=product_id)
