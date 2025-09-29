from typing import List

from gql import gql

from farmwise.farmbetter import FarmBetterAPIError, farmbetter_client
from farmwise.farmbetter.models import GetGqAllConceptsResponse, GqConceptDto

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


async def get_concepts() -> List[GqConceptDto]:
    """Fetch concepts from the FarmBetter GraphQL API."""

    async with farmbetter_client as session:
        result = await session.execute(GET_CONCEPTS_QUERY)

    response = result["getConcepts"]
    if response["status"] != 200:
        raise FarmBetterAPIError(response.get("message", "Unknown error"))

    return GetGqAllConceptsResponse(**response).payload
