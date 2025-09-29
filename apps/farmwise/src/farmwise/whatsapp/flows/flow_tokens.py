from __future__ import annotations

import json
from dataclasses import dataclass

from upstash_redis.asyncio import Redis

from farmwise.settings import settings

_FLOW_TOKEN_TTL_SECONDS = 15 * 60  # 15 minutes gives users time to finish the flow


@dataclass(slots=True)
class FlowSession:
    wa_id: str
    name: str | None = None

    def to_json(self) -> str:
        return json.dumps({"wa_id": self.wa_id, "name": self.name})

    @classmethod
    def from_json(cls, raw: str) -> "FlowSession":
        data = json.loads(raw)
        return cls(wa_id=data["wa_id"], name=data.get("name"))


redis = Redis(url=settings.UPSTASH_REDIS_REST_URL, token=settings.UPSTASH_REDIS_REST_TOKEN)


def _make_key(flow_token: str) -> str:
    return f"{settings.ENV}:wa_flow:{flow_token}"


async def store_flow_session(flow_token: str, session: FlowSession, *, ttl_seconds: int = _FLOW_TOKEN_TTL_SECONDS) -> None:
    """Persist the flow session mapping so subsequent requests can resolve the WhatsApp user."""

    await redis.set(_make_key(flow_token), session.to_json(), ex=ttl_seconds)


async def get_flow_session(flow_token: str, *, touch_ttl: bool = True) -> FlowSession | None:
    """Fetch the stored mapping, optionally bumping the TTL so sessions stay alive while active."""

    key = _make_key(flow_token)
    raw = await redis.get(key)
    if raw is None:
        return None

    if touch_ttl:
        await redis.expire(key, _FLOW_TOKEN_TTL_SECONDS)

    return FlowSession.from_json(raw)


async def clear_flow_session(flow_token: str) -> None:
    """Remove stored session once the flow completes or is aborted."""

    await redis.delete(_make_key(flow_token))
