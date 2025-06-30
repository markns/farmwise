from upstash_redis.asyncio import Redis

from farmwise.context import UserContext
from farmwise.schema import SessionState
from farmwise.settings import settings

redis = Redis(url=settings.UPSTASH_REDIS_REST_URL, token=settings.UPSTASH_REDIS_REST_TOKEN)


def get_state_key(context: UserContext):
    return f"session:{context.contact.organization.slug}:{context.contact.phone_number}"


async def get_session_state(context: UserContext) -> SessionState | None:
    key = get_state_key(context)
    raw = await redis.get(key)

    if raw is not None:
        return SessionState.model_validate_json(raw)
    return None


async def set_session_state(context: UserContext, session_state: SessionState):
    key = get_state_key(context)
    await redis.set(key, session_state.model_dump_json(), ex=settings.SESSION_TTL_SECS)
