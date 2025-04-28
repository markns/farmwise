import json
import uuid
from typing import Any

import geoalchemy2 as ga
import sqlalchemy
from fastapi import APIRouter, HTTPException
from geoalchemy2.functions import ST_GeomFromGeoJSON
from geojson_pydantic.geometries import Polygon, parse_geometry_obj
from sqlalchemy import func
from sqlmodel import select

from farmbase.api2.deps import CurrentUser, SessionDep
from farmbase.models import Field, FieldCreate, FieldPublic, FieldsPublic, FieldUpdate, Message

router = APIRouter(prefix="/farms/{farm_id}/fields", tags=["fields"])


@router.get("/", response_model=FieldsPublic)
def read_fields(
    session: SessionDep, current_user: CurrentUser, farm_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve fields.
    """
    count_statement = select(func.count()).select_from(Field).where(Field.farm_id == farm_id)
    count = session.exec(count_statement).one()
    statement = select(Field).where(Field.farm_id == farm_id).offset(skip).limit(limit)
    fields = session.exec(statement).all()

    return FieldsPublic(data=fields, count=count)


@router.get("/{id}", response_model=FieldPublic)
def read_field(session: SessionDep, current_user: CurrentUser, farm_id: uuid.UUID, id: uuid.UUID) -> Any:
    """
    Get field by ID.
    """

    stmt = (
        select(Field.id, Field.name, Field.area, ga.functions.ST_AsGeoJSON(Field.boundary).label("boundary"))
        .where(Field.id == id)
        .where("farm_id" == farm_id)
    )

    try:
        result = session.exec(stmt).one()
    except sqlalchemy.exc.NoResultFound:
        raise HTTPException(status_code=404, detail="Field not found")

    # if not current_user.is_superuser and (field.owner_id != current_user.id):
    #     raise HTTPException(status_code=400, detail="Not enough permissions")

    field = FieldPublic(
        id=result.id,
        farm_id=farm_id,
        name=result.name,
        boundary=parse_geometry_obj(json.loads(result.boundary)),
    )

    return field


@router.post("/", response_model=FieldPublic)
def create_field(*, session: SessionDep, current_user: CurrentUser, farm_id: uuid.UUID, field_in: FieldCreate) -> Any:
    """
    Create new field.
    """

    linestring = field_in.boundary

    # Ensure the LineString is closed by adding the first coordinate at the end
    if linestring.coordinates[0] != linestring.coordinates[-1]:
        closed_coords = linestring.coordinates + [linestring.coordinates[0]]
    else:
        closed_coords = linestring.coordinates  # Already closed

    # Convert to Polygon
    polygon = Polygon(type="Polygon", coordinates=[closed_coords])

    field = Field(
        name=field_in.name,
        farm_id=farm_id,
        linestring=ST_GeomFromGeoJSON(linestring.model_dump_json()),
        boundary=ST_GeomFromGeoJSON(polygon.model_dump_json()),
    )
    session.add(field)
    session.commit()
    session.refresh(field)

    geometry_json = session.exec(select(ga.functions.ST_AsGeoJSON(field.boundary))).one()
    boundary = parse_geometry_obj(json.loads(geometry_json))
    response = FieldPublic(
        id=field.id,
        farm_id=farm_id,
        name=field.name,
        boundary=boundary,
    )

    return response


@router.put("/{id}", response_model=FieldPublic)
def update_field(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    farm_id: uuid.UUID,
    id: uuid.UUID,
    field_in: FieldUpdate,
) -> Any:
    """
    Update a field.
    """
    field = session.get(Field, id)
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")
    if not current_user.is_superuser and (field.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    update_dict = field_in.model_dump(exclude_unset=True)
    field.sqlmodel_update(update_dict)
    session.add(field)
    session.commit()
    session.refresh(field)
    return field


@router.delete("/{id}")
def delete_field(session: SessionDep, current_user: CurrentUser, farm_id: uuid.UUID, id: uuid.UUID) -> Message:
    """
    Delete a field.
    """
    field = session.get(Field, id)
    if not field:
        raise HTTPException(status_code=404, detail="Field not found")
    if not current_user.is_superuser and (field.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(field)
    session.commit()
    return Message(message="Field deleted successfully")
