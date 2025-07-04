import asyncio
from agents import Agent, run_demo_loop

# https://openai.github.io/openai-agents-python/repl/
async def main() -> None:
    from farmwise.agent import triage_agent
    # agent = Agent(name="Assistant", instructions="You are a helpful assistant.")
    await run_demo_loop(triage_agent)

if __name__ == "__main__":
    asyncio.run(main())