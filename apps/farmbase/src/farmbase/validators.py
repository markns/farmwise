# validators.py
from typing import Any

from geoalchemy2 import WKBElement
from geoalchemy2.shape import to_shape
from shapely import wkt


def must_not_be_blank(v: str, field_name: str = "Field") -> str:
    """Ensure a string is not empty or only whitespace."""
    if not v.strip():
        raise ValueError(f"{field_name} must not be empty or whitespace.")
    return v


def _from_ewkt(ewkt_string) -> WKBElement:
    """Convert to EWKT format."""
    _, wkt_part = ewkt_string.split(";", 1)
    geom = wkt.loads(wkt_part)
    return geom


def validate_location(data: Any) -> Any:
    if isinstance(data, WKBElement):
        point: WKBElement = to_shape(data)
        print(f"wkb {point}")
        return {"longitude": point.x, "latitude": point.y}
    elif isinstance(data, str):
        point = _from_ewkt(data)
        print(f"str {point}")
        return {"longitude": point.x, "latitude": point.y}
    # If data is already a dictionary or another compatible type, pass it through.
    print(f"data {data}")
    return data
