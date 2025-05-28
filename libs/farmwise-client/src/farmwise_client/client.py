import os
from typing import Any

import httpx
from farmwise_schema.schema import (
    ServiceMetadata,
    UserInput,
    WhatsAppResponse,
)


class AgentClientError(Exception):
    pass


class AgentClient:
    """Client for interacting with the agent service."""

    def __init__(
        self,
        base_url: str = "http://0.0.0.0",
        agent: str = None,
        timeout: float | None = None,
        get_info: bool = True,
    ) -> None:
        """
        Initialize the client.

        Args:
            base_url (str): The base URL of the agent service.
            agent (str): The name of the default agent to use.
            timeout (float, optional): The timeout for requests.
            get_info (bool, optional): Whether to fetch agent information on init.
                Default: True
        """
        self.base_url = base_url
        self.auth_secret = os.getenv("AUTH_SECRET")
        self.timeout = timeout
        self.info: ServiceMetadata | None = None
        self.agent: str | None = None
        if get_info:
            self.retrieve_info()
        if agent:
            self.update_agent(agent)

    @property
    def _headers(self) -> dict[str, str]:
        headers = {}
        if self.auth_secret:
            headers["Authorization"] = f"Bearer {self.auth_secret}"
        return headers

    def retrieve_info(self) -> None:
        try:
            response = httpx.get(
                f"{self.base_url}/info",
                headers=self._headers,
                timeout=self.timeout,
            )
            response.raise_for_status()
        except httpx.HTTPError as e:
            raise AgentClientError(f"Error getting service info: {e}")

        self.info: ServiceMetadata = ServiceMetadata.model_validate(response.json())
        if not self.agent or self.agent not in [a.key for a in self.info.agents]:
            self.agent = self.info.default_agent

    def update_agent(self, agent: str, verify: bool = True) -> None:
        if verify:
            if not self.info:
                self.retrieve_info()
            agent_keys = [a.key for a in self.info.agents]
            if agent not in agent_keys:
                raise AgentClientError(f"Agent {agent} not found in available agents: {', '.join(agent_keys)}")
        self.agent = agent

    async def invoke(
        self,
        message: str,
        user_id: str,
        image: str = None,
        voice: str = None,
        user_name: str | None = None,
        agent_config: dict[str, Any] | None = None,
    ) -> WhatsAppResponse:
        """
        Invoke the agent asynchronously. Only the final message is returned.

        Args:
            message (str): The message to send to the agent
            user_id (str): user ID for continuing a conversation
            image:
            user_name:
            agent_config (dict[str, Any], optional): Additional configuration to pass through to the agent

        Returns:
            AnyMessage: The response from the agent
        """
        if not self.agent:
            raise AgentClientError("No agent selected. Use update_agent() to select an agent.")
        request = UserInput(message=message, user_id=user_id, user_name=user_name)

        if agent_config:
            request.agent_config = agent_config
        if image:
            request.image = image
        if voice:
            request.voice = voice
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/invoke",
                    json=request.model_dump(mode="json"),
                    headers=self._headers,
                    timeout=self.timeout,
                )
                response.raise_for_status()
            except httpx.HTTPError as e:
                raise AgentClientError(f"Error: {e}")

        return WhatsAppResponse.model_validate(response.json())

    async def invoke_voice(
        self,
        user_id: str,
        voice: str,
        user_name: str | None = None,
        agent_config: dict[str, Any] | None = None,
    ) -> str:
        if not self.agent:
            raise AgentClientError("No agent selected. Use update_agent() to select an agent.")
        request = UserInput(voice=voice, user_id=user_id, user_name=user_name)

        if agent_config:
            request.agent_config = agent_config
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/invoke_voice",
                    json=request.model_dump(mode="json"),
                    headers=self._headers,
                    timeout=self.timeout,
                )
                response.raise_for_status()
            except httpx.HTTPError as e:
                raise AgentClientError(f"Error: {e}")

        return response.text
