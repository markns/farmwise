from __future__ import annotations

from datetime import datetime
from typing import Callable, Optional

from geoalchemy2 import Geometry
from geoalchemy2.elements import WKBElement
from sqlalchemy import (
    JSON,
    BigInteger,
    CheckConstraint,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.schema import Computed
from sqlalchemy_utils.types.ltree import LtreeType

from farmbase.database.core import Base
from farmbase.enums import FarmbaseEnum

# ————————————————————————————————————————
# Enums
# ————————————————————————————————————————


class ListingStatus(FarmbaseEnum):
    ACTIVE = "active"
    SOLD = "sold"
    EXPIRED = "expired"
    HIDDEN = "hidden"


# ————————————————————————————————————————
# Category tree
# ————————————————————————————————————————


class Category(Base):
    __tablename__ = "category"
    __table_args__ = {"schema": "farmbase_core"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    parent_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("category.id", ondelete="CASCADE"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    # LTree path makes subtree queries super fast
    path: Mapped[str] = mapped_column(LtreeType)

    parent: Mapped[Optional["Category"]] = relationship(remote_side=[id], back_populates="children")
    children: Mapped[list["Category"]] = relationship(back_populates="parent", cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint("parent_id", "name"),)

    def __repr__(self) -> str:
        return f"<Category(id={self.id}, name='{self.name}')>"


# ————————————————————————————————————————
# Listing & related artefacts
# ————————————————————————————————————————


class Listing(Base):
    __tablename__ = "listing"
    __table_args__ = {"schema": "farmbase_core"}

    # primary data -----------------------------------------------------------
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    tenant_key: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    contact_id: Mapped[int] = mapped_column(Integer, nullable=False)
    #
    #  ^^^ no ForeignKey – the target table lives in tenant_key.contact
    #

    category_id: Mapped[Optional[int]] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description_md: Mapped[str] = mapped_column(Text, nullable=False)

    price_cents: Mapped[Optional[int]] = mapped_column(Integer, CheckConstraint("price_cents >= 0"))
    currency_code: Mapped[str] = mapped_column(String(3), default="USD")
    status: Mapped[ListingStatus] = mapped_column(default=ListingStatus.ACTIVE, nullable=False, index=True)
    expires_at: Mapped[Optional[datetime]]

    location: Mapped[Optional[WKBElement]] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326, spatial_index=True), nullable=True
    )

    fulltext: Mapped[str] = mapped_column(
        TSVECTOR,
        Computed(
            "setweight(to_tsvector('simple', coalesce(title,'')), 'A') || "
            "setweight(to_tsvector('simple', coalesce(description_md,'')), 'B')",
            persisted=True,
        ),
    )

    __table_args__ = (CheckConstraint("(price_cents IS NOT NULL) OR (status = 'hidden')"),)

    # relationships inside the core schema
    images: Mapped[list["ListingImage"]] = relationship(back_populates="listing", cascade="all, delete-orphan")
    reports: Mapped[list["Report"]] = relationship(back_populates="listing", cascade="all, delete-orphan")
    audits: Mapped[list["AuditListingEdit"]] = relationship(back_populates="listing", cascade="all, delete-orphan")

    # ------- helper: fetch the Contact on demand ---------------------------
    def fetch_contact(self, tenant_session_factory: Callable[[str], "Session"]) -> "Contact | None":
        """
        Convenience method:
            contact = listing.fetch_contact(session_for_tenant)
        where `session_for_tenant(tenant_key)` returns a Session bound to the
        proper tenant schema.
        """

        with tenant_session_factory(self.tenant_key) as tsess:
            return tsess.get(Contact, self.contact_id)  # type: ignore[name-defined]

    # repr
    def __repr__(self) -> str:
        return f"<Listing(id={self.id}, tenant='{self.tenant_key}', title='{self.title[:24]}')>"


class ListingImage(Base):
    __tablename__ = "listing_image"
    __table_args__ = {"schema": "farmbase_core"}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    listing_id: Mapped[int] = mapped_column(ForeignKey("listing.id", ondelete="CASCADE"))
    listing: Mapped["Listing"] = relationship(back_populates="images")

    image_url: Mapped[str] = mapped_column(String, nullable=False)
    position: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    __table_args__ = (UniqueConstraint("listing_id", "position"),)

    def __repr__(self) -> str:
        return f"<ListingImage(id={self.id}, url='{self.image_url}')>"


# ————————————————————————————————————————
# Social interactions
# ————————————————————————————————————————


class Report(Base):
    __tablename__ = "report"
    __table_args__ = {"schema": "farmbase_core"}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    tenant_key: Mapped[str] = mapped_column(String(64), nullable=False)
    reporter_id: Mapped[int] = mapped_column(Integer, nullable=False)

    listing_id: Mapped[int] = mapped_column(BigInteger, index=True)

    reason_text: Mapped[str] = mapped_column(Text, nullable=False)

    listing: Mapped["Listing"] = relationship(
        back_populates="reports",
        primaryjoin="Report.listing_id == Listing.id",
        viewonly=True,
    )

    def fetch_reporter(self, factory):
        with factory(self.tenant_key) as s:
            return s.get(Contact, self.reporter_id)  # type: ignore[name-defined]


class AuditListingEdit(Base):
    __tablename__ = "audit_listing_edit"
    __table_args__ = {"schema": "farmbase_core"}

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    tenant_key: Mapped[str] = mapped_column(String(64), nullable=False)
    editor_id: Mapped[int] = mapped_column(Integer, nullable=False)

    listing_id: Mapped[int] = mapped_column(BigInteger, index=True)

    old_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    new_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    edited_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())

    listing: Mapped["Listing"] = relationship(
        back_populates="audits",
        primaryjoin="AuditListingEdit.listing_id == Listing.id",
        viewonly=True,
    )

    def fetch_editor(self, factory):
        with factory(self.tenant_key) as s:
            return s.get(Contact, self.editor_id)  # type: ignore[name-defined]


# ————————————————————————————————————————
# Patch relationships onto your Contact model
# ————————————————————————————————————————
# NB: This assumes `Contact` is imported *after* the classes above
try:
    from yourproject.models import Contact  # adjust import path to suit
except ImportError:  # pragma: no cover
    pass
else:
    Contact.listings = relationship("Listing", back_populates="contact", cascade="all, delete-orphan")
    Contact.favourites = relationship("Favourite", back_populates="contact", cascade="all, delete-orphan")


if __name__ == "__main__":
    # factory that returns a Session bound to the tenant’s schema
    def session_for_tenant(tenant_key: str) -> Session:
        eng = TENANT_ENGINES[tenant_key]  # cache of Engine objects
        return Session(eng)

    # 1. load from the shared "core" schema
    with Session(CORE_ENGINE) as core_sess:
        listing = core_sess.get(Listing, 123)

        # 2. hop to the tenant to get its user
        seller = listing.fetch_contact(session_for_tenant)
        print(listing.title, "posted by", seller.name)
