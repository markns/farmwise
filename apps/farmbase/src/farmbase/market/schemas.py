from datetime import date
from typing import List, Optional

from pydantic import Field

from farmbase.commodity.schemas import CommodityRead
from farmbase.models import FarmbaseBase, Pagination, PrimaryKey


class MarketBase(FarmbaseBase):
    """Base model for Market data."""

    name: str = Field(description="Name of the market")
    # Note: location is a PostGIS geometry field, so we'll handle it as optional coordinates


class MarketCreate(MarketBase):
    """Model for creating a new market."""

    pass


class MarketUpdate(MarketBase):
    """Model for updating an existing market."""

    name: Optional[str] = Field(default=None, description="Name of the market")


class MarketRead(MarketBase):
    """Model for reading Market data."""

    id: PrimaryKey = Field(description="Unique identifier of the market")


class MarketPagination(Pagination):
    """Model for paginated list of markets."""

    items: List[MarketRead] = Field(default_factory=list, description="List of markets in the current page")


class MarketPriceBase(FarmbaseBase):
    """Base model for MarketPrice data."""

    price_date: Optional[date] = Field(default=None, description="Date of the price record")
    supply_volume: Optional[float] = Field(default=None, description="Volume of supply available")
    wholesale_price: Optional[float] = Field(default=None, description="Wholesale price")
    wholesale_unit: Optional[str] = Field(default=None, description="Unit for wholesale price (e.g., 'kg', 'ton')")
    wholesale_ccy: Optional[str] = Field(default=None, description="Currency code for wholesale price")
    retail_price: Optional[float] = Field(default=None, description="Retail price")
    retail_unit: Optional[str] = Field(default=None, description="Unit for retail price (e.g., 'kg', 'ton')")
    retail_ccy: Optional[str] = Field(default=None, description="Currency code for retail price")


class MarketPriceCreate(MarketPriceBase):
    """Model for creating a new market price."""

    market_id: int = Field(description="ID of the market")
    commodity_id: int = Field(description="ID of the commodity")


class MarketPriceUpdate(MarketPriceBase):
    """Model for updating an existing market price."""

    pass


class MarketPriceRead(MarketPriceBase):
    """Model for reading MarketPrice data."""

    id: PrimaryKey = Field(description="Unique identifier of the market price")
    market: MarketRead = Field(description="Market information")
    commodity: CommodityRead = Field(description="Commodity information")
    # We'll use a simplified commodity representation to avoid circular imports
    # commodity_name: str = Field(description="Name of the commodity")
    # commodity_classification: Optional[str] = Field(default=None, description="Classification of the commodity")
    # commodity_grade: Optional[str] = Field(default=None, description="Grade of the commodity")


class MarketPricePagination(Pagination):
    """Model for paginated list of market prices."""

    items: List[MarketPriceRead] = Field(default_factory=list, description="List of market prices in the current page")
