from agents import Agent, RunContextWrapper
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
from pywa.types import Section, SectionRow

from farmwise.agent.prompt_utils import get_profile_and_memories
from farmwise.context import UserContext
from farmwise.schema import SectionList, TextResponse
from farmwise.tools.farmbase import get_market_price_snapshot, get_markets


def market_price_agent_instructions(ctx: RunContextWrapper[UserContext], agent: Agent[UserContext]) -> str:
    from farmwise.whatsapp.activities import activities

    markets_list = SectionList(
        button_title="Select market",
        sections=[
            Section(
                title="Nearby Markets",
                rows=[
                    # The LLM should replace these placeholders with actual market names and IDs
                    SectionRow(title="Market A", callback_data="1"),
                    SectionRow(title="Market B", callback_data="2"),
                ],
            )
        ],
    )
    return f"""{RECOMMENDED_PROMPT_PREFIX}
System Prompt for Market Price Agent

Role Definition:
You are an agent that presents market price information to farmers based on their farm location and interests.

Workflow:
1. Check if the user's farm coordinates are available in the user details below; if not, request the location 
   by adding the request_location action to the response.
2. Once coordinates are available, call the get_markets tool with the latitude and longitude to retrieve local markets.
3. Present the list of markets using a SectionList in the response:
   {markets_list}
4. Wait for the user to select a market by its callback_data.
5. Upon selection, call the get_market_price_snapshot tool with the selected market ID.
6. If the user has product_interests defined in their profile (ctx.context.contact.product_interests), filter the 
   snapshot to those products and show each with its current price and a brief trend summary if available 
   (e.g., “↑5%” for an increase).
   Otherwise, show the current price for all products in the market.
7. Format the price information clearly in the response content, for example:
   Tomato: 300 KES/kg (↑5% from last week)
   Onion: 50 KES/kg (↔0% change)
8. After completing this workflow ask if the user would like prices for other products or from other markets, and
   add the following section list to the response to offer the user a new list of activities: {activities}

{get_profile_and_memories(ctx.context)}
"""


market_price_agent: Agent[UserContext] = Agent(
    name="Market Price Agent",
    handoff_description="Provides current market prices based on farm location and product interests.",
    instructions=market_price_agent_instructions,
    tools=[get_markets, get_market_price_snapshot],
    output_type=TextResponse,
    model="gpt-4.1",
)
