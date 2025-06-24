from __future__ import annotations

from typing import List, Optional

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from farmbase.database.core import Base
from farmbase.enums import FarmbaseEnum
from farmbase.models import TimeStampMixin

# ————————————————————————————————————————
# Enums
# ————————————————————————————————————————


class EventCategory(FarmbaseEnum):
    """Agricultural event categories"""

    FERTILIZATION_CONVENTIONAL = "fertilization_conventional"
    FERTILIZATION_ORGANIC = "fertilization_organic"
    FIELD_PREPARATION = "field_preparation"
    SITE_SELECTION = "site_selection"
    PLANTING = "planting"
    PLANT_SELECTION = "plant_selection"
    IRRIGATION = "irrigation"
    WEEDING = "weeding"
    MONITORING = "monitoring"
    PLANT_TRAINING = "plant_training"
    PREVENTIVE_MEASURES = "preventive_measures"
    CHEMICAL_PLANT_PROTECTION = "chemical_plant_protection"
    BIOLOGICAL_PLANT_PROTECTION = "biological_plant_protection"
    HARVESTING = "harvesting"
    POST_HARVEST = "post_harvest"
    AWARENESS = "awareness"
    BOARDING = "boarding"


class EventType(FarmbaseEnum):
    """Agricultural event types"""

    ADVICE = "advice"
    HINT = "hint"
    PROCEDURE = "procedure"


class PathogenClass(FarmbaseEnum):
    """Pathogen classification types"""

    FUNGI = "fungi"
    BACTERIA = "bacteria"
    VIRUS = "virus"
    INSECT = "insect"
    MITE = "mite"
    DEFICIENCY = "deficiency"
    WEED = "weed"
    OTHERS = "others"
    ADDITIONAL = "additional"


class SpreadRisk(FarmbaseEnum):
    """Pathogen spread risk levels"""

    LOW = "Low"
    INTERMEDIATE = "Intermediate"
    HIGH = "High"


class GrowthStage(FarmbaseEnum):
    """Crop growth stages"""

    SEEDLING = "seedling"
    VEGETATIVE = "vegetative"
    FLOWERING = "flowering"
    FRUITING = "fruiting"
    HARVESTING = "harvesting"


class CultivationType(FarmbaseEnum):
    """Crop cultivation types"""

    DIRECT_SEEDING = "direct_seeding"
    TRANSPLANTED = "transplanted"


class LaborLevel(FarmbaseEnum):
    """Labor requirement levels"""

    LOW = "low"
    INTERMEDIATE = "intermediate"
    HIGH = "high"


class WateringLevel(FarmbaseEnum):
    """Watering requirement levels"""

    LOW = "low"
    INTERMEDIATE = "intermediate"
    HIGH = "high"


# ————————————————————————————————————————
# Association Tables
# ————————————————————————————————————————

# Event-Pathogen association (prevent_pathogens)
event_pathogen_association = Table(
    "event_pathogen",
    Base.metadata,
    Column("event_id", String, ForeignKey("farmbase_core.event.id", ondelete="CASCADE")),
    Column("pathogen_id", Integer, ForeignKey("farmbase_core.pathogen.id", ondelete="CASCADE")),
    schema="farmbase_core",
)

# Event-Crop association (host_ids)
event_crop_association = Table(
    "event_crop",
    Base.metadata,
    Column("event_id", String, ForeignKey("farmbase_core.event.id", ondelete="CASCADE")),
    Column("crop_id", String, ForeignKey("farmbase_core.crop.host_id", ondelete="CASCADE")),
    schema="farmbase_core",
)

# Pathogen-Crop association (host_ids)
pathogen_crop_association = Table(
    "pathogen_crop",
    Base.metadata,
    Column("pathogen_id", Integer, ForeignKey("farmbase_core.pathogen.id", ondelete="CASCADE")),
    Column("crop_id", String, ForeignKey("farmbase_core.crop.host_id", ondelete="CASCADE")),
    schema="farmbase_core",
)

# Pathogen-Stage association
pathogen_stage_association = Table(
    "pathogen_stage",
    Base.metadata,
    Column("pathogen_id", Integer, ForeignKey("farmbase_core.pathogen.id", ondelete="CASCADE")),
    Column("stage", String),  # Store stage as string directly
    schema="farmbase_core",
)


# ————————————————————————————————————————
# Main Models
# ————————————————————————————————————————


