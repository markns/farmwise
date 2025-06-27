import logging
from typing import Any, Dict, Optional

from fastapi import HTTPException, APIRouter
from fastapi.responses import JSONResponse
from mem0 import Memory

from farmbase.config import settings
from farmbase.contact.memory.models import MemoryCreate, SearchRequest

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

memory_instance = Memory.from_config(DEFAULT_CONFIG)

router = APIRouter()


def get_user_id(organization: str, contact_id: int):
    return f"{organization}:{contact_id}"


# @router.post("/configure", summary="Configure Mem0")
# def set_config(config: Dict[str, Any]):
#     """Set memory configuration."""
#     global memory_instance
#     memory_instance = Memory.from_config(config)
#     return {"message": "Configuration set successfully"}


@router.post("/", summary="Create memories")
def add_memory(organization: str,
               contact_id: int,
               memory_create: MemoryCreate):
    """Store new memories."""
    print(memory_create)
    try:
        response = memory_instance.add(messages=[m.model_dump() for m in memory_create.messages],
                                       user_id=get_user_id(organization, contact_id))
        return JSONResponse(content=response)
    except Exception as e:
        logging.exception("Error in add_memory:")  # This will log the full traceback
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", summary="Get memories")
def get_all_memories(
        organization: str,
        contact_id: int,
):
    """Retrieve stored memories."""
    try:
        return memory_instance.get_all(
            user_id=get_user_id(organization, contact_id),
        )
    except Exception as e:
        logging.exception("Error in get_all_memories:")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{memory_id}", summary="Get a memory")
def get_memory(memory_id: str):
    """Retrieve a specific memory by ID."""
    try:
        return memory_instance.get(memory_id)
    except Exception as e:
        logging.exception("Error in get_memory:")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search", summary="Search memories")
def search_memories(organization: str,
                    contact_id: int,
                    search_req: SearchRequest):
    """Search for memories based on a query."""
    try:
        return memory_instance.search(query=search_req.query,
                                      user_id=get_user_id(organization, contact_id))
    except Exception as e:
        logging.exception("Error in search_memories:")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{memory_id}", summary="Update a memory")
def update_memory(memory_id: str, updated_memory: Dict[str, Any]):
    """Update an existing memory."""
    try:
        return memory_instance.update(memory_id=memory_id, data=updated_memory)
    except Exception as e:
        logging.exception("Error in update_memory:")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{memory_id}/history", summary="Get memory history")
def memory_history(memory_id: str):
    """Retrieve memory history."""
    try:
        return memory_instance.history(memory_id=memory_id)
    except Exception as e:
        logging.exception("Error in memory_history:")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{memory_id}", summary="Delete a memory")
def delete_memory(memory_id: str):
    """Delete a specific memory by ID."""
    try:
        memory_instance.delete(memory_id=memory_id)
        return {"message": "Memory deleted successfully"}
    except Exception as e:
        logging.exception("Error in delete_memory:")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/", summary="Delete all memories")
def delete_all_memories(
        organization: str,
        contact_id: int
):
    """Delete all memories for a given identifier."""
    try:
        memory_instance.delete_all(user_id=get_user_id(organization, contact_id))
        return {"message": "All relevant memories deleted"}
    except Exception as e:
        logging.exception("Error in delete_all_memories:")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset", summary="Reset all memories")
def reset_memory():
    """Completely reset stored memories."""
    try:
        memory_instance.reset()
        return {"message": "All memories reset"}
    except Exception as e:
        logging.exception("Error in reset_memory:")
        raise HTTPException(status_code=500, detail=str(e))
