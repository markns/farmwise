"""
Service layer for products and manufacturers.
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from farmbase.products.models import Product, ProductCreate, ProductUpdate


async def get(*, db_session: AsyncSession, product_id: int) -> Optional[Product]:
    """Fetch a product by its ID."""
    result = await db_session.execute(select(Product).where(Product.id == product_id))
    return result.scalars().first()


async def create(*, db_session: AsyncSession, product_in: ProductCreate) -> Product:
    """Create a new product."""
    product = Product(**product_in.model_dump())
    db_session.add(product)
    await db_session.commit()
    return product


async def update(*, db_session: AsyncSession, product: Product, product_in: ProductUpdate) -> Product:
    """Update an existing product."""
    data = product_in.model_dump(skip_defaults=True)
    for field, value in data.items():
        setattr(product, field, value)
    await db_session.commit()
    return product


async def delete(*, db_session: AsyncSession, product_id: int) -> None:
    """Delete a product by its ID."""
    product = await get(db_session=db_session, product_id=product_id)
    if product:
        await db_session.delete(product)
        await db_session.commit()
