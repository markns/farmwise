from __future__ import annotations

import datetime
from typing import Optional

from geoalchemy2 import Geometry
from sqlalchemy import (
    DECIMAL,
    TEXT,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.ext.associationproxy import association_proxy  # For simpler many-to-many access if needed
from sqlalchemy.orm import Mapped, mapped_column, relationship

from farmbase.contact.models import Contact
from farmbase.database.core import Base
from farmbase.products.models import Product


class Platform(Base):
    __tablename__ = "platform"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)  # Changed platform_id to id
    platform_name: Mapped[str] = mapped_column(String(50), nullable=False)

    # Relationships (collection names remain plural)
    fields_added: Mapped[list["Field"]] = relationship(back_populates="added_on_platform")
    boundary_activities: Mapped[list["BoundaryDefinitionActivity"]] = relationship(back_populates="platform")

    def __repr__(self):
        return f"<Platform(id={self.id}, platform_name='{self.platform_name}')>"  # Changed platform_id to id


class Commodity(Base):
    __tablename__ = "commodity"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)  # Changed commodity_id to id
    commodity_name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    # Relationships
    plantings: Mapped[list["Planting"]] = relationship(back_populates="commodity")

    def __repr__(self):
        return f"<Commodity(id={self.id}, commodity_name='{self.commodity_name}')>"  # Changed commodity_id to id


class Farm(Base):
    __tablename__ = "farm"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)  # Changed farm_id to id
    farm_name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str | None] = mapped_column(TEXT, nullable=True)
    date_registered: Mapped[datetime.datetime | None] = mapped_column(DateTime, nullable=True)

    # Relationships
    fields: Mapped[list["Field"]] = relationship(back_populates="farm")
    field_groups: Mapped[list["FieldGroup"]] = relationship(back_populates="farm")
    storage_locations: Mapped[list["StorageLocation"]] = relationship(back_populates="farm")
    notes: Mapped[list["Note"]] = relationship(back_populates="farm")
    contact_associations: Mapped[list["FarmContact"]] = relationship(
        back_populates="farm", cascade="all, delete-orphan"
    )

    contacts = association_proxy("contact_associations", "contact")

    def __repr__(self):
        return f"<Farm(id={self.id}, farm_name='{self.farm_name}')>"  # Changed farm_id to id


class ActivityType(Base):
    __tablename__ = "activity_type"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)  # Changed activity_type_id to id
    activity_type_name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(TEXT, nullable=True)

    # Relationships
    farm_activities: Mapped[list["FarmActivity"]] = relationship(back_populates="activity_type")

    def __repr__(self):
        return f"<ActivityType(id={self.id}, activity_type_name='{self.activity_type_name}')>"  # Changed activity_type_id to id


# --- Dependent Entity Tables ---


class FieldGroup(Base):
    __tablename__ = "field_group"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)  # Changed field_group_id to id
    farm_id: Mapped[int] = mapped_column(ForeignKey(Farm.id), nullable=False)  # Changed Farm.farm_id to Farm.id
    group_name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(TEXT, nullable=True)

    # Relationships
    farm: Mapped["Farm"] = relationship(back_populates="field_groups")
    member_associations: Mapped[list["FieldGroupMember"]] = relationship(
        back_populates="field_group", cascade="all, delete-orphan"
    )

    fields: Mapped[list["Field"]] = relationship(
        secondary="field_group_member", back_populates="field_groups", viewonly=True
    )

    def __repr__(self):
        return f"<FieldGroup(id={self.id}, group_name='{self.group_name}')>"  # Changed field_group_id to id


