from google.adk.agents import Agent

# from farmwise.tools.farmbase import get_market_price_snapshot, get_markets
from .prompt import market_price_agent_instructions

market_price_agent = Agent(
    name="market_price_agent",
    description="Provides current market prices based on farm location and product interests.",
    instruction=market_price_agent_instructions,
    # tools=[get_markets, get_market_price_snapshot],
    model="gemini-2.5-flash",
)
