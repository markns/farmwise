from __future__ import annotations

from datetime import date

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import Mapped, mapped_column, relationship

from farmbase.database.core import Base
from farmbase.enums import ContactRole, Gender
from farmbase.organization.models import Organization

# TODO: use this pattern to add other contact types. eg. farmers
# https://docs.sqlalchemy.org/en/20/orm/queryguide/_inheritance_setup.html


class Contact(Base):
    __tablename__ = "contact"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone_number: Mapped[str | None] = mapped_column(String(50), unique=True, nullable=True)
    preferred_form_of_address: Mapped[str] = mapped_column(String(255), nullable=True)
    gender: Mapped[Gender] = mapped_column(SqlEnum(Gender, name="gender_enum"), nullable=True)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=True)
    estimated_age: Mapped[int] = mapped_column(Integer, nullable=True)
    # TODO: we might want to change Contact to a hierarchy in future.
    role: Mapped[ContactRole] = mapped_column(SqlEnum(ContactRole, name="contact_role_enum"), nullable=True)
    experience: Mapped[int] = mapped_column(Integer, nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)

    # Add JSON field for product interests
    product_interests: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)

    # Relationships
    organization_id: Mapped[int] = mapped_column(ForeignKey(Organization.id))
    organization = relationship("Organization")

    farm_associations: Mapped[list["FarmContact"]] = relationship(
        back_populates="contact", cascade="all, delete-orphan"
    )
    notes_created: Mapped[list["Note"]] = relationship(back_populates="created_by_contact")
    harvest_loads_involved: Mapped[list["HarvestLoad"]] = relationship(back_populates="person_involved_contact")

    farms = association_proxy("farm_associations", "farm")
    consents: Mapped[list["ContactConsent"]] = relationship(
        back_populates="contact", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Contact(id={self.id}, name='{self.name}')>"


class ContactConsent(Base):
    __tablename__ = "contact_consents"

    id: Mapped[int] = mapped_column(primary_key=True)
    contact_id: Mapped[int] = mapped_column(ForeignKey("contact.id", ondelete="CASCADE"), nullable=False)

    consent_type: Mapped[str] = mapped_column(String(length=100), nullable=False)
    consent_given: Mapped[bool] = mapped_column(Boolean, nullable=False)
    consent_version: Mapped[str] = mapped_column(String(length=50), nullable=False)

    contact: Mapped["Contact"] = relationship(back_populates="consents")


