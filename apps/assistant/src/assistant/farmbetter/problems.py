from __future__ import annotations

from typing import Sequence

from gql import gql
from loguru import logger

from assistant.farmbetter import FarmBetterAPIError, farmbetter_client
from assistant.farmbetter.models import CreateGqReportedProblemRequest, GqReportedProblemModelDto, GqTimelineEntryInput
from assistant.farmbetter.utils import strip_typename

CREATE_REPORTED_PROBLEM_MUTATION = gql(
    """
    mutation CreateReportedProblem($problem: CreateGqReportedProblemRequest!) {
        createReportedProblem(problem: $problem) {
            message
            status
            payload {
                id
                farmerId
                tenant
                status
                extensionAgent {
                    id
                    firstName
                    lastName
                }
                timeline {
                    audioMedia
                    created
                    documentMedia
                    from
                    media
                    message
                    reportedProblemId
                    videoMedia
                }
                
            }
        }
    }
    """
)


async def create_reported_problem(
    farmer_id: str,
    tenant_id: str,
    status: str,
    timeline: Sequence[GqTimelineEntryInput] | None = None,
) -> GqReportedProblemModelDto:
    """Create a reported problem via the FarmBetter GraphQL API."""

    problem = CreateGqReportedProblemRequest(status=status, farmerId=farmer_id, tenant=tenant_id, timeline=timeline)

    logger.info(f"Creating reported problem: {problem}")
    async with farmbetter_client as session:
        result = await session.execute(
            CREATE_REPORTED_PROBLEM_MUTATION,
            variable_values={"problem": strip_typename(problem.model_dump(exclude_none=True,
                                                                          by_alias=True))},
        )
    response = result["createReportedProblem"]
    if response["status"] != 200:
        raise FarmBetterAPIError(response.get("message", "Unknown error"))

    logger.info(f"Reported problem created: {response['payload']}")

    return GqReportedProblemModelDto(**response["payload"])
