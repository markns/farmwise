import json
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status

from farmbase.database.core import DbSession
from farmbase.database.service import CommonParameters, search_filter_sort_paginate
from farmbase.models import PrimaryKey
from farmbase.enums import ProductCategory

from .models import (
    ProductRead,
    ProductCreate,
    ProductUpdate,
    ProductPagination,
)
from .service import get, create, update, delete

router = APIRouter()


@router.get("", response_model=ProductPagination)
async def list_products(
    common: CommonParameters,
    category: Optional[ProductCategory] = None,
):
    """List products, optionally filtered by category."""
    # Merge category filter into existing filters
    if category:
        spec = common.get("filter_spec")
        # parse existing filter spec if present
        filters = []
        if spec:
            filters = json.loads(spec) if isinstance(spec, str) else spec
            if not isinstance(filters, list):
                filters = [filters]
        # add category filter
        filters.append({"field": "category", "op": "==", "value": category})
        common["filter_spec"] = filters
    return await search_filter_sort_paginate(model="Product", **common)


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