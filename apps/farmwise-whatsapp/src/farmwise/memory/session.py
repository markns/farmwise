import uuid

from pydantic import BaseModel
from upstash_redis.asyncio import Redis

from farmwise.agent import DEFAULT_AGENT
from farmwise.context import UserContext
from farmwise.memory.zep import create_thread
from farmwise.settings import settings

redis = Redis(url=settings.UPSTASH_REDIS_REST_URL, token=settings.UPSTASH_REDIS_REST_TOKEN)


def get_state_key(context: UserContext):
    return f"{settings.ENV}:session:{context.user.wa_id}"


class SessionState(BaseModel):
    current_agent: str = DEFAULT_AGENT
    thread_id: str
    previous_response_id: str | None = None


async def get_or_create_session(context: UserContext) -> SessionState | None:
    key = get_state_key(context)
    raw = await redis.get(key)

    if raw is not None:
        return SessionState.model_validate_json(raw)

    thread_id = uuid.uuid4().hex
    await create_thread(thread_id, context.user)

    session_state = SessionState(thread_id=thread_id)
    await redis.set(key, session_state.model_dump_json(), ex=settings.SESSION_TTL_SECS)

    return session_state


async def set_session_state(context: UserContext, session_state: SessionState):
    key = get_state_key(context)
    await redis.set(key, session_state.model_dump_json(), ex=settings.SESSION_TTL_SECS)


async def clear_session_state(context: UserContext):
    key = get_state_key(context)
    await redis.delete(key)
