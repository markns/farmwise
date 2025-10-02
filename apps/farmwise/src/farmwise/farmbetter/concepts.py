from __future__ import annotations

from typing import List

from gql import gql
from upstash_redis.asyncio import Redis

from farmwise.farmbetter import FarmBetterAPIError, farmbetter_client
from farmwise.farmbetter.models import GetGqAllConceptsResponse, GqConceptDto
from farmwise.settings import settings

GET_CONCEPTS_QUERY = gql(
    """
    query GetConcepts {
      getConcepts {
        count
        message
        payload {
          id
          name
          parentId
        }
        status
      }
    }
    """
)

CACHE_KEY = f"{settings.ENV}:farmbetter:concepts"
CACHE_TTL_SECONDS = 24 * 60 * 60

redis = Redis(url=settings.UPSTASH_REDIS_REST_URL, token=settings.UPSTASH_REDIS_REST_TOKEN)


async def get_concepts() -> List[GqConceptDto]:
    """Fetch concepts from the FarmBetter GraphQL API."""

    cached = await redis.get(CACHE_KEY)
    if cached is not None:
        cached_response = GetGqAllConceptsResponse.model_validate_json(cached)
        return cached_response.payload

    async with farmbetter_client as session:
        result = await session.execute(GET_CONCEPTS_QUERY)

    response = result["getConcepts"]
    if response["status"] != 200:
        raise FarmBetterAPIError(response.get("message", "Unknown error"))

    parsed_response = GetGqAllConceptsResponse(**response)
    await redis.set(CACHE_KEY, parsed_response.model_dump_json(), ex=CACHE_TTL_SECONDS)

    return parsed_response.payload