class Field(Base):
    __tablename__ = "field"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    farm_id: Mapped[int] = mapped_column(ForeignKey(Farm.id), nullable=False)
    field_name: Mapped[str] = mapped_column(String(255), nullable=False)
    boundary_geometry: Mapped[Optional[str]] = mapped_column(
        Geometry(geometry_type="POLYGON", srid=4326, from_text="ST_GeomFromEWKT", name="geometry"), nullable=True
    )  # Used Optional
    total_physical_acres: Mapped[Optional[float]] = mapped_column(DECIMAL(10, 2), nullable=True)  # Used Optional
    added_on_platform_id: Mapped[int] = mapped_column(ForeignKey(Platform.id), nullable=False)
    date_created: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)
    last_modified: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )

    # Relationships
    farm: Mapped["Farm"] = relationship(back_populates="fields")
    added_on_platform: Mapped["Platform"] = relationship(back_populates="fields_added")
    field_group_associations: Mapped[list["FieldGroupMember"]] = relationship(
        back_populates="field", cascade="all, delete-orphan"
    )
    plantings: Mapped[list["Planting"]] = relationship(back_populates="field", cascade="all, delete-orphan")
    boundary_definition_activities: Mapped[list["BoundaryDefinitionActivity"]] = relationship(
        back_populates="field", cascade="all, delete-orphan"
    )
    notes: Mapped[list["Note"]] = relationship(back_populates="field", cascade="all, delete-orphan")
    farm_activities: Mapped[list["FarmActivity"]] = relationship(back_populates="field", cascade="all, delete-orphan")

    field_groups: Mapped[list["FieldGroup"]] = relationship(
        secondary="field_group_member", back_populates="fields", viewonly=True
    )

    def __repr__(self):
        return f"<Field(id={self.id}, field_name='{self.field_name}')>"  # Changed field_id to id


class StorageLocation(Base):
    __tablename__ = "storage_location"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    farm_id: Mapped[int] = mapped_column(ForeignKey(Farm.id), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # Used Optional
    capacity: Mapped[Optional[float]] = mapped_column(DECIMAL(12, 2), nullable=True)  # Used Optional
    capacity_unit: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # Used Optional
    location_address: Mapped[Optional[str]] = mapped_column(TEXT, nullable=True)  # Used Optional

    # Relationships
    farm: Mapped["Farm"] = relationship(back_populates="storage_locations")
    harvest_loads_destination: Mapped[list["HarvestLoad"]] = relationship(back_populates="destination_storage_location")

    def __repr__(self):
        return f"<StorageLocation(id={self.id}, name='{self.name}')>"  # Changed storage_location_id to id


class Planting(Base):
    __tablename__ = "planting"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    field_id: Mapped[int] = mapped_column(ForeignKey(Field.id), nullable=False)
    commodity_id: Mapped[int] = mapped_column(ForeignKey(Commodity.id), nullable=False)
    planting_year: Mapped[int] = mapped_column(Integer, nullable=False)
    acres_planted: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    planting_date: Mapped[Optional[datetime.date]] = mapped_column(Date, nullable=True)  # Used Optional
    harvest_date: Mapped[Optional[datetime.date]] = mapped_column(Date, nullable=True)  # Used Optional
    total_actual_yield: Mapped[Optional[float]] = mapped_column(DECIMAL(12, 2), nullable=True)  # Used Optional
    actual_yield_per_acre: Mapped[Optional[float]] = mapped_column(DECIMAL(10, 2), nullable=True)  # Used Optional
    yield_unit: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # Used Optional
    yield_data_source: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # Used Optional
    notes: Mapped[Optional[str]] = mapped_column(TEXT, nullable=True)  # Used Optional
    date_recorded: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    field: Mapped["Field"] = relationship(back_populates="plantings")
    commodity: Mapped["Commodity"] = relationship(back_populates="plantings")
    farm_activities: Mapped[list["FarmActivity"]] = relationship(
        back_populates="planting", cascade="all, delete-orphan"
    )
    notes: Mapped[list["Note"]] = relationship(back_populates="planting", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Planting(id={self.id}, field_id={self.field_id}, commodity_id={self.commodity_id})>"  # Changed planting_id to id


class BoundaryDefinitionActivity(Base):
    __tablename__ = "boundary_definition_activity"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)  # Changed activity_id to id
    field_id: Mapped[int] = mapped_column(ForeignKey(Field.id), nullable=False)  # Changed Field.field_id to Field.id
    activity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    platform_id: Mapped[int] = mapped_column(
        ForeignKey(Platform.id), nullable=False
    )  # Changed Platform.platform_id to Platform.id
    activity_timestamp: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)
    notes: Mapped[str | None] = mapped_column(TEXT, nullable=True)

    # Relationships
    field: Mapped["Field"] = relationship(back_populates="boundary_definition_activities")
    platform: Mapped["Platform"] = relationship(back_populates="boundary_activities")

    def __repr__(self):
        return f"<BoundaryDefinitionActivity(id={self.id}, field_id={self.field_id})>"  # Changed activity_id to id


