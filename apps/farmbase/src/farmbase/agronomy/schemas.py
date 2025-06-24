from typing import List, Optional
from datetime import datetime

from pydantic import Field

from farmbase.models import FarmbaseBase, Pagination, PrimaryKey
from farmbase.agronomy.models import (
    EventCategory,
    EventType,
    PathogenClass,
    SpreadRisk,
    GrowthStage,
    CultivationType,
    LaborLevel,
    WateringLevel,
)


# ————————————————————————————————————————
# Crop Schemas
# ————————————————————————————————————————

class CropBase(FarmbaseBase):
    """Base model for Crop data."""
    
    host_id: str = Field(description="Unique crop identifier")
    crop_cycle_length_min: int = Field(description="Minimum crop cycle length in days")
    crop_cycle_length_max: int = Field(description="Maximum crop cycle length in days")
    cultivation_type: CultivationType = Field(description="Cultivation method")
    description: Optional[str] = Field(default=None, description="Crop description")
    labor: LaborLevel = Field(description="Labor requirement level")
    watering: WateringLevel = Field(description="Watering requirement level")
    
    # Nutrient requirements
    n_opt: int = Field(description="Optimal nitrogen requirement (kg/ha)")
    p_opt: int = Field(description="Optimal phosphorus requirement (kg/ha)")
    k_opt: int = Field(description="Optimal potassium requirement (kg/ha)")
    
    # Soil requirements
    ph_from: float = Field(description="Minimum pH requirement")
    ph_to: float = Field(description="Maximum pH requirement")
    soil_description: Optional[str] = Field(default=None, description="Soil description")
    
    # Temperature requirements
    temp_day_growth_from: int = Field(description="Minimum growing temperature (°C)")
    temp_day_growth_to: int = Field(description="Maximum growing temperature (°C)")


class CropRead(CropBase):
    """Model for reading Crop data."""
    
    created_at: datetime
    updated_at: datetime


class CropCreate(CropBase):
    """Model for creating a new Crop."""
    pass


class CropUpdate(FarmbaseBase):
    """Model for updating an existing Crop."""
    
    crop_cycle_length_min: Optional[int] = Field(default=None)
    crop_cycle_length_max: Optional[int] = Field(default=None)
    cultivation_type: Optional[CultivationType] = Field(default=None)
    description: Optional[str] = Field(default=None)
    labor: Optional[LaborLevel] = Field(default=None)
    watering: Optional[WateringLevel] = Field(default=None)
    n_opt: Optional[int] = Field(default=None)
    p_opt: Optional[int] = Field(default=None)
    k_opt: Optional[int] = Field(default=None)
    ph_from: Optional[float] = Field(default=None)
    ph_to: Optional[float] = Field(default=None)
    soil_description: Optional[str] = Field(default=None)
    temp_day_growth_from: Optional[int] = Field(default=None)
    temp_day_growth_to: Optional[int] = Field(default=None)


class CropPagination(Pagination):
    """Model for paginated list of crops."""
    
    items: List[CropRead] = Field(default_factory=list)


# ————————————————————————————————————————
# Pathogen Schemas
# ————————————————————————————————————————

class PathogenImageBase(FarmbaseBase):
    """Base model for pathogen images."""
    
    file_name: str = Field(description="Image file name")
    url: Optional[str] = Field(default=None, description="Image URL")
    caption: Optional[str] = Field(default=None, description="Image caption")
    is_default: bool = Field(default=False, description="Is this the default image")


class PathogenImageRead(PathogenImageBase):
    """Model for reading pathogen image data."""
    
    id: PrimaryKey
    pathogen_id: int


