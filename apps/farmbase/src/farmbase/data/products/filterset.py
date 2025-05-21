from pydantic import Field
from sqlalchemy_filterset import (
    Filter,
    JoinStrategy,
    OrderingField,
    OrderingFilter,
    SearchFilter,
)

from ...database.core import BaseFilterSet
from ...enums import ProductCategory
from ...models import PaginationParams
from .models import Manufacturer, Product


class ProductFilterSet(BaseFilterSet[Product]):
    name = SearchFilter(Product.name)
    category = Filter(Product.category)
    # price = RangeFilter(Product.price)
    # is_active = Filter(Product.is_active)
    manufacturer = Filter(
        Manufacturer.name,
        strategy=JoinStrategy(
            Manufacturer,
            Product.manufacturer_id == Manufacturer.id,
        ),
    )
    ordering = OrderingFilter(
        id=OrderingField(Product.id),
        name=OrderingField(Product.name),
        price=OrderingField(Product.price),
    )


class ProductQueryParams(PaginationParams):
    name: str | None = Field(None)
    category: ProductCategory | None = Field(None)
