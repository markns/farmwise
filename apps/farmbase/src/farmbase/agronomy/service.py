from typing import List, Optional, Sequence
from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session, selectinload

from farmbase.models import PaginationParams
from farmbase.agronomy.models import (
    Crop,
    Pathogen,
    Event,
    CropCycle,
    CropStage,
    PathogenImage,
    EventCategory,
    PathogenClass,
    GrowthStage,
    event_crop_association,
    event_pathogen_association,
    pathogen_crop_association,
)


# ————————————————————————————————————————
# Crop Services
# ————————————————————————————————————————

def get_crop(session: Session, host_id: str) -> Optional[Crop]:
    """Get a crop by host_id."""
    return session.get(Crop, host_id)


def get_all_crops(
    session: Session,
    pagination: Optional[PaginationParams] = None,
    cultivation_type: Optional[str] = None,
    labor_level: Optional[str] = None,
) -> Sequence[Crop]:
    """Get all crops with optional filtering and pagination."""
    query = select(Crop)
    
    # Apply filters
    if cultivation_type:
        query = query.where(Crop.cultivation_type == cultivation_type)
    if labor_level:
        query = query.where(Crop.labor == labor_level)
    
    # Apply pagination
    if pagination and pagination.limit_offset:
        limit, offset = pagination.limit_offset
        query = query.offset(offset).limit(limit)
    
    return session.execute(query).scalars().all()


def create_crop(session: Session, crop_data: dict) -> Crop:
    """Create a new crop."""
    crop = Crop(**crop_data)
    session.add(crop)
    session.commit()
    session.refresh(crop)
    return crop


def update_crop(session: Session, host_id: str, crop_data: dict) -> Optional[Crop]:
    """Update an existing crop."""
    crop = session.get(Crop, host_id)
    if not crop:
        return None
    
    for key, value in crop_data.items():
        if hasattr(crop, key) and value is not None:
            setattr(crop, key, value)
    
    session.commit()
    session.refresh(crop)
    return crop


def delete_crop(session: Session, host_id: str) -> bool:
    """Delete a crop."""
    crop = session.get(Crop, host_id)
    if not crop:
        return False
    
    session.delete(crop)
    session.commit()
    return True


# ————————————————————————————————————————
# Pathogen Services
# ————————————————————————————————————————

def get_pathogen(session: Session, pathogen_id: int) -> Optional[Pathogen]:
    """Get a pathogen by ID with images."""
    return session.execute(
        select(Pathogen)
        .options(selectinload(Pathogen.images))
        .where(Pathogen.id == pathogen_id)
    ).scalar_one_or_none()


def get_all_pathogens(
    session: Session,
    pagination: Optional[PaginationParams] = None,
    pathogen_class: Optional[PathogenClass] = None,
    severity: Optional[int] = None,
    crop_id: Optional[str] = None,
    is_activated: bool = True,
) -> Sequence[Pathogen]:
    """Get all pathogens with optional filtering and pagination."""
    query = select(Pathogen).options(selectinload(Pathogen.images))
    
    # Apply filters
    if pathogen_class:
        query = query.where(Pathogen.pathogen_class == pathogen_class)
    if severity is not None:
        query = query.where(Pathogen.severity == severity)
    if is_activated:
        query = query.where(Pathogen.is_activated == True)
    if crop_id:
        query = query.join(pathogen_crop_association).where(
            pathogen_crop_association.c.crop_id == crop_id
        )
    
    # Apply pagination
    if pagination and pagination.limit_offset:
        limit, offset = pagination.limit_offset
        query = query.offset(offset).limit(limit)
    
    return session.execute(query).scalars().all()


def search_pathogens_by_crop(
    session: Session, 
    crop_id: str,
    pathogen_class: Optional[PathogenClass] = None,
    severity: Optional[int] = None,
) -> Sequence[Pathogen]:
    """Search pathogens that affect a specific crop."""
    query = (
        select(Pathogen)
        .options(selectinload(Pathogen.images))
        .join(pathogen_crop_association)
        .where(pathogen_crop_association.c.crop_id == crop_id)
        .where(Pathogen.is_activated == True)
    )
    
    if pathogen_class:
        query = query.where(Pathogen.pathogen_class == pathogen_class)
    if severity is not None:
        query = query.where(Pathogen.severity == severity)
    
    return session.execute(query).scalars().all()


