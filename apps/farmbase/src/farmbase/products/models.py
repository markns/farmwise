from typing import List, Optional

from sqlalchemy import Float, ForeignKey, String, Text, Integer
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
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    category: Mapped[ProductCategory] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    manufacturer_id: Mapped[int] = mapped_column(ForeignKey("manufacturer.id"), nullable=False)
    manufacturer: Mapped[Manufacturer] = relationship("Manufacturer")
    price: Mapped[float] = mapped_column(Float, nullable=False)  # TODO: this should be a time series
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    default_unit: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Relationships
    activity_associations: Mapped[list["ActivityProduct"]] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )

    # class Product(Base):
    #     __tablename__ = "product"
    #     product_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    #     product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    #     product_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    #

    def __repr__(self):
        return f"<Product(id={self.id}, product_name='{self.product_name}')>"


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
