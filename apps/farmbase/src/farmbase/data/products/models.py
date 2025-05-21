from typing import List, Optional

from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from farmbase.database.core import Base
from farmbase.enums import ProductCategory
from farmbase.models import FarmbaseBase, Pagination, PrimaryKey, TimeStampMixin


# TODO: add
class Manufacturer(Base, TimeStampMixin):
    """Manufacturer of agricultural products."""

    __tablename__ = "manufacturer"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)


class Product(Base, TimeStampMixin):
    """An agricultural product, e.g., fungicide, insecticide, herbicide."""

    __tablename__ = "product"
    id: Mapped[int] = mapped_column(primary_key=True)
    category: Mapped[ProductCategory] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    manufacturer_id: Mapped[int] = mapped_column(ForeignKey("manufacturer.id"), nullable=False)
    manufacturer: Mapped[Manufacturer] = relationship("Manufacturer")
    price: Mapped[float] = mapped_column(Float, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


# Pydantic schemas
class ManufacturerRead(FarmbaseBase):
    id: PrimaryKey
    name: str


class ManufacturerCreate(FarmbaseBase):
    name: str


class ProductBase(FarmbaseBase):
    category: ProductCategory
    name: str
    # manufacturer_id: PrimaryKey
    price: float
    description: Optional[str] = None


class ProductRead(ProductBase):
    id: PrimaryKey
    manufacturer: ManufacturerRead


class ProductCreate(ProductBase):
    """Schema for creating a new product."""

    pass


class ProductUpdate(FarmbaseBase):
    """Schema for updating an existing product."""

    category: Optional[ProductCategory] = None
    name: Optional[str] = None
    manufacturer_id: Optional[PrimaryKey] = None
    price: Optional[float] = None
    description: Optional[str] = None


class ProductPagination(Pagination):
    items: List[ProductRead] = []
