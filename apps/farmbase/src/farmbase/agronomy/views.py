from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from farmbase.agronomy.models import EventCategory, PathogenClass
from farmbase.agronomy.schemas import (
    CropCreate,
    CropCycleCreate,
    CropCycleEventCreate,
    CropCycleEventRead,
    CropCyclePagination,
    CropCycleRead,
    CropCycleStageCreate,
    CropCycleStageRead,
    CropCycleUpdate,
    CropPagination,
    CropRead,
    CropUpdate,
    EventCreate,
    EventPagination,
    EventRead,
    EventSearchResponse,
    EventUpdate,
    PathogenCreate,
    PathogenPagination,
    PathogenRead,
    PathogenSearchResponse,
    PathogenUpdate,
    SearchFilters,
)
from farmbase.agronomy.service import (
    count_events_by_category,
    # Utility services
    count_pathogens_by_class,
    create_crop,
    create_crop_cycle,
    create_event,
    create_pathogen,
    delete_crop,
    delete_crop_cycle,
    delete_event,
    delete_pathogen,
    get_all_crop_cycles,
    get_all_crops,
    get_all_events,
    get_all_pathogens,
    # Crop services
    get_crop,
    # Crop cycle services
    get_crop_cycle,
    get_crop_cycle_events_by_time_range,
    # Crop cycle event services
    get_crop_cycle_events_for_crop_cycle,
    # Crop cycle stage services
    get_crop_cycle_stages_for_crop_cycle,
    get_crop_cycles_for_crop,
    get_crop_summary,
    # Event services
    get_event,
    get_events_for_crop,
    # Pathogen services
    get_pathogen,
    get_preventive_events_for_pathogen,
    search_pathogens_by_crop,
    update_crop,
    update_crop_cycle,
    update_event,
    update_pathogen,
)
from farmbase.database.core import DbSession
from farmbase.models import PaginationParams

router = APIRouter()


# ————————————————————————————————————————
# Crop Endpoints
# ————————————————————————————————————————


@router.get("/crops", response_model=CropPagination)
async def list_crops(
    session: DbSession,
    pagination: PaginationParams = Depends(),
    cultivation_type: Optional[str] = Query(None, description="Filter by cultivation type"),
    labor_level: Optional[str] = Query(None, description="Filter by labor level"),
) -> CropPagination:
    """Get all crops with optional filtering and pagination."""
    crops = await get_all_crops(
        session=session,
        pagination=pagination,
        cultivation_type=cultivation_type,
        labor_level=labor_level,
    )

    return CropPagination(
        items=[CropRead.model_validate(crop) for crop in crops],
        page=pagination.page,
        items_per_page=pagination.items_per_page,
        total=len(crops),  # TODO: Implement proper count
    )


@router.get("/crops/{crop_id}", response_model=CropRead)
async def get_crop_detail(session: DbSession, crop_id: str) -> CropRead:
    """Get detailed information about a specific crop."""
    crop = await get_crop(session, crop_id)
    if not crop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Crop with ID '{crop_id}' not found")
    return CropRead.model_validate(crop)


@router.post("/crops", response_model=CropRead, status_code=status.HTTP_201_CREATED)
async def create_new_crop(session: DbSession, crop_data: CropCreate) -> CropRead:
    """Create a new crop."""
    crop = await create_crop(session, crop_data.model_dump())
    return CropRead.model_validate(crop)


@router.put("/crops/{crop_id}", response_model=CropRead)
async def update_existing_crop(session: DbSession, crop_id: str, crop_data: CropUpdate) -> CropRead:
    """Update an existing crop."""
    crop = await update_crop(session, crop_id, crop_data.model_dump(exclude_unset=True))
    if not crop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Crop with ID '{crop_id}' not found")
    return CropRead.model_validate(crop)


