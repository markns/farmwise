from typing import List, Optional

from pydantic import Field

from farmbase.enums import Gender
from farmbase.models import FarmbaseBase, Pagination, PrimaryKey


class CommodityBase(FarmbaseBase):
    """Base model for Commodity data."""

    name: str = Field(description="Name of the commodity")
    classification: Optional[str] = Field(default=None, description="Classification or category of the commodity")
    grade: Optional[str] = Field(default=None, description="Grade or quality level of the commodity")
    sex: Optional[Gender] = Field(default=None, description="Sex specification for livestock commodities")


class CommodityCreate(CommodityBase):
    """Model for creating a new commodity."""

    pass


class CommodityUpdate(CommodityBase):
    """Model for updating an existing commodity."""

    name: Optional[str] = Field(default=None, description="Name of the commodity")


class CommodityRead(CommodityBase):
    """Model for reading Commodity data."""

    id: PrimaryKey = Field(description="Unique identifier of the commodity")


class CommodityPagination(Pagination):
    """Model for paginated list of commodities."""

    items: List[CommodityRead] = Field(default_factory=list, description="List of commodities in the current page")