class FarmActivity(Base):
    __tablename__ = "farm_activity"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    field_id: Mapped[Optional[int]] = mapped_column(ForeignKey(Field.id), nullable=True)  # Used Optional for FK
    planting_id: Mapped[Optional[int]] = mapped_column(ForeignKey(Planting.id), nullable=True)  # Used Optional for FK
    activity_type_id: Mapped[int] = mapped_column(ForeignKey(ActivityType.id), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    activity_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(TEXT, nullable=True)  # Used Optional
    date_logged: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    field: Mapped[Optional["Field"]] = relationship(back_populates="farm_activities")  # Changed to Optional["Field"]
    planting: Mapped[Optional["Planting"]] = relationship(
        back_populates="farm_activities"
    )  # Changed to Optional["Planting"]
    activity_type: Mapped["ActivityType"] = relationship(back_populates="farm_activities")
    product_associations: Mapped[list["ActivityProduct"]] = relationship(
        back_populates="farm_activity", cascade="all, delete-orphan"
    )
    harvest_loads: Mapped[list["HarvestLoad"]] = relationship(
        back_populates="farm_activity", cascade="all, delete-orphan"
    )

    products = association_proxy("product_associations", "product")

    def __repr__(self):
        return f"<FarmActivity(id={self.id}, activity_type_id={self.activity_type_id})>"


class HarvestLoad(Base):
    __tablename__ = "harvest_load"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    farm_activity_id: Mapped[int] = mapped_column(ForeignKey(FarmActivity.id), nullable=False)
    load_timestamp: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.datetime.utcnow
    )
    quantity: Mapped[float] = mapped_column(DECIMAL(12, 2), nullable=False)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)
    moisture_content: Mapped[Optional[float]] = mapped_column(DECIMAL(5, 2), nullable=True)  # Used Optional
    ticket_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # Used Optional
    destination_storage_location_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey(StorageLocation.id), nullable=True
    )  # Used Optional for FK
    destination_buyer: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # Used Optional
    contact_id_person_involved: Mapped[Optional[int]] = mapped_column(
        ForeignKey(Contact.id), nullable=True
    )  # Used Optional for FK
    notes: Mapped[Optional[str]] = mapped_column(TEXT, nullable=True)  # Used Optional

    __table_args__ = (
        CheckConstraint(
            "(destination_storage_location_id IS NOT NULL OR destination_buyer IS NOT NULL)",
            name="chk_harvest_load_destination",
        ),
    )

    # Relationships
    farm_activity: Mapped["FarmActivity"] = relationship(back_populates="harvest_loads")
    destination_storage_location: Mapped[Optional["StorageLocation"]] = relationship(
        back_populates="harvest_loads_destination"
    )  # Changed to Optional["StorageLocation"]
    person_involved_contact: Mapped[Optional["Contact"]] = relationship(
        back_populates="harvest_loads_involved"
    )  # Changed to Optional["Contact"]

    def __repr__(self):
        return f"<HarvestLoad(id={self.id}, farm_activity_id={self.farm_activity_id})>"  # Changed harvest_load_id to id


