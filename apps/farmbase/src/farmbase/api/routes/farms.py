import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from farmbase.api.deps import CurrentUser, SessionDep
from farmbase.models import Farm, FarmCreate, FarmPublic, FarmsPublic, FarmUpdate, Message

router = APIRouter(prefix="/farms", tags=["farms"])


@router.get("/", response_model=FarmsPublic)
def read_farms(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve farms.
    """

    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Farm)
        count = session.exec(count_statement).one()
        statement = select(Farm).offset(skip).limit(limit)
        farms = session.exec(statement).all()
    else:
        count_statement = (
            select(func.count())
            .select_from(Farm)
            .where(Farm.owner_id == current_user.id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(Farm)
            .where(Farm.owner_id == current_user.id)
            .offset(skip)
            .limit(limit)
        )
        farms = session.exec(statement).all()

    return FarmsPublic(data=farms, count=count)


@router.get("/{id}", response_model=FarmPublic)
def read_farm(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get farm by ID.
    """
    farm = session.get(Farm, id)
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    if not current_user.is_superuser and (farm.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return farm


@router.post("/", response_model=FarmPublic)
def create_farm(
    *, session: SessionDep, current_user: CurrentUser, farm_in: FarmCreate
) -> Any:
    """
    Create new farm.
    """
    farm = Farm.model_validate(farm_in, update={"owner_id": current_user.id})
    session.add(farm)
    session.commit()
    session.refresh(farm)
    return farm


@router.put("/{id}", response_model=FarmPublic)
def update_farm(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: uuid.UUID,
    farm_in: FarmUpdate,
) -> Any:
    """
    Update a farm.
    """
    farm = session.get(Farm, id)
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    if not current_user.is_superuser and (farm.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    update_dict = farm_in.model_dump(exclude_unset=True)
    farm.sqlmodel_update(update_dict)
    session.add(farm)
    session.commit()
    session.refresh(farm)
    return farm


@router.delete("/{id}")
def delete_farm(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete a farm.
    """
    farm = session.get(Farm, id)
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    if not current_user.is_superuser and (farm.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(farm)
    session.commit()
    return Message(message="Farm deleted successfully")
