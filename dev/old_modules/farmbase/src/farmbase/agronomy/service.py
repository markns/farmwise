from typing import List, Optional, Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from farmbase.agronomy.models import (
    Crop,
    CropCycle,
    CropCycleEvent,
    CropCycleStage,
    Event,
    EventCategory,
    Pathogen,
    PathogenClass,
    event_crop_association,
    event_pathogen_association,
    pathogen_crop_association,
)
from farmbase.models import PaginationParams

# ————————————————————————————————————————
# Crop Services
# ————————————————————————————————————————


async def get_crop(session: AsyncSession, host_id: str) -> Optional[Crop]:
    """Get a crop by host_id."""
    return await session.get(Crop, host_id)


async def get_all_crops(
    session: AsyncSession,
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

    result = await session.execute(query)
    return result.scalars().all()


async def create_crop(session: AsyncSession, crop_data: dict) -> Crop:
    """Create a new crop."""
    crop = Crop(**crop_data)
    session.add(crop)
    await session.commit()
    await session.refresh(crop)
    return crop


async def update_crop(session: AsyncSession, host_id: str, crop_data: dict) -> Optional[Crop]:
    """Update an existing crop."""
    crop = await session.get(Crop, host_id)
    if not crop:
        return None

    for key, value in crop_data.items():
        if hasattr(crop, key) and value is not None:
            setattr(crop, key, value)

    await session.commit()
    await session.refresh(crop)
    return crop


async def delete_crop(session: AsyncSession, host_id: str) -> bool:
    """Delete a crop."""
    crop = await session.get(Crop, host_id)
    if not crop:
        return False

    await session.delete(crop)
    await session.commit()
    return True


# ————————————————————————————————————————
# Pathogen Services
# ————————————————————————————————————————


async def get_pathogen(session: AsyncSession, pathogen_id: int) -> Optional[Pathogen]:
    """Get a pathogen by ID with images."""
    result = await session.execute(
        select(Pathogen).options(selectinload(Pathogen.images)).where(Pathogen.id == pathogen_id)
    )
    return result.scalar_one_or_none()


async def get_all_pathogens(
    session: AsyncSession,
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
        query = query.where(Pathogen.is_activated)
    if crop_id:
        query = query.join(pathogen_crop_association).where(pathogen_crop_association.c.crop_id == crop_id)

    # Apply pagination
    if pagination and pagination.limit_offset:
        limit, offset = pagination.limit_offset
        query = query.offset(offset).limit(limit)

    result = await session.execute(query)
    return result.scalars().all()


async def search_pathogens_by_crop(
    session: AsyncSession,
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
        .where(Pathogen.is_activated)
    )

    if pathogen_class:
        query = query.where(Pathogen.pathogen_class == pathogen_class)
    if severity is not None:
        query = query.where(Pathogen.severity == severity)

    result = await session.execute(query)
    return result.scalars().all()


async def create_pathogen(session: AsyncSession, pathogen_data: dict) -> Pathogen:
    """Create a new pathogen."""
    pathogen = Pathogen(**pathogen_data)
    session.add(pathogen)
    await session.commit()
    await session.refresh(pathogen)
    return pathogen


async def update_pathogen(session: AsyncSession, pathogen_id: int, pathogen_data: dict) -> Optional[Pathogen]:
    """Update an existing pathogen."""
    pathogen = await session.get(Pathogen, pathogen_id)
    if not pathogen:
        return None

    for key, value in pathogen_data.items():
        if hasattr(pathogen, key) and value is not None:
            setattr(pathogen, key, value)

    await session.commit()
    await session.refresh(pathogen)
    return pathogen


async def delete_pathogen(session: AsyncSession, pathogen_id: int) -> bool:
    """Delete a pathogen."""
    pathogen = await session.get(Pathogen, pathogen_id)
    if not pathogen:
        return False

    await session.delete(pathogen)
    await session.commit()
    return True


# ————————————————————————————————————————
# Event Services
# ————————————————————————————————————————


async def get_event(session: AsyncSession, event_id: str) -> Optional[Event]:
    """Get an event by ID."""
    return await session.get(Event, event_id)


async def get_all_events(
    session: AsyncSession,
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
        query = query.join(event_crop_association).where(event_crop_association.c.crop_id == crop_id)

    # Apply pagination
    if pagination and pagination.limit_offset:
        limit, offset = pagination.limit_offset
        query = query.offset(offset).limit(limit)

    result = await session.execute(query)
    return result.scalars().all()


async def get_events_for_crop(
    session: AsyncSession,
    crop_id: str,
    event_category: Optional[EventCategory] = None,
    start_day: Optional[int] = None,
    end_day: Optional[int] = None,
) -> Sequence[Event]:
    """Get events relevant to a specific crop."""
    query = select(Event).join(event_crop_association).where(event_crop_association.c.crop_id == crop_id)

    if event_category:
        query = query.where(Event.event_category == event_category)

    # Filter by timing if provided
    if start_day is not None:
        query = query.where(Event.end_day >= start_day)
    if end_day is not None:
        query = query.where(Event.start_day <= end_day)

    # Order by start day for crop planning
    query = query.order_by(Event.start_day.nullslast())

    result = await session.execute(query)
    return result.scalars().all()


async def get_preventive_events_for_pathogen(
    session: AsyncSession,
    pathogen_id: int,
    crop_id: Optional[str] = None,
) -> Sequence[Event]:
    """Get events that prevent a specific pathogen."""
    query = (
        select(Event).join(event_pathogen_association).where(event_pathogen_association.c.pathogen_id == pathogen_id)
    )

    if crop_id:
        query = query.join(event_crop_association).where(event_crop_association.c.crop_id == crop_id)

    result = await session.execute(query)
    return result.scalars().all()


async def create_event(session: AsyncSession, event_data: dict) -> Event:
    """Create a new event."""
    event = Event(**event_data)
    session.add(event)
    await session.commit()
    await session.refresh(event)
    return event


async def update_event(session: AsyncSession, event_id: str, event_data: dict) -> Optional[Event]:
    """Update an existing event."""
    event = await session.get(Event, event_id)
    if not event:
        return None

    for key, value in event_data.items():
        if hasattr(event, key) and value is not None:
            setattr(event, key, value)

    await session.commit()
    await session.refresh(event)
    return event


async def delete_event(session: AsyncSession, event_id: str) -> bool:
    """Delete an event."""
    event = await session.get(Event, event_id)
    if not event:
        return False

    await session.delete(event)
    await session.commit()
    return True


# ————————————————————————————————————————
# Crop Cycle Services
# ————————————————————————————————————————


async def get_crop_cycle(session: AsyncSession, cycle_id: int) -> Optional[CropCycle]:
    """Get a crop cycle by ID with stages and events."""
    result = await session.execute(
        select(CropCycle)
        .options(
            selectinload(CropCycle.stages),
            selectinload(CropCycle.events).selectinload(CropCycleEvent.event),
            selectinload(CropCycle.crop),
        )
        .where(CropCycle.id == cycle_id)
    )
    return result.scalar_one_or_none()


async def get_crop_cycles_for_crop(
    session: AsyncSession,
    crop_id: str,
    koppen_classification: Optional[str] = None,
) -> Sequence[CropCycle]:
    """Get all crop cycles for a specific crop, optionally filtered by climate classification."""
    query = (
        select(CropCycle)
        .options(
            selectinload(CropCycle.stages),
            selectinload(CropCycle.events).selectinload(CropCycleEvent.event),
            selectinload(CropCycle.crop),
        )
        .where(CropCycle.crop_id == crop_id)
    )

    if koppen_classification:
        query = query.where(CropCycle.koppen_climate_classification == koppen_classification)

    result = await session.execute(query)
    return result.scalars().all()


async def get_all_crop_cycles(
    session: AsyncSession,
    pagination: Optional[PaginationParams] = None,
    crop_id: Optional[str] = None,
    koppen_classification: Optional[str] = None,
) -> Sequence[CropCycle]:
    """Get all crop cycles with optional filtering and pagination."""
    query = select(CropCycle).options(
        selectinload(CropCycle.stages),
        selectinload(CropCycle.events).selectinload(CropCycleEvent.event),
        selectinload(CropCycle.crop),
    )

    # Apply filters
    if crop_id:
        query = query.where(CropCycle.crop_id == crop_id)
    if koppen_classification:
        query = query.where(CropCycle.koppen_climate_classification == koppen_classification)

    # Apply pagination
    if pagination and pagination.limit_offset:
        limit, offset = pagination.limit_offset
        query = query.offset(offset).limit(limit)

    result = await session.execute(query)
    return result.scalars().all()


async def create_crop_cycle(
    session: AsyncSession,
    cycle_data: dict,
    stages_data: Optional[List[dict]] = None,
    events_data: Optional[List[dict]] = None,
) -> CropCycle:
    """Create a new crop cycle with stages and events."""
    cycle = CropCycle(**cycle_data)
    session.add(cycle)
    await session.flush()  # Get the ID without committing

    # Add stages
    if stages_data:
        for stage_data in stages_data:
            stage = CropCycleStage(cycle_id=cycle.id, **stage_data)
            session.add(stage)

    # Add events
    if events_data:
        for event_data in events_data:
            event = CropCycleEvent(crop_cycle_id=cycle.id, **event_data)
            session.add(event)

    await session.commit()
    await session.refresh(cycle)
    return cycle


async def update_crop_cycle(
    session: AsyncSession,
    cycle_id: int,
    cycle_data: dict,
    stages_data: Optional[List[dict]] = None,
    events_data: Optional[List[dict]] = None,
) -> Optional[CropCycle]:
    """Update an existing crop cycle."""
    cycle = await session.get(CropCycle, cycle_id)
    if not cycle:
        return None

    # Update cycle data
    for key, value in cycle_data.items():
        if hasattr(cycle, key) and value is not None:
            setattr(cycle, key, value)

    # Update stages if provided
    if stages_data is not None:
        # Delete existing stages
        result = await session.execute(select(CropCycleStage).where(CropCycleStage.cycle_id == cycle_id))
        existing_stages = result.scalars().all()

        for stage in existing_stages:
            await session.delete(stage)

        # Add new stages
        for stage_data in stages_data:
            stage = CropCycleStage(cycle_id=cycle.id, **stage_data)
            session.add(stage)

    # Update events if provided
    if events_data is not None:
        # Delete existing events
        result = await session.execute(select(CropCycleEvent).where(CropCycleEvent.crop_cycle_id == cycle_id))
        existing_events = result.scalars().all()

        for event in existing_events:
            await session.delete(event)

        # Add new events
        for event_data in events_data:
            event = CropCycleEvent(crop_cycle_id=cycle.id, **event_data)
            session.add(event)

    await session.commit()
    await session.refresh(cycle)
    return cycle


async def delete_crop_cycle(session: AsyncSession, cycle_id: int) -> bool:
    """Delete a crop cycle."""
    cycle = await session.get(CropCycle, cycle_id)
    if not cycle:
        return False

    await session.delete(cycle)
    await session.commit()
    return True


# ————————————————————————————————————————
# Crop Cycle Event Services
# ————————————————————————————————————————


async def get_crop_cycle_events_for_crop_cycle(session: AsyncSession, cycle_id: int) -> Sequence[CropCycleEvent]:
    """Get all events for a specific crop cycle."""
    result = await session.execute(
        select(CropCycleEvent)
        .options(selectinload(CropCycleEvent.event))
        .where(CropCycleEvent.crop_cycle_id == cycle_id)
        .order_by(CropCycleEvent.start_day)
    )
    return result.scalars().all()


async def get_crop_cycle_events_by_time_range(
    session: AsyncSession,
    cycle_id: int,
    start_day: Optional[int] = None,
    end_day: Optional[int] = None,
) -> Sequence[CropCycleEvent]:
    """Get crop cycle events within a specific time range."""
    query = (
        select(CropCycleEvent)
        .options(selectinload(CropCycleEvent.event))
        .where(CropCycleEvent.crop_cycle_id == cycle_id)
    )

    if start_day is not None:
        query = query.where(CropCycleEvent.end_day >= start_day)
    if end_day is not None:
        query = query.where(CropCycleEvent.start_day <= end_day)

    result = await session.execute(query.order_by(CropCycleEvent.start_day))
    return result.scalars().all()


# ————————————————————————————————————————
# Crop Cycle Stage Services
# ————————————————————————————————————————


async def get_crop_cycle_stages_for_crop_cycle(session: AsyncSession, cycle_id: int) -> Sequence[CropCycleStage]:
    """Get all stages for a specific crop cycle."""
    result = await session.execute(
        select(CropCycleStage).where(CropCycleStage.cycle_id == cycle_id).order_by(CropCycleStage.order)
    )
    return result.scalars().all()


# ————————————————————————————————————————
# Utility Services
# ————————————————————————————————————————


async def count_pathogens_by_class(session: AsyncSession) -> dict:
    """Get count of pathogens by class."""
    result = await session.execute(
        select(Pathogen.pathogen_class, func.count(Pathogen.id))
        .where(Pathogen.is_activated)
        .group_by(Pathogen.pathogen_class)
    )
    rows = result.all()

    return {pathogen_class: count for pathogen_class, count in rows}


async def count_events_by_category(session: AsyncSession) -> dict:
    """Get count of events by category."""
    result = await session.execute(select(Event.event_category, func.count(Event.id)).group_by(Event.event_category))
    rows = result.all()

    return {category: count for category, count in rows}


async def get_crop_summary(session: AsyncSession, crop_id: str) -> dict:
    """Get a summary of data related to a crop."""
    crop = await session.get(Crop, crop_id)
    if not crop:
        return {}

    # Count pathogens
    pathogen_result = await session.execute(
        select(func.count(Pathogen.id.distinct()))
        .join(pathogen_crop_association)
        .where(pathogen_crop_association.c.crop_id == crop_id)
        .where(Pathogen.is_activated)
    )
    pathogen_count = pathogen_result.scalar()

    # Count events
    event_result = await session.execute(
        select(func.count(Event.id.distinct()))
        .join(event_crop_association)
        .where(event_crop_association.c.crop_id == crop_id)
    )
    event_count = event_result.scalar()

    # Count cycles
    cycle_result = await session.execute(select(func.count(CropCycle.id)).where(CropCycle.crop_id == crop_id))
    cycle_count = cycle_result.scalar()

    return {
        "crop": crop,
        "pathogen_count": pathogen_count,
        "event_count": event_count,
        "cycle_count": cycle_count,
    }