@router.delete("/crops/{crop_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_crop(session: DbSession, crop_id: str) -> None:
    """Delete a crop."""
    success = await delete_crop(session, crop_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Crop with ID '{crop_id}' not found")


@router.get("/crops/{crop_id}/summary")
async def get_crop_summary_info(session: DbSession, crop_id: str) -> dict:
    """Get a summary of all data related to a crop."""
    summary = await get_crop_summary(session, crop_id)
    if not summary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Crop with ID '{crop_id}' not found")
    return summary


# ————————————————————————————————————————
# Pathogen Endpoints
# ————————————————————————————————————————


@router.get("/pathogens", response_model=PathogenPagination)
async def list_pathogens(
    session: DbSession,
    pagination: PaginationParams = Depends(),
    pathogen_class: Optional[PathogenClass] = Query(None, description="Filter by pathogen class"),
    severity: Optional[int] = Query(None, description="Filter by severity level"),
    crop_id: Optional[str] = Query(None, description="Filter by affected crop"),
    is_activated: bool = Query(True, description="Filter by activation status"),
) -> PathogenPagination:
    """Get all pathogens with optional filtering and pagination."""
    pathogens = await get_all_pathogens(
        session=session,
        pagination=pagination,
        pathogen_class=pathogen_class,
        severity=severity,
        crop_id=crop_id,
        is_activated=is_activated,
    )

    return PathogenPagination(
        items=[PathogenRead.model_validate(pathogen) for pathogen in pathogens],
        page=pagination.page,
        items_per_page=pagination.items_per_page,
        total=len(pathogens),  # TODO: Implement proper count
    )


@router.get("/pathogens/{pathogen_id}", response_model=PathogenRead)
async def get_pathogen_detail(session: DbSession, pathogen_id: int) -> PathogenRead:
    """Get detailed information about a specific pathogen."""
    pathogen = await get_pathogen(session, pathogen_id)
    if not pathogen:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Pathogen with ID '{pathogen_id}' not found")
    return PathogenRead.model_validate(pathogen)


@router.get("/pathogens/search/by-crop/{crop_id}", response_model=PathogenSearchResponse)
async def search_pathogens_for_crop(
    session: DbSession,
    crop_id: str,
    pathogen_class: Optional[PathogenClass] = Query(None),
    severity: Optional[int] = Query(None, ge=0, le=2),
) -> PathogenSearchResponse:
    """Search pathogens that affect a specific crop."""
    pathogens = await search_pathogens_by_crop(
        session=session,
        crop_id=crop_id,
        pathogen_class=pathogen_class,
        severity=severity,
    )

    return PathogenSearchResponse(
        pathogens=[PathogenRead.model_validate(p) for p in pathogens],
        total_count=len(pathogens),
        search_filters=SearchFilters(
            crop_id=crop_id,
            pathogen_class=pathogen_class,
            severity=severity,
        ),
    )


@router.post("/pathogens", response_model=PathogenRead, status_code=status.HTTP_201_CREATED)
async def create_new_pathogen(session: DbSession, pathogen_data: PathogenCreate) -> PathogenRead:
    """Create a new pathogen."""
    pathogen = await create_pathogen(session, pathogen_data.model_dump())
    return PathogenRead.model_validate(pathogen)


@router.put("/pathogens/{pathogen_id}", response_model=PathogenRead)
async def update_existing_pathogen(
    session: DbSession,
    pathogen_id: int,
    pathogen_data: PathogenUpdate,
) -> PathogenRead:
    """Update an existing pathogen."""
    pathogen = await update_pathogen(session, pathogen_id, pathogen_data.model_dump(exclude_unset=True))
    if not pathogen:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Pathogen with ID '{pathogen_id}' not found")
    return PathogenRead.model_validate(pathogen)


@router.delete("/pathogens/{pathogen_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_pathogen(session: DbSession, pathogen_id: int) -> None:
    """Delete a pathogen."""
    success = await delete_pathogen(session, pathogen_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Pathogen with ID '{pathogen_id}' not found")


# ————————————————————————————————————————
# Event Endpoints
# ————————————————————————————————————————


@router.get("/events", response_model=EventPagination)
async def list_events(
    session: DbSession,
    pagination: PaginationParams = Depends(),
    event_category: Optional[EventCategory] = Query(None, description="Filter by event category"),
    crop_id: Optional[str] = Query(None, description="Filter by crop"),
    importance: Optional[int] = Query(None, ge=1, le=4, description="Filter by importance level"),
) -> EventPagination:
    """Get all events with optional filtering and pagination."""
    events = await get_all_events(
        session=session,
        pagination=pagination,
        event_category=event_category,
        crop_id=crop_id,
        importance=importance,
    )

    return EventPagination(
        items=[EventRead.model_validate(event) for event in events],
        page=pagination.page,
        items_per_page=pagination.items_per_page,
        total=len(events),  # TODO: Implement proper count
    )


@router.get("/events/{event_id}", response_model=EventRead)
async def get_event_detail(session: DbSession, event_id: str) -> EventRead:
    """Get detailed information about a specific event."""
    event = await get_event(session, event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Event with ID '{event_id}' not found")
    return EventRead.model_validate(event)


@router.get("/events/crop/{crop_id}", response_model=EventSearchResponse)
async def get_events_for_crop_endpoint(
    session: DbSession,
    crop_id: str,
    event_category: Optional[EventCategory] = Query(None),
    start_day: Optional[int] = Query(None, ge=0, description="Filter events starting from this day"),
    end_day: Optional[int] = Query(None, ge=0, description="Filter events ending before this day"),
) -> EventSearchResponse:
    """Get events relevant to a specific crop."""
    events = await get_events_for_crop(
        session=session,
        crop_id=crop_id,
        event_category=event_category,
        start_day=start_day,
        end_day=end_day,
    )

    return EventSearchResponse(
        events=[EventRead.model_validate(event) for event in events],
        total_count=len(events),
        search_filters=SearchFilters(
            crop_id=crop_id,
            event_category=event_category,
        ),
    )


@router.get("/events/pathogen/{pathogen_id}/preventive", response_model=List[EventRead])
async def get_preventive_events_for_pathogen_endpoint(
    session: DbSession,
    pathogen_id: int,
    crop_id: Optional[str] = Query(None, description="Filter by crop"),
) -> List[EventRead]:
    """Get events that prevent a specific pathogen."""
    events = await get_preventive_events_for_pathogen(
        session=session,
        pathogen_id=pathogen_id,
        crop_id=crop_id,
    )

    return [EventRead.model_validate(event) for event in events]


@router.post("/events", response_model=EventRead, status_code=status.HTTP_201_CREATED)
async def create_new_event(session: DbSession, event_data: EventCreate) -> EventRead:
    """Create a new event."""
    event = await create_event(session, event_data.model_dump())
    return EventRead.model_validate(event)


@router.put("/events/{event_id}", response_model=EventRead)
async def update_existing_event(
    session: DbSession,
    event_id: str,
    event_data: EventUpdate,
) -> EventRead:
    """Update an existing event."""
    event = await update_event(session, event_id, event_data.model_dump(exclude_unset=True))
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Event with ID '{event_id}' not found")
    return EventRead.model_validate(event)


@router.delete("/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_event(session: DbSession, event_id: str) -> None:
    """Delete an event."""
    success = await delete_event(session, event_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Event with ID '{event_id}' not found")


# ————————————————————————————————————————
# Crop Cycle Endpoints
# ————————————————————————————————————————


@router.get("/crop-cycles", response_model=CropCyclePagination)
async def list_crop_cycles(
    session: DbSession,
    pagination: PaginationParams = Depends(),
    crop_id: Optional[str] = Query(None, description="Filter by crop ID"),
    koppen_classification: Optional[str] = Query(None, description="Filter by Köppen climate classification"),
) -> CropCyclePagination:
    """Get all crop cycles with optional filtering and pagination."""
    cycles = await get_all_crop_cycles(
        session=session,
        pagination=pagination,
        crop_id=crop_id,
        koppen_classification=koppen_classification,
    )

    return CropCyclePagination(
        items=[CropCycleRead.model_validate(cycle) for cycle in cycles],
        page=pagination.page,
        items_per_page=pagination.items_per_page,
        total=len(cycles),  # TODO: Implement proper count
    )


@router.get("/crop-cycles/{cycle_id}", response_model=CropCycleRead)
async def get_crop_cycle_detail(session: DbSession, cycle_id: int) -> CropCycleRead:
    """Get detailed information about a specific crop cycle."""
    cycle = await get_crop_cycle(session, cycle_id)
    if not cycle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Crop cycle with ID '{cycle_id}' not found")
    return CropCycleRead.model_validate(cycle)


@router.get("/crop-cycles/crop/{crop_id}", response_model=List[CropCycleRead])
async def get_crop_cycles_for_crop_endpoint(
    session: DbSession,
    crop_id: str,
    koppen_classification: Optional[str] = Query(None, description="Filter by Köppen climate classification"),
) -> List[CropCycleRead]:
    """Get all crop cycles for a specific crop."""
    cycles = await get_crop_cycles_for_crop(session, crop_id, koppen_classification)
    return [CropCycleRead.model_validate(cycle) for cycle in cycles]


@router.post("/crop-cycles", response_model=CropCycleRead, status_code=status.HTTP_201_CREATED)
async def create_new_crop_cycle(
    session: DbSession,
    cycle_data: CropCycleCreate,
    stages_data: Optional[List[CropCycleStageCreate]] = [],
    events_data: Optional[List[CropCycleEventCreate]] = [],
) -> CropCycleRead:
    """Create a new crop cycle with stages and events."""
    stages_dict = [stage.model_dump() for stage in stages_data] if stages_data else []
    events_dict = [event.model_dump() for event in events_data] if events_data else []

    cycle = await create_crop_cycle(session, cycle_data.model_dump(), stages_dict, events_dict)
    return CropCycleRead.model_validate(cycle)


@router.put("/crop-cycles/{cycle_id}", response_model=CropCycleRead)
async def update_existing_crop_cycle(
    session: DbSession,
    cycle_id: int,
    cycle_data: CropCycleUpdate,
    stages_data: Optional[List[CropCycleStageCreate]] = None,
    events_data: Optional[List[CropCycleEventCreate]] = None,
) -> CropCycleRead:
    """Update an existing crop cycle."""
    stages_dict = [stage.model_dump() for stage in stages_data] if stages_data else None
    events_dict = [event.model_dump() for event in events_data] if events_data else None

    cycle = await update_crop_cycle(
        session, cycle_id, cycle_data.model_dump(exclude_unset=True), stages_dict, events_dict
    )
    if not cycle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Crop cycle with ID '{cycle_id}' not found")
    return CropCycleRead.model_validate(cycle)


@router.delete("/crop-cycles/{cycle_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_crop_cycle(session: DbSession, cycle_id: int) -> None:
    """Delete a crop cycle."""
    success = await delete_crop_cycle(session, cycle_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Crop cycle with ID '{cycle_id}' not found")


# ————————————————————————————————————————
# Crop Cycle Events Endpoints
# ————————————————————————————————————————


@router.get("/crop-cycles/{cycle_id}/events", response_model=List[CropCycleEventRead])
async def get_crop_cycle_events(session: DbSession, cycle_id: int) -> List[CropCycleEventRead]:
    """Get all events for a specific crop cycle."""
    events = await get_crop_cycle_events_for_crop_cycle(session, cycle_id)
    return [CropCycleEventRead.model_validate(event) for event in events]


@router.get("/crop-cycles/{cycle_id}/events/time-range", response_model=List[CropCycleEventRead])
async def get_crop_cycle_events_by_time(
    session: DbSession,
    cycle_id: int,
    start_day: Optional[int] = Query(None, ge=0, description="Start day filter"),
    end_day: Optional[int] = Query(None, ge=0, description="End day filter"),
) -> List[CropCycleEventRead]:
    """Get crop cycle events within a specific time range."""
    events = await get_crop_cycle_events_by_time_range(session, cycle_id, start_day, end_day)
    return [CropCycleEventRead.model_validate(event) for event in events]


# ————————————————————————————————————————
# Crop Cycle Stages Endpoints
# ————————————————————————————————————————


@router.get("/crop-cycles/{cycle_id}/stages", response_model=List[CropCycleStageRead])
async def get_crop_cycle_stages(session: DbSession, cycle_id: int) -> List[CropCycleStageRead]:
    """Get all stages for a specific crop cycle."""
    stages = await get_crop_cycle_stages_for_crop_cycle(session, cycle_id)
    return [CropCycleStageRead.model_validate(stage) for stage in stages]


# ————————————————————————————————————————
# Analytics Endpoints
# ————————————————————————————————————————


@router.get("/analytics/pathogens/by-class")
async def get_pathogen_counts_by_class(session: DbSession) -> dict:
    """Get count of pathogens by classification."""
    return await count_pathogens_by_class(session)


@router.get("/analytics/events/by-category")
async def get_event_counts_by_category(session: DbSession) -> dict:
    """Get count of events by category."""
    return await count_events_by_category(session)
