import logging
from typing import Any, Dict

from async_lru import alru_cache
from fastapi import APIRouter, HTTPException
from mem0 import AsyncMemory
from mem0.configs.base import MemoryItem

from farmbase.config import settings
from farmbase.contact.memory.models import MemoryAddResults, MemoryCreate, MemoryResults, SearchRequest

DEFAULT_CONFIG = {
    "version": "v1.1",
    "vector_store": {
        "provider": "pgvector",
        # https:/docs.mem0.ai/components/vectordbs/dbs/pgvector#config
        "config": {
            "host": settings.DATABASE_HOSTNAME,
            "port": settings.DATABASE_PORT,
            "dbname": settings.DATABASE_NAME,
            "user": settings.DATABASE_USER,
            "password": settings.DATABASE_PASSWORD.get_secret_value(),
        },
    },
    # "graph_store": {
    #     "provider": "neo4j",
    #     "config": {"url": NEO4J_URI, "username": NEO4J_USERNAME, "password": NEO4J_PASSWORD},
    # },
    "llm": {"provider": "openai",
            "config": {"api_key": settings.OPENAI_API_KEY.get_secret_value(),
                       "temperature": 0.1, "model": "gpt-4o-mini"}},
    "embedder": {"provider": "openai",
                 "config": {"api_key": settings.OPENAI_API_KEY.get_secret_value(),
                            "model": "text-embedding-3-small"}},
}

router = APIRouter()


def get_user_id(organization: str, contact_id: int):
    return f"{organization}:{contact_id}"


# TODO: Could use api_router
@alru_cache(maxsize=None)
async def memory_instance() -> AsyncMemory:
    return await AsyncMemory.from_config(DEFAULT_CONFIG)


# @router.post("/configure", summary="Configure Mem0")
# def set_config(config: Dict[str, Any]):
#     """Set memory configuration."""
#     global memory_instance
#     memory_instance = Memory.from_config(config)
#     return {"message": "Configuration set successfully"}


@router.post("/", summary="Create memories", response_model=MemoryAddResults)
async def add_memory(organization: str,
                     contact_id: int,
                     memory_create: MemoryCreate):
    """Store new memories."""
    try:
        memory = await memory_instance()
        response = await memory.add(messages=[m.model_dump() for m in memory_create.messages],
                                    user_id=get_user_id(organization, contact_id))
        return response
    except Exception as e:
        logging.exception("Error in add_memory:")  # This will log the full traceback
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", summary="Get memories", response_model=MemoryResults)
async def get_all_memories(
        organization: str,
        contact_id: int,
):
    """Retrieve stored memories."""
    try:
        memory = await memory_instance()
        mem = await memory.get_all(
            user_id=get_user_id(organization, contact_id),
        )
        # TODO: Bug in AsyncMemory.get_all method!
        mem['results'] = await mem['results']
        return mem
    except Exception as e:
        logging.exception("Error in get_all_memories:")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{memory_id}", summary="Get a memory", response_model=MemoryItem)
async def get_memory(memory_id: str):
    """Retrieve a specific memory by ID."""
    try:
        memory = await memory_instance()
        return await memory.get(memory_id)
    except Exception as e:
        logging.exception("Error in get_memory:")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search", summary="Search memories", response_model=MemoryResults)
async def search_memories(organization: str,
                          contact_id: int,
                          search_req: SearchRequest):
    """Search for memories based on a query."""
    try:
        memory = await memory_instance()
        return await memory.search(query=search_req.query,
                                   user_id=get_user_id(organization, contact_id))
    except Exception as e:
        logging.exception("Error in search_memories:")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{memory_id}", summary="Update a memory", response_model=MemoryItem)
async def update_memory(memory_id: str, updated_memory: Dict[str, Any]):
    """Update an existing memory."""
    try:
        memory = await memory_instance()
        return await memory.update(memory_id=memory_id, data=updated_memory)
    except Exception as e:
        logging.exception("Error in update_memory:")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{memory_id}/history", summary="Get memory history")
async def memory_history(memory_id: str):
    """Retrieve memory history."""
    try:
        memory = await memory_instance()
        return await memory.history(memory_id=memory_id)
    except Exception as e:
        logging.exception("Error in memory_history:")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{memory_id}", summary="Delete a memory")
async def delete_memory(memory_id: str):
    """Delete a specific memory by ID."""
    try:
        memory = await memory_instance()
        await memory.delete(memory_id=memory_id)
        return {"message": "Memory deleted successfully"}
    except Exception as e:
        logging.exception("Error in delete_memory:")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/", summary="Delete all memories")
async def delete_all_memories(
        organization: str,
        contact_id: int
):
    """Delete all memories for a given identifier."""
    try:
        memory = await memory_instance()
        await memory.delete_all(user_id=get_user_id(organization, contact_id))
        return {"message": "All relevant memories deleted"}
    except Exception as e:
        logging.exception("Error in delete_all_memories:")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset", summary="Reset all memories")
async def reset_memory():
    """Completely reset stored memories."""
    try:
        memory = await memory_instance()
        await memory.reset()
        return {"message": "All memories reset"}
    except Exception as e:
        logging.exception("Error in reset_memory:")
        raise HTTPException(status_code=500, detail=str(e))