def create_pathogen(session: Session, pathogen_data: dict) -> Pathogen:
    """Create a new pathogen."""
    pathogen = Pathogen(**pathogen_data)
    session.add(pathogen)
    session.commit()
    session.refresh(pathogen)
    return pathogen


def update_pathogen(session: Session, pathogen_id: int, pathogen_data: dict) -> Optional[Pathogen]:
    """Update an existing pathogen."""
    pathogen = session.get(Pathogen, pathogen_id)
    if not pathogen:
        return None
    
    for key, value in pathogen_data.items():
        if hasattr(pathogen, key) and value is not None:
            setattr(pathogen, key, value)
    
    session.commit()
    session.refresh(pathogen)
    return pathogen


def delete_pathogen(session: Session, pathogen_id: int) -> bool:
    """Delete a pathogen."""
    pathogen = session.get(Pathogen, pathogen_id)
    if not pathogen:
        return False
    
    session.delete(pathogen)
    session.commit()
    return True


# ————————————————————————————————————————
# Event Services
# ————————————————————————————————————————

def get_event(session: Session, event_id: str) -> Optional[Event]:
    """Get an event by ID."""
    return session.get(Event, event_id)


def get_all_events(
    session: Session,
    pagination: Optional[PaginationParams] = None,
    event_category: Optional[EventCategory] = None,
    crop_id: Optional[str] = None,
    importance: Optional[int] = None,
) -> Sequence[Event]:
    """Get all events with optional filtering and pagination."""
    query = select(Event)
    
    # Apply filters
    if event_category:
        query = query.where(Event.event_category == event_category)
    if importance is not None:
        query = query.where(Event.importance == importance)
    if crop_id:
        query = query.join(event_crop_association).where(
            event_crop_association.c.crop_id == crop_id
        )
    
    # Apply pagination
    if pagination and pagination.limit_offset:
        limit, offset = pagination.limit_offset
        query = query.offset(offset).limit(limit)
    
    return session.execute(query).scalars().all()


def get_events_for_crop(
    session: Session,
    crop_id: str,
    event_category: Optional[EventCategory] = None,
    start_day: Optional[int] = None,
    end_day: Optional[int] = None,
) -> Sequence[Event]:
    """Get events relevant to a specific crop."""
    query = (
        select(Event)
        .join(event_crop_association)
        .where(event_crop_association.c.crop_id == crop_id)
    )
    
    if event_category:
        query = query.where(Event.event_category == event_category)
    
    # Filter by timing if provided
    if start_day is not None:
        query = query.where(Event.end_day >= start_day)
    if end_day is not None:
        query = query.where(Event.start_day <= end_day)
    
    # Order by start day for crop planning
    query = query.order_by(Event.start_day.nullslast())
    
    return session.execute(query).scalars().all()


def get_preventive_events_for_pathogen(
    session: Session,
    pathogen_id: int,
    crop_id: Optional[str] = None,
) -> Sequence[Event]:
    """Get events that prevent a specific pathogen."""
    query = (
        select(Event)
        .join(event_pathogen_association)
        .where(event_pathogen_association.c.pathogen_id == pathogen_id)
    )
    
    if crop_id:
        query = query.join(event_crop_association).where(
            event_crop_association.c.crop_id == crop_id
        )
    
    return session.execute(query).scalars().all()


def create_event(session: Session, event_data: dict) -> Event:
    """Create a new event."""
    event = Event(**event_data)
    session.add(event)
    session.commit()
    session.refresh(event)
    return event


def update_event(session: Session, event_id: str, event_data: dict) -> Optional[Event]:
    """Update an existing event."""
    event = session.get(Event, event_id)
    if not event:
        return None
    
    for key, value in event_data.items():
        if hasattr(event, key) and value is not None:
            setattr(event, key, value)
    
    session.commit()
    session.refresh(event)
    return event


def delete_event(session: Session, event_id: str) -> bool:
    """Delete an event."""
    event = session.get(Event, event_id)
    if not event:
        return False
    
    session.delete(event)
    session.commit()
    return True


