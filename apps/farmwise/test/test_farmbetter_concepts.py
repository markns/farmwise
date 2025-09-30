import pytest

from farmwise.farmbetter import FarmBetterAPIError
from farmwise.farmbetter.concepts import get_concepts
from farmwise.farmbetter.models import GetGqAllConceptsResponse


class _DummyFarmBetterClient:
    def __init__(self, result):
        self._result = result

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        return False

    async def execute(self, query, variable_values=None):
        return self._result


@pytest.mark.asyncio
async def test_get_concepts_success(monkeypatch):
    dummy_response = {
        "getConcepts": {
            "count": 1,
            "message": "OK",
            "payload": [
                {
                    "id": "concept-1",
                    "name": "Concept One",
                    "parentId": None,
                }
            ],
            "status": 200,
        }
    }

    monkeypatch.setattr(
        "farmwise.farmbetter.concepts.farmbetter_client",
        _DummyFarmBetterClient(dummy_response),
    )

    response = await get_concepts()

    assert isinstance(response, GetGqAllConceptsResponse)
    assert response.count == 1
    assert response.payload[0].id == "concept-1"
    assert response.payload[0].name == "Concept One"


@pytest.mark.asyncio
async def test_get_concepts_error(monkeypatch):
    dummy_response = {
        "getConcepts": {
            "count": 0,
            "message": "Failure",
            "payload": [],
            "status": 500,
        }
    }

    monkeypatch.setattr(
        "farmwise.farmbetter.concepts.farmbetter_client",
        _DummyFarmBetterClient(dummy_response),
    )

    with pytest.raises(FarmBetterAPIError) as exc:
        await get_concepts()

    assert "Failure" in str(exc.value)
