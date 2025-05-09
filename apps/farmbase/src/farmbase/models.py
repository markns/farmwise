from datetime import datetime, timedelta
from typing import Annotated
from zoneinfo import ZoneInfo

from pydantic import BaseModel, field_validator
from pydantic.fields import Field
from pydantic.types import SecretStr, constr
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, event, func
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

# pydantic type that limits the range of primary keys
PrimaryKey = Annotated[int, Field(default=None, gt=0.0, lt=2147483647.0)]
OrganizationSlug = constr(pattern=r"^[\w]+(?:_[\w]+)*$", min_length=3)


# SQLAlchemy models...
class ProjectMixin(object):
    """Project mixin"""

    @declared_attr
    def project_id(cls):  # noqa
        return Column(Integer, ForeignKey("project.id", ondelete="CASCADE"))

    @declared_attr
    def project(cls):  # noqa
        return relationship("Project")


class TimeStampMixin(object):
    """Timestamping mixin"""

    created_at = Column(DateTime, default=datetime.utcnow)
    created_at._creation_order = 9998
    updated_at = Column(DateTime, default=datetime.utcnow)
    updated_at._creation_order = 9998

    @staticmethod
    def _updated_at(mapper, connection, target):
        target.updated_at = datetime.utcnow()

    @classmethod
    def __declare_last__(cls):
        event.listen(cls, "before_update", cls._updated_at)


class ContactMixin(TimeStampMixin):
    """Contact mixin"""

    is_active = Column(Boolean, default=True)
    is_external = Column(Boolean, default=False)
    contact_type = Column(String)
    email = Column(String)
    company = Column(String)
    notes = Column(String)
    owner = Column(String)


class ResourceMixin(TimeStampMixin):
    """Resource mixin."""

    resource_type = Column(String)
    resource_id = Column(String)
    weblink = Column(String)


class EvergreenMixin(object):
    """Evergreen mixin."""

    evergreen = Column(Boolean)
    evergreen_owner = Column(String)
    evergreen_reminder_interval = Column(Integer, default=90)  # number of days
    evergreen_last_reminder_at = Column(DateTime, default=datetime.utcnow())

    @hybrid_property
    def overdue(self):
        now = datetime.utcnow()
        next_reminder = self.evergreen_last_reminder_at + timedelta(days=self.evergreen_reminder_interval)

        if now >= next_reminder:
            return True

    @overdue.expression
    def overdue(cls):
        return (
            func.date_part("day", func.now() - cls.evergreen_last_reminder_at) >= cls.evergreen_reminder_interval  # noqa
        )


class FeedbackMixin(object):
    """Feedback mixin."""

    rating = Column(String)
    feedback = Column(String)


def datetime_to_utc_str(dt: datetime) -> str:
    if not dt.tzinfo:
        dt = dt.replace(tzinfo=ZoneInfo("UTC"))

    return dt.strftime("%Y-%m-%dT%H:%M:%S%z")


# Pydantic models...
class FarmbaseBase(BaseModel):
    class Config:
        from_attributes = True
        validate_assignment = True
        arbitrary_types_allowed = True
        str_strip_whitespace = True

        json_encoders = {
            # custom output conversion for datetime
            datetime: datetime_to_utc_str,
            SecretStr: lambda v: v.get_secret_value() if v else None,
        }


class Location(BaseModel):
    latitude: float = Field(..., description="Latitude in decimal degrees (-90 to 90)")
    longitude: float = Field(..., description="Longitude in decimal degrees (-180 to 180)")

    @field_validator("latitude")
    @classmethod
    def validate_latitude(cls, value: float) -> float:
        if not -90 <= value <= 90:
            raise ValueError("Latitude must be between -90 and 90 degrees.")
        return value

    @field_validator("longitude")
    @classmethod
    def validate_longitude(cls, value: float) -> float:
        if not -180 <= value <= 180:
            raise ValueError("Longitude must be between -180 and 180 degrees.")
        return value

    def to_ewkt(self) -> str:
        """Convert to EWKT format."""
        return f"SRID=4326;POINT({self.longitude} {self.latitude})"


class Pagination(FarmbaseBase):
    items_per_page: int
    page: int
    total: int


class PrimaryKeyModel(BaseModel):
    id: PrimaryKey


# class EvergreenBase(FarmbaseBase):
#     evergreen: Optional[bool] = False
#     evergreen_owner: Optional[EmailStr]
#     evergreen_reminder_interval: Optional[int] = 90
#     evergreen_last_reminder_at: Optional[datetime] = Field(None, nullable=True)
#
#
# class ResourceBase(FarmbaseBase):
#     resource_type: Optional[str] = Field(None, nullable=True)
#     resource_id: Optional[str] = Field(None, nullable=True)
#     weblink: Optional[AnyHttpUrl] = Field(None, nullable=True)
