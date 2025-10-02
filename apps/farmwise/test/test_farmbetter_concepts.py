import pytest

from farmwise.farmbetter import FarmBetterAPIError
from farmwise.farmbetter.concepts import CACHE_KEY, get_concepts
from farmwise.farmbetter.models import GetGqAllConceptsResponse, GqConceptDto


class _DummyRedis:
    def __init__(self):
        self.storage: dict[str, str] = {}

    async def get(self, key: str):
        return self.storage.get(key)

    async def set(self, key: str, value: str, ex: int | None = None):
        self.storage[key] = value


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
    dummy_redis = _DummyRedis()
    monkeypatch.setattr("farmwise.farmbetter.concepts.redis", dummy_redis)

    response = await get_concepts()

    assert len(response) == 1
    assert response[0].id == "concept-1"
    assert response[0].name == "Concept One"
    assert CACHE_KEY in dummy_redis.storage


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
    dummy_redis = _DummyRedis()
    monkeypatch.setattr("farmwise.farmbetter.concepts.redis", dummy_redis)

    with pytest.raises(FarmBetterAPIError) as exc:
        await get_concepts()

    assert "Failure" in str(exc.value)


@pytest.mark.asyncio
async def test_get_concepts_uses_cache(monkeypatch):
    cached_response = GetGqAllConceptsResponse(
        count=1,
        message="OK",
        status=200,
        payload=[GqConceptDto(id="cached", name="Cached Concept", parentId=None)],
    )

    dummy_redis = _DummyRedis()
    dummy_redis.storage[CACHE_KEY] = cached_response.model_dump_json()
    monkeypatch.setattr("farmwise.farmbetter.concepts.redis", dummy_redis)

    class _FailingFarmBetterClient:
        async def __aenter__(self):
            raise AssertionError("Should not call API when cache is populated")

        async def __aexit__(self, exc_type, exc_value, traceback):
            return False

    monkeypatch.setattr(
        "farmwise.farmbetter.concepts.farmbetter_client",
        _FailingFarmBetterClient(),
    )

    response = await get_concepts()

    assert len(response) == 1
    assert response[0].id == "cached"
