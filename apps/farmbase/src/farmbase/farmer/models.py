from typing import List

from pydantic import field_validator
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from farmbase.database.core import Base
from farmbase.models import FarmbaseBase, Pagination, PrimaryKey, TimeStampMixin
from farmbase.organization.models import Organization, OrganizationRead
from farmbase.validators import must_not_be_blank


class Farmer(Base, TimeStampMixin):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()

    # TODO: use PhoneNumber libraries for sqlalchemy and pydantic
    phone_number: Mapped[str] = mapped_column()
    # _phone_number = Column(Unicode(20))
    # country_code: Mapped[str] = mapped_column()
    # phone_number = orm.composite(SQLPhoneNumber, _phone_number, country_code)

    organization_id: Mapped[int] = mapped_column(ForeignKey(Organization.id))
    organization = relationship("Organization")


class FarmerBase(FarmbaseBase):
    id: PrimaryKey = None
    name: str
    phone_number: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        return must_not_be_blank(v)


class FarmerCreate(FarmerBase):
    organization: OrganizationRead


class FarmerUpdate(FarmerBase): ...


class FarmerRead(FarmerBase): ...


class FarmerPagination(Pagination):
    items: List[FarmerRead] = []
