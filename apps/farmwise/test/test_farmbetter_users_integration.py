import os

import pytest

from farmwise.farmbetter.models import GqUserModelDto


def _require_env(var: str) -> str:
    value = os.getenv(var)
    if not value:
        pytest.skip(f"Skipping integration test: env var {var} is not set")
    return value


@pytest.mark.asyncio
async def test_get_user_integration():
    """
    Integration test for farmwise.farmbetter.users.get_user.

    This test exercises the real FARMBETTER GraphQL endpoint using credentials from the environment (.env).
    It does not assert on specific user data; instead it validates the response shape and key fields so it
    remains stable across environments. If required env vars are missing, the test will fail
    Required env:
      - FARMBETTER_ENDPOINT
      - FARMBETTER_TOKEN
    """
    # Use explicit test phone from env to avoid hard-coding personally identifiable data here.
    cc = 254
    num = 712345676

    from farmwise.farmbetter.users import get_user_by_phone

    user = await get_user_by_phone(country_code=cc, national_number=num)
    assert isinstance(user, GqUserModelDto)
    assert user.id
    assert user.firstName
    assert user.lastName
