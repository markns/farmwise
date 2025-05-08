from datetime import datetime
from typing import List, Optional

from geoalchemy2 import Geometry, WKBElement
from pydantic import field_validator
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from farmbase.database.core import Base
from farmbase.models import FarmbaseBase, Pagination, PrimaryKey, TimeStampMixin
from farmbase.organization.models import Organization
from farmbase.validators import must_not_be_blank


class Contact(Base, TimeStampMixin):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()

    # TODO: use PhoneNumber libraries for sqlalchemy and pydantic
    phone_number: Mapped[str] = mapped_column()
    # _phone_number = Column(Unicode(20))
    # country_code: Mapped[str] = mapped_column()
    # phone_number = orm.composite(SQLPhoneNumber, _phone_number, country_code)

    organization_id: Mapped[int] = mapped_column(ForeignKey(Organization.id))
    organization = relationship("Organization")

    geo_location: Mapped[WKBElement] = mapped_column(Geometry(geometry_type="POINT", srid=4326, spatial_index=True))


class ContactBase(FarmbaseBase):
    name: str
    phone_number: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        return must_not_be_blank(v)


class ContactCreate(ContactBase): ...


class ContactPatch(ContactBase):
    name: Optional[str] = None
    phone_number: Optional[str] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if v is not None:
            return must_not_be_blank(v)
        return v


class ContactRead(ContactBase):
    id: PrimaryKey
    created_at: datetime
    updated_at: datetime


class ContactPagination(Pagination):
    items: List[ContactRead] = []