class PathogenBase(FarmbaseBase):
    """Base model for Pathogen data."""
    
    name: str = Field(description="Pathogen name")
    name_en: Optional[str] = Field(default=None, description="English name")
    scientific_name: Optional[str] = Field(default=None, description="Scientific name")
    pathogen_class: PathogenClass = Field(description="Pathogen classification")
    severity: int = Field(description="Severity level (0-2)", ge=0, le=2)
    spread_risk: SpreadRisk = Field(description="Risk of spread")
    
    # Content fields
    symptoms: Optional[str] = Field(default=None, description="Disease symptoms")
    trigger: Optional[str] = Field(default=None, description="Disease triggers")
    chemical_treatment: Optional[str] = Field(default=None, description="Chemical treatment options")
    alternative_treatment: Optional[str] = Field(default=None, description="Alternative treatment options")
    preventive_measures: Optional[List[str]] = Field(default=None, description="Preventive measures")
    bullet_points: Optional[List[str]] = Field(default=None, description="Key bullet points")
    
    # Metadata
    default_image: Optional[str] = Field(default=None, description="Default image filename")
    eppo: Optional[str] = Field(default=None, description="EPPO code")
    is_activated: bool = Field(default=True, description="Is pathogen activated")
    translated: bool = Field(default=False, description="Is content translated")
    version_number: Optional[int] = Field(default=None, description="Version number")


class PathogenRead(PathogenBase):
    """Model for reading Pathogen data."""
    
    id: int
    created_at: datetime
    updated_at: datetime
    images: List[PathogenImageRead] = Field(default_factory=list)


class PathogenCreate(PathogenBase):
    """Model for creating a new Pathogen."""
    
    id: int = Field(description="Pathogen ID")


class PathogenUpdate(FarmbaseBase):
    """Model for updating an existing Pathogen."""
    
    name: Optional[str] = Field(default=None)
    name_en: Optional[str] = Field(default=None)
    scientific_name: Optional[str] = Field(default=None)
    pathogen_class: Optional[PathogenClass] = Field(default=None)
    severity: Optional[int] = Field(default=None, ge=0, le=2)
    spread_risk: Optional[SpreadRisk] = Field(default=None)
    symptoms: Optional[str] = Field(default=None)
    trigger: Optional[str] = Field(default=None)
    chemical_treatment: Optional[str] = Field(default=None)
    alternative_treatment: Optional[str] = Field(default=None)
    preventive_measures: Optional[List[str]] = Field(default=None)
    bullet_points: Optional[List[str]] = Field(default=None)
    default_image: Optional[str] = Field(default=None)
    eppo: Optional[str] = Field(default=None)
    is_activated: Optional[bool] = Field(default=None)
    translated: Optional[bool] = Field(default=None)
    version_number: Optional[int] = Field(default=None)


class PathogenPagination(Pagination):
    """Model for paginated list of pathogens."""
    
    items: List[PathogenRead] = Field(default_factory=list)


# ————————————————————————————————————————
# Event Schemas
# ————————————————————————————————————————

class EventBase(FarmbaseBase):
    """Base model for Event data."""
    
    identifier: str = Field(description="Unique event identifier")
    title: str = Field(description="Event title")
    description: Optional[str] = Field(default=None, description="Event description")
    nutshell: Optional[str] = Field(default=None, description="Brief summary")
    
    event_category: EventCategory = Field(description="Event category")
    event_type: EventType = Field(description="Event type")
    importance: Optional[int] = Field(default=None, description="Importance level (1-4)")
    
    # Timing information
    start_day: Optional[int] = Field(default=None, description="Start day from planting")
    end_day: Optional[int] = Field(default=None, description="End day from planting")
    
    # Metadata
    video_url: Optional[str] = Field(default=None, description="Video URL")
    translated: bool = Field(default=False, description="Is content translated")
    
    # JSON fields
    image_list: Optional[dict] = Field(default=None, description="Image information")
    params: Optional[List[dict]] = Field(default=None, description="Event parameters")
    farm_assets: Optional[List[str]] = Field(default=None, description="Required farm assets")
    farm_classes: Optional[List[str]] = Field(default=None, description="Farm classifications")
    farm_soils: Optional[List[str]] = Field(default=None, description="Suitable soil types")
    farmer_experiences: Optional[List[str]] = Field(default=None, description="Required farmer experience")
    farmer_groups: Optional[List[str]] = Field(default=None, description="Target farmer groups")
    weather_limitations: Optional[List[str]] = Field(default=None, description="Weather limitations")


