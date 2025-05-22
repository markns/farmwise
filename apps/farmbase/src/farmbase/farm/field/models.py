from __future__ import annotations

import datetime
from typing import Optional

from geoalchemy2 import Geometry
from sqlalchemy import DECIMAL, TEXT, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from farmbase.database.core import Base
from farmbase.farm.activity.models import FarmActivity

# from farmbase.farm.models import Farm
from farmbase.farm.planting.models import Planting
from farmbase.farm.platform.models import Platform


class FieldGroup(Base):
    __tablename__ = "field_group"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)  # Changed field_group_id to id
    farm_id: Mapped[int] = mapped_column(ForeignKey("farm.id"), nullable=False)  # Changed Farm.farm_id to Farm.id
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
    farm_id: Mapped[int] = mapped_column(ForeignKey("farm.id"), nullable=False)
    field_name: Mapped[str] = mapped_column(String(255), nullable=False)
    boundary_geometry: Mapped[Optional[str]] = mapped_column(
        Geometry(geometry_type="POLYGON", srid=4326, from_text="ST_GeomFromEWKT", name="geometry"), nullable=True
    )
    total_physical_acres: Mapped[Optional[float]] = mapped_column(DECIMAL(10, 2), nullable=True)
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