# ————————————————————————————————————————
# Crop Cycle Services
# ————————————————————————————————————————

def get_crop_cycle(session: Session, cycle_id: int) -> Optional[CropCycle]:
    """Get a crop cycle by ID with stages."""
    return session.execute(
        select(CropCycle)
        .options(selectinload(CropCycle.stages))
        .where(CropCycle.id == cycle_id)
    ).scalar_one_or_none()


def get_crop_cycles_for_crop(
    session: Session,
    crop_id: str,
) -> Sequence[CropCycle]:
    """Get all crop cycles for a specific crop."""
    return session.execute(
        select(CropCycle)
        .options(selectinload(CropCycle.stages))
        .where(CropCycle.crop_id == crop_id)
    ).scalars().all()


def create_crop_cycle(session: Session, cycle_data: dict, stages_data: List[dict]) -> CropCycle:
    """Create a new crop cycle with stages."""
    cycle = CropCycle(**cycle_data)
    session.add(cycle)
    session.flush()  # Get the ID without committing
    
    # Add stages
    for stage_data in stages_data:
        stage = CropStage(cycle_id=cycle.id, **stage_data)
        session.add(stage)
    
    session.commit()
    session.refresh(cycle)
    return cycle


def update_crop_cycle(
    session: Session,
    cycle_id: int,
    cycle_data: dict,
    stages_data: Optional[List[dict]] = None,
) -> Optional[CropCycle]:
    """Update an existing crop cycle."""
    cycle = session.get(CropCycle, cycle_id)
    if not cycle:
        return None
    
    # Update cycle data
    for key, value in cycle_data.items():
        if hasattr(cycle, key) and value is not None:
            setattr(cycle, key, value)
    
    # Update stages if provided
    if stages_data is not None:
        # Delete existing stages
        session.execute(
            select(CropStage).where(CropStage.cycle_id == cycle_id)
        )
        
        # Add new stages
        for stage_data in stages_data:
            stage = CropStage(cycle_id=cycle.id, **stage_data)
            session.add(stage)
    
    session.commit()
    session.refresh(cycle)
    return cycle


def delete_crop_cycle(session: Session, cycle_id: int) -> bool:
    """Delete a crop cycle."""
    cycle = session.get(CropCycle, cycle_id)
    if not cycle:
        return False
    
    session.delete(cycle)
    session.commit()
    return True


# ————————————————————————————————————————
# Utility Services
# ————————————————————————————————————————

def count_pathogens_by_class(session: Session) -> dict:
    """Get count of pathogens by class."""
    result = session.execute(
        select(Pathogen.pathogen_class, func.count(Pathogen.id))
        .where(Pathogen.is_activated == True)
        .group_by(Pathogen.pathogen_class)
    ).all()
    
    return {pathogen_class: count for pathogen_class, count in result}


def count_events_by_category(session: Session) -> dict:
    """Get count of events by category."""
    result = session.execute(
        select(Event.event_category, func.count(Event.id))
        .group_by(Event.event_category)
    ).all()
    
    return {category: count for category, count in result}


def get_crop_summary(session: Session, crop_id: str) -> dict:
    """Get a summary of data related to a crop."""
    crop = session.get(Crop, crop_id)
    if not crop:
        return {}
    
    # Count pathogens
    pathogen_count = session.execute(
        select(func.count(Pathogen.id.distinct()))
        .join(pathogen_crop_association)
        .where(pathogen_crop_association.c.crop_id == crop_id)
        .where(Pathogen.is_activated == True)
    ).scalar()
    
    # Count events
    event_count = session.execute(
        select(func.count(Event.id.distinct()))
        .join(event_crop_association)
        .where(event_crop_association.c.crop_id == crop_id)
    ).scalar()
    
    # Count cycles
    cycle_count = session.execute(
        select(func.count(CropCycle.id))
        .where(CropCycle.crop_id == crop_id)
    ).scalar()
    
    return {
        "crop": crop,
        "pathogen_count": pathogen_count,
        "event_count": event_count,
        "cycle_count": cycle_count,
    }