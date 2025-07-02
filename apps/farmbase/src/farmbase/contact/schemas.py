from __future__ import annotations

from datetime import date
from typing import List, Optional

from pydantic import Field, field_validator

from farmbase.enums import ContactRole, Gender
from farmbase.models import FarmbaseBase, Pagination, PrimaryKey
from farmbase.organization.models import OrganizationRead
from farmbase.validators import must_not_be_blank


class ProductInterests(FarmbaseBase):
    crops: List[str]
    livestock: List[str]
    other: List[str]


class ContactBase(FarmbaseBase):
    """Base model for Contact data."""

    preferred_form_of_address: Optional[str] = Field(
        default=None, description="Preferred form of address of the contact"
    )
    gender: Optional[Gender] = Field(default=None, description="Contact's gender")
    date_of_birth: Optional[date] = Field(default=None, description="Contact's date of birth")
    estimated_age: Optional[int] = Field(default=None, description="Contact's estimated age")
    role: Optional[ContactRole] = Field(default=None, description="Role of the contact")
    experience: Optional[int] = Field(default=None, description="Contact's work experience in years")
    email: Optional[str] = Field(default=None, description="Contact's email address")
    product_interests: Optional[ProductInterests] = Field(
        default=None, description="The crops, livestock and other farm products that the contact is interested in"
    )


class ContactBaseWrite(ContactBase): ...


class ContactCreate(ContactBaseWrite):
    name: str = Field(description="The whatsapp name of the contact")
    phone_number: str = Field(description="Contact's phone number")


class ContactPatch(ContactBaseWrite):
    """Model for updating existing Contact."""

    name: Optional[str] = Field(default=None, description="Updated name of the contact")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if v is not None:
            return must_not_be_blank(v)
        return v


class ContactRead(ContactBase):
    """Model for reading Contact data."""

    id: PrimaryKey = Field(description="Unique identifier of the contact")
    name: str = Field(description="The WhatsApp name of the contact")
    phone_number: str = Field(description="Contact's phone number")
    organization: OrganizationRead = Field(description="The organization the contact belongs to")
    farms: List["FarmSummary"] = Field(
        default_factory=list,
        description="List of farms associated with the contact",
    )


class ContactPagination(Pagination):
    """Model for paginated list of contacts."""

    items: List[ContactRead] = Field(default_factory=list, description="List of contacts in the current page")


class ContactConsentBase(FarmbaseBase):
    """Base model for ContactConsent data."""

    consent_type: str = Field(description="Type of consent (e.g., 'data_processing', 'marketing', 'communication')")
    consent_given: bool = Field(description="Whether consent was given or not")
    consent_version: str = Field(description="Version of the consent terms")


class ContactConsentCreate(ContactConsentBase):
    """Model for creating new ContactConsent."""

    pass


class ContactConsentRead(ContactConsentBase):
    """Model for reading ContactConsent data."""

    id: PrimaryKey = Field(description="Unique identifier of the consent record")
    contact_id: int = Field(description="ID of the contact this consent belongs to")
