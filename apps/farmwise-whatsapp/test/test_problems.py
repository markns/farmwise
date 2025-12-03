# File: tests/test_problems.py

from datetime import datetime

import pytest

from farmwise.farmbetter import FarmBetterAPIError
from farmwise.farmbetter.models import (
    CreateGqReportedProblemRequest,
    GqReportedProblemModelDto,
    GqTimelineEntryInput,
)
from farmwise.farmbetter.problems import TimelineEntry, create_reported_problem


@pytest.mark.asyncio
async def test_create_reported_problem_success(monkeypatch):
    async def mock_execute(*args, **kwargs):
        return {
            "createReportedProblem": {
                "status": 200,
                "message": "Reported problem created successfully.",
                "payload": {
                    "id": "problem-001",
                    "status": "pending",
                    "tenant": "tenant-001",
                    "timeline": [],
                },
            }
        }

    class MockClient:
        async def execute(self, *args, **kwargs):
            return await mock_execute(*args, **kwargs)

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

    monkeypatch.setattr("farmwise.farmbetter.problems.farmbetter_client", MockClient())

    problem_request = CreateGqReportedProblemRequest(
        id="problem-001",
        status="pending",
        tenant="tenant-001",
        timeline=[],
    )

    response = await create_reported_problem(problem_request)

    assert isinstance(response, GqReportedProblemModelDto)
    assert response.id == "problem-001"
    assert response.status == "pending"
    assert response.tenant == "tenant-001"
    assert response.timeline == []


@pytest.mark.asyncio
async def test_create_reported_problem():
    await create_reported_problem(
        "fa9d9bb7-2eb4-49e2-851c-931f03f502b3",
        "a920379c-415b-49e6-9318-86dd79f7840b",
        [
            GqTimelineEntryInput(
                created="2025-07-31T12:52:21.560Z", from_="fa9d9bb7-2eb4-49e2-851c-931f03f502b3", message="uh oh"
            ),
            GqTimelineEntryInput(
                created="2025-07-31T12:52:21.560Z", from_="fa9d9bb7-2eb4-49e2-851c-931f03f502b3", message="it's ok"
            ),
        ],
    )


@pytest.mark.asyncio
async def test_create_reported_problem_invalid_status(monkeypatch):
    async def mock_execute(*args, **kwargs):
        return {
            "createReportedProblem": {
                "status": 400,
                "message": "Invalid problem request.",
                "payload": {},
            }
        }

    class MockClient:
        async def execute(self, *args, **kwargs):
            return await mock_execute(*args, **kwargs)

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

    monkeypatch.setattr("farmwise.farmbetter.problems.farmbetter_client", MockClient())

    problem_request = CreateGqReportedProblemRequest(
        id="problem-002",
        status="invalid",
        tenant="tenant-002",
        timeline=[],
    )

    with pytest.raises(FarmBetterAPIError, match="Invalid problem request."):
        await create_reported_problem(problem_request)


@pytest.mark.asyncio
async def test_create_reported_problem_with_timeline(monkeypatch):
    async def mock_execute(*args, **kwargs):
        return {
            "createReportedProblem": {
                "status": 200,
                "message": "Reported problem created successfully.",
                "payload": {
                    "id": "problem-003",
                    "status": "pending",
                    "tenant": "tenant-003",
                    "timeline": [
                        {
                            "message": "Timeline entry message",
                            "created": "2023-10-01T10:00:00Z",
                            "media": [],
                        }
                    ],
                },
            }
        }

    class MockClient:
        async def execute(self, *args, **kwargs):
            return await mock_execute(*args, **kwargs)

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            pass

    monkeypatch.setattr("farmwise.farmbetter.problems.farmbetter_client", MockClient())

    problem_request = CreateGqReportedProblemRequest(
        id="problem-003",
        status="pending",
        tenant="tenant-003",
        timeline=[],
    )

    timeline_entries = [
        TimelineEntry(
            message="Timeline entry message",
            created=datetime(2023, 10, 1, 10, 0, 0),
            media=[],
        )
    ]

    response = await create_reported_problem(problem_request, timeline_entries)

    assert isinstance(response, GqReportedProblemModelDto)
    assert response.id == "problem-003"
    assert response.status == "pending"
    assert response.tenant == "tenant-003"
    assert len(response.timeline) == 1
    assert response.timeline[0]["message"] == "Timeline entry message"
    assert response.timeline[0]["created"] == "2023-10-01T10:00:00Z"
