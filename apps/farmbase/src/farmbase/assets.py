from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class SexEnum(str, Enum):
    F = "F"
    M = "M"


class Animal(BaseModel):
    animal_type: str = Field(..., description="Species/breed of the animal. Required field.")
    birthdate: Optional[datetime] = Field(
        None, description="Birthdate provided as a Unix timestamp or ISO date string."
    )
    is_castrated: Optional[bool] = Field(False, description="Indicates if the animal has been castrated.")
    nickname: List[str] = Field(description="List of nicknames for the animal.")  # todo:, default_factory=list)
    sex: SexEnum = Field(..., description="Sex of the animal: 'F' for Female or 'M' for Male.")

    @field_validator("birthdate", mode="before")
    def validate_birthdate(cls, value):
        if value is None:
            return value
        if isinstance(value, (int, float)):
            return datetime.fromtimestamp(value)
        return value


class Land(BaseModel):
    land_type: str = Field(..., description="Type of land asset.")
    area_size: Optional[float] = Field(None, description="Size of the land in hectares.")
    location: Optional[str] = Field(None, description="Geographical location of the land.")


class Water(BaseModel):
    water_type: str = Field(..., description="Type of water resource (e.g., pond, river, well).")
    capacity: Optional[float] = Field(None, description="Water capacity in cubic meters.")
    location: Optional[str] = Field(None, description="Geographical location of the water source.")


class Seed(BaseModel):
    seed_variety: str = Field(..., description="Type of seed.")
    quantity: Optional[int] = Field(None, description="Quantity of seeds in kilograms.")
    origin: Optional[str] = Field(None, description="Source or supplier of the seed.")


class Plant(BaseModel):
    plant_species: str = Field(..., description="Species of the plant.")
    growth_stage: Optional[str] = Field(None, description="Current growth stage of the plant.")
    planted_date: Optional[datetime] = Field(None, description="Date when the plant was planted.")

    @field_validator("planted_date", mode="before")
    def validate_planted_date(cls, value):
        if value is None:
            return value
        if isinstance(value, (int, float)):
            return datetime.fromtimestamp(value)
        return value


class Pasture(BaseModel):
    pasture_type: str = Field(..., description="Type of pasture.")
    area_size: Optional[float] = Field(None, description="Size of the pasture in hectares.")
    usage: Optional[str] = Field(None, description="Usage description for the pasture.")


class Product(BaseModel):
    product_name: str = Field(..., description="Name of the product.")
    quantity: Optional[int] = Field(None, description="Quantity available.")
    unit: Optional[str] = Field(None, description="Unit of measurement.")


class Sensor(BaseModel):
    sensor_type: str = Field(..., description="Type of sensor.")
    location: Optional[str] = Field(None, description="Location of the sensor.")
    status: Optional[str] = Field(None, description="Current status of the sensor.")


class Compost(BaseModel):
    compost_type: str = Field(..., description="Type of compost material.")
    quantity: Optional[float] = Field(None, description="Amount of compost in kilograms.")
    composition: Optional[str] = Field(None, description="Composition details of the compost.")


class Structure(BaseModel):
    structure_type: str = Field(..., description="Type of farm structure.")
    size: Optional[float] = Field(None, description="Size of the structure in square meters.")
    material: Optional[str] = Field(None, description="Primary material used in the structure.")


class Equipment(BaseModel):
    equipment_type: str = Field(..., description="Type of equipment.")
    model: Optional[str] = Field(None, description="Model of the equipment.")
    condition: Optional[str] = Field(None, description="Current condition of the equipment.")


class Material(BaseModel):
    material_type: str = Field(..., description="Type of material.")
    quantity: Optional[float] = Field(None, description="Amount of material available.")
    unit: Optional[str] = Field(None, description="Unit of measurement for the material.")