class EventRead(EventBase):
    """Model for reading Event data."""
    
    id: str
    created_at: datetime
    updated_at: datetime


class EventCreate(EventBase):
    """Model for creating a new Event."""
    
    id: str = Field(description="Event ID")


class EventUpdate(FarmbaseBase):
    """Model for updating an existing Event."""
    
    identifier: Optional[str] = Field(default=None)
    title: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    nutshell: Optional[str] = Field(default=None)
    event_category: Optional[EventCategory] = Field(default=None)
    event_type: Optional[EventType] = Field(default=None)
    importance: Optional[int] = Field(default=None)
    start_day: Optional[int] = Field(default=None)
    end_day: Optional[int] = Field(default=None)
    video_url: Optional[str] = Field(default=None)
    translated: Optional[bool] = Field(default=None)
    image_list: Optional[dict] = Field(default=None)
    params: Optional[List[dict]] = Field(default=None)
    farm_assets: Optional[List[str]] = Field(default=None)
    farm_classes: Optional[List[str]] = Field(default=None)
    farm_soils: Optional[List[str]] = Field(default=None)
    farmer_experiences: Optional[List[str]] = Field(default=None)
    farmer_groups: Optional[List[str]] = Field(default=None)
    weather_limitations: Optional[List[str]] = Field(default=None)


class EventPagination(Pagination):
    """Model for paginated list of events."""
    
    items: List[EventRead] = Field(default_factory=list)


# ————————————————————————————————————————
# Crop Cycle & Stage Schemas
# ————————————————————————————————————————

class CropStageBase(FarmbaseBase):
    """Base model for crop stages."""
    
    stage_id: Optional[int] = Field(default=None, description="Original stage ID")
    name: str = Field(description="Stage name")
    duration_days: int = Field(description="Stage duration in days")
    sequence_order: int = Field(description="Order in the cycle")
    description: Optional[str] = Field(default=None, description="Stage description")


class CropStageRead(CropStageBase):
    """Model for reading crop stage data."""
    
    id: PrimaryKey
    cycle_id: int
    created_at: datetime
    updated_at: datetime


class CropCycleBase(FarmbaseBase):
    """Base model for crop cycles."""
    
    crop_id: str = Field(description="Associated crop ID")
    name: str = Field(description="Cycle name")
    description: Optional[str] = Field(default=None, description="Cycle description")
    total_duration_days: Optional[int] = Field(default=None, description="Total cycle duration")
    cultivation_method: Optional[str] = Field(default=None, description="Cultivation method")


class CropCycleRead(CropCycleBase):
    """Model for reading crop cycle data."""
    
    id: PrimaryKey
    created_at: datetime
    updated_at: datetime
    stages: List[CropStageRead] = Field(default_factory=list)


class CropCycleCreate(CropCycleBase):
    """Model for creating a new crop cycle."""
    pass


class CropCyclePagination(Pagination):
    """Model for paginated list of crop cycles."""
    
    items: List[CropCycleRead] = Field(default_factory=list)


# ————————————————————————————————————————
# Search and Filter Schemas
# ————————————————————————————————————————

class SearchFilters(FarmbaseBase):
    """Common search filters for data."""
    
    crop_id: Optional[str] = Field(default=None, description="Filter by crop ID")
    pathogen_class: Optional[PathogenClass] = Field(default=None, description="Filter by pathogen class")
    event_category: Optional[EventCategory] = Field(default=None, description="Filter by event category")
    severity: Optional[int] = Field(default=None, description="Filter by pathogen severity")
    growth_stage: Optional[GrowthStage] = Field(default=None, description="Filter by growth stage")


class PathogenSearchResponse(FarmbaseBase):
    """Response model for pathogen search."""
    
    pathogens: List[PathogenRead]
    total_count: int
    search_filters: SearchFilters


class EventSearchResponse(FarmbaseBase):
    """Response model for event search."""
    
    events: List[EventRead]
    total_count: int
    search_filters: SearchFilters