class Note(Base):
    __tablename__ = "note"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    field_id: Mapped[Optional[int]] = mapped_column(ForeignKey(Field.id), nullable=True)  # Used Optional for FK
    farm_id: Mapped[int] = mapped_column(ForeignKey(Farm.id), nullable=False)
    planting_id: Mapped[Optional[int]] = mapped_column(ForeignKey(Planting.id), nullable=True)  # Used Optional for FK
    note_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)
    note_text: Mapped[str] = mapped_column(TEXT, nullable=False)
    location_coordinates: Mapped[Optional[str]] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326, from_text="ST_GeomFromEWKT", name="geometry"), nullable=True
    )  # Used Optional
    image_path: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)  # Used Optional
    contact_id_created_by: Mapped[Optional[int]] = mapped_column(
        ForeignKey(Contact.id), nullable=True
    )  # Used Optional for FK
    date_created: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)
    tags: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # Used Optional

    # Relationships
    field: Mapped[Optional["Field"]] = relationship(back_populates="notes")  # Changed to Optional["Field"]
    farm: Mapped["Farm"] = relationship(back_populates="notes")
    planting: Mapped[Optional["Planting"]] = relationship(back_populates="notes")  # Changed to Optional["Planting"]
    created_by_contact: Mapped[Optional["Contact"]] = relationship(
        back_populates="notes_created"
    )  # Changed to Optional["Contact"]

    def __repr__(self):
        return f"<Note(id={self.id}, note_date={self.note_date})>"


# --- Association Tables (Defined after entities they refer to) ---


class FieldGroupMember(Base):
    __tablename__ = "field_group_member"
    field_id: Mapped[int] = mapped_column(ForeignKey(Field.id), primary_key=True)  # Changed Field.field_id to Field.id
    field_group_id: Mapped[int] = mapped_column(
        ForeignKey(FieldGroup.id), primary_key=True
    )  # Changed FieldGroup.field_group_id to FieldGroup.id

    # Relationships to access the objects directly from the association object (optional)
    field: Mapped["Field"] = relationship(back_populates="field_group_associations")
    field_group: Mapped["FieldGroup"] = relationship(back_populates="member_associations")

    def __repr__(self):
        return f"<FieldGroupMember(field_id={self.field_id}, field_group_id={self.field_group_id})>"


class FarmContact(Base):
    __tablename__ = "farm_contact"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)  # Changed farm_contact_id to id
    farm_id: Mapped[int] = mapped_column(ForeignKey(Farm.id), nullable=False)  # Changed Farm.farm_id to Farm.id
    contact_id: Mapped[int] = mapped_column(
        ForeignKey(Contact.id), nullable=False
    )  # Changed Contact.contact_id to Contact.id
    role: Mapped[str] = mapped_column(String(100), nullable=False)

    __table_args__ = (UniqueConstraint("farm_id", "contact_id", "role", name="uq_farm_contact_role"),)

    # Relationships
    farm: Mapped["Farm"] = relationship(back_populates="contact_associations")
    contact: Mapped["Contact"] = relationship(back_populates="farm_associations")

    def __repr__(self):
        return f"<FarmContact(id={self.id}, farm_id={self.farm_id}, contact_id={self.contact_id}, role='{self.role}')>"  # Changed farm_contact_id to id


class ActivityProduct(Base):
    __tablename__ = "activity_product"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    farm_activity_id: Mapped[int] = mapped_column(ForeignKey(FarmActivity.id), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey(Product.id), nullable=False)
    quantity_applied: Mapped[Optional[float]] = mapped_column(DECIMAL(10, 2), nullable=True)  # Used Optional
    application_rate: Mapped[Optional[float]] = mapped_column(DECIMAL(10, 2), nullable=True)  # Used Optional
    application_rate_unit: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # Used Optional
    cost: Mapped[Optional[float]] = mapped_column(DECIMAL(10, 2), nullable=True)  # Used Optional

    # Relationships
    farm_activity: Mapped["FarmActivity"] = relationship(back_populates="product_associations")
    product: Mapped["Product"] = relationship(back_populates="activity_associations")

    def __repr__(self):
        return f"<ActivityProduct(id={self.id}, farm_activity_id={self.farm_activity_id}, product_id={self.product_id})>"  # Changed activity_product_id to id