class Crop(Base, TimeStampMixin):
    """Crop cultivation parameters from"""

    __tablename__ = "crop"
    __table_args__ = {"schema": "farmbase_core"}

    host_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    crop_cycle_length_min: Mapped[int] = mapped_column(Integer, nullable=False)
    crop_cycle_length_max: Mapped[int] = mapped_column(Integer, nullable=False)
    cultivation_type: Mapped[CultivationType] = mapped_column(nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    labor: Mapped[LaborLevel] = mapped_column(nullable=False)
    watering: Mapped[WateringLevel] = mapped_column(nullable=False)

    # Nutrient requirements (kg/ha)
    n_opt: Mapped[int] = mapped_column(Integer, nullable=False, comment="Nitrogen kg/ha")
    p_opt: Mapped[int] = mapped_column(Integer, nullable=False, comment="Phosphorus kg/ha")
    k_opt: Mapped[int] = mapped_column(Integer, nullable=False, comment="Potassium kg/ha")

    # Soil requirements
    ph_from: Mapped[float] = mapped_column(Float, nullable=False)
    ph_to: Mapped[float] = mapped_column(Float, nullable=False)
    soil_description: Mapped[Optional[str]] = mapped_column(Text)

    # Temperature requirements (Celsius)
    temp_day_growth_from: Mapped[int] = mapped_column(Integer, nullable=False)
    temp_day_growth_to: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relationships
    events: Mapped[List["Event"]] = relationship(secondary=event_crop_association, back_populates="crops")
    pathogens: Mapped[List["Pathogen"]] = relationship(secondary=pathogen_crop_association, back_populates="crops")
    cycles: Mapped[List["CropCycle"]] = relationship(back_populates="crop")

    def __repr__(self) -> str:
        return f"<Crop(host_id='{self.host_id}', cultivation_type='{self.cultivation_type}')>"


class Pathogen(Base, TimeStampMixin):
    """Plant pathogen information from"""

    __tablename__ = "pathogen"
    __table_args__ = {"schema": "farmbase_core"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    name_en: Mapped[Optional[str]] = mapped_column(String(255))
    scientific_name: Mapped[Optional[str]] = mapped_column(String(255))
    pathogen_class: Mapped[PathogenClass] = mapped_column(nullable=False)

    severity: Mapped[int] = mapped_column(Integer, nullable=False, comment="0-2 severity scale")
    spread_risk: Mapped[SpreadRisk] = mapped_column(nullable=False)

    # Content fields
    symptoms: Mapped[Optional[str]] = mapped_column(Text)
    trigger: Mapped[Optional[str]] = mapped_column(Text)
    chemical_treatment: Mapped[Optional[str]] = mapped_column(Text)
    alternative_treatment: Mapped[Optional[str]] = mapped_column(Text)
    preventive_measures: Mapped[Optional[List[str]]] = mapped_column(JSON)
    bullet_points: Mapped[Optional[List[str]]] = mapped_column(JSON)

    # Metadata
    default_image: Mapped[Optional[str]] = mapped_column(String(255))
    eppo: Mapped[Optional[str]] = mapped_column(String(50), comment="EPPO code")
    is_activated: Mapped[bool] = mapped_column(Boolean, default=True)
    translated: Mapped[bool] = mapped_column(Boolean, default=False)
    version_number: Mapped[Optional[int]] = mapped_column(Integer)

    # Relationships
    crops: Mapped[List["Crop"]] = relationship(secondary=pathogen_crop_association, back_populates="pathogens")
    events: Mapped[List["Event"]] = relationship(
        secondary=event_pathogen_association, back_populates="prevent_pathogens"
    )
    images: Mapped[List["PathogenImage"]] = relationship(back_populates="pathogen", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Pathogen(id={self.id}, name='{self.name}', class='{self.pathogen_class}')>"


class PathogenImage(Base, TimeStampMixin):
    """Pathogen image metadata"""

    __tablename__ = "pathogen_image"
    __table_args__ = {"schema": "farmbase_core"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pathogen_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("farmbase_core.pathogen.id", ondelete="CASCADE"), nullable=False
    )

    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[Optional[str]] = mapped_column(String(500))
    caption: Mapped[Optional[str]] = mapped_column(Text)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    pathogen: Mapped["Pathogen"] = relationship(back_populates="images")

    def __repr__(self) -> str:
        return f"<PathogenImage(id={self.id}, file_name='{self.file_name}')>"


class Event(Base, TimeStampMixin):
    """Agricultural events and advice from"""

    __tablename__ = "event"
    __table_args__ = {"schema": "farmbase_core"}

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    identifier: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    nutshell: Mapped[Optional[str]] = mapped_column(Text)

    event_category: Mapped[EventCategory] = mapped_column(nullable=False)
    event_type: Mapped[EventType] = mapped_column(nullable=False)
    importance: Mapped[Optional[int]] = mapped_column(Integer, comment="1-4 importance scale")

    # Timing information (for crop cycle events)
    start_day: Mapped[Optional[int]] = mapped_column(Integer, comment="Days from planting")
    end_day: Mapped[Optional[int]] = mapped_column(Integer, comment="Days from planting")

    # Metadata
    video_url: Mapped[Optional[str]] = mapped_column(String(500))
    translated: Mapped[bool] = mapped_column(Boolean, default=False)

    # JSON fields for complex data
    image_list: Mapped[Optional[dict]] = mapped_column(JSON)
    params: Mapped[Optional[List[dict]]] = mapped_column(JSON)
    farm_assets: Mapped[Optional[List[str]]] = mapped_column(JSON)
    farm_classes: Mapped[Optional[List[str]]] = mapped_column(JSON)
    farm_soils: Mapped[Optional[List[str]]] = mapped_column(JSON)
    farmer_experiences: Mapped[Optional[List[str]]] = mapped_column(JSON)
    farmer_groups: Mapped[Optional[List[str]]] = mapped_column(JSON)
    weather_limitations: Mapped[Optional[List[str]]] = mapped_column(JSON)

    # Relationships
    crops: Mapped[List["Crop"]] = relationship(secondary=event_crop_association, back_populates="events")
    prevent_pathogens: Mapped[List["Pathogen"]] = relationship(
        secondary=event_pathogen_association, back_populates="events"
    )

    def __repr__(self) -> str:
        return f"<Event(id='{self.id}', title='{self.title[:30]}...')>"


class CropCycle(Base, TimeStampMixin):
    """Crop cycle definition with stages"""

    __tablename__ = "crop_cycle"
    __table_args__ = {"schema": "farmbase_core"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    crop_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("farmbase_core.crop.host_id", ondelete="CASCADE"), nullable=False
    )
    koppen_climate_classification: Mapped[str] = mapped_column(String(10), nullable=False)

    # Relationships
    crop: Mapped["Crop"] = relationship(back_populates="cycles")
    stages: Mapped[List["CropCycleStage"]] = relationship(back_populates="cycle", cascade="all, delete-orphan")
    events: Mapped[List["CropCycleEvent"]] = relationship(back_populates="crop_cycle", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<CropCycle(id={self.id}, crop_id='{self.crop_id}', koppen='{self.koppen_climate_classification}')>"


class CropCycleStage(Base, TimeStampMixin):
    """Individual stages within a crop cycle"""

    __tablename__ = "crop_cycle_stage"
    __table_args__ = {"schema": "farmbase_core"}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cycle_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("farmbase_core.crop_cycle.id", ondelete="CASCADE"), nullable=False
    )
    order: Mapped[int] = mapped_column(Integer, nullable=False, comment="Crop cycle stage order")
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    duration: Mapped[int] = mapped_column(Integer, nullable=False, comment="Duration in days")

    # Relationships
    cycle: Mapped["CropCycle"] = relationship(back_populates="stages")

    def __repr__(self) -> str:
        return f"<CropCycleStage(id={self.id}, name='{self.name}', duration={self.duration})>"


class CropCycleEvent(Base, TimeStampMixin):
    """Events associated with crop cycles"""

    __tablename__ = "crop_cycle_event"
    __table_args__ = (UniqueConstraint("crop_cycle_id", "event_identifier"), {"schema": "farmbase_core"})

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    crop_cycle_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("farmbase_core.crop_cycle.id", ondelete="CASCADE"), nullable=False
    )
    event_identifier: Mapped[str] = mapped_column(
        String(255), ForeignKey("farmbase_core.event.identifier", ondelete="CASCADE"), nullable=False
    )
    start_day: Mapped[int] = mapped_column(Integer, nullable=False, comment="Days from planting")
    end_day: Mapped[int] = mapped_column(Integer, nullable=False, comment="Days from planting")
    original_event_id: Mapped[Optional[int]] = mapped_column(Integer, comment="Original ID from crop cycle JSON")

    # Relationships
    crop_cycle: Mapped["CropCycle"] = relationship(back_populates="events")
    event: Mapped["Event"] = relationship()

    def __repr__(self) -> str:
        return f"<CropCycleEvent(id={self.id}, event_identifier='{self.event_identifier}')>"
