from typing import Any

from agents import Agent, RunContextWrapper, RunHooks, Tool, Usage
from loguru import logger

from farmwise.context import UserContext


class AgentHooks(RunHooks):
    def __init__(self):
        self.event_counter = 0

    def _usage_to_str(self, usage: Usage) -> str:
        return f"{usage.requests} requests, {usage.input_tokens} input tokens, {usage.output_tokens} output tokens, {usage.total_tokens} total tokens"

    async def on_agent_start(self, context: RunContextWrapper[UserContext], agent: Agent) -> None:
        self.event_counter += 1
        logger.info(f"### {self.event_counter}: Agent {agent.name} started. Usage: {self._usage_to_str(context.usage)}")

    async def on_agent_end(self, context: RunContextWrapper[UserContext], agent: Agent, output: Any) -> None:
        self.event_counter += 1
        logger.info(
            f"### {self.event_counter}: Agent {agent.name} ended with output {output}. Usage: {self._usage_to_str(context.usage)}"
        )

    async def on_tool_start(self, context: RunContextWrapper[UserContext], agent: Agent, tool: Tool) -> None:
        self.event_counter += 1
        logger.info(f"### {self.event_counter}: Tool {tool.name} started. Usage: {self._usage_to_str(context.usage)}")

    async def on_tool_end(self, context: RunContextWrapper[UserContext], agent: Agent, tool: Tool, result: str) -> None:
        self.event_counter += 1
        logger.info(
            f"### {self.event_counter}: Tool {tool.name} ended with result {result}. Usage: {self._usage_to_str(context.usage)}"
        )

    async def on_handoff(self, context: RunContextWrapper[UserContext], from_agent: Agent, to_agent: Agent) -> None:
        self.event_counter += 1
        logger.info(
            f"### {self.event_counter}: Handoff from {from_agent.name} to {to_agent.name}. Usage: {self._usage_to_str(context.usage)}"
        )


hooks = AgentHooks()

# await Runner.run(
#     start_agent,
#     hooks=hooks,
#     input=f"Generate a random number between 0 and {user_input}.",
# )
