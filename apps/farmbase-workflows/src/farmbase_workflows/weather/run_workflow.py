import asyncio
import traceback

from datetime import date
from temporalio import workflow
from temporalio.client import Client, WorkflowFailureError

from farmbase_workflows import weather
from farmbase_workflows.settings import settings

with workflow.unsafe.imports_passed_through():
    from temporalio.contrib.pydantic import pydantic_data_converter


async def main() -> None:
    client: Client = await Client.connect(settings.TEMPORAL_ENDPOINT,
                                          data_converter=pydantic_data_converter)
    try:
        result = await client.start_workflow(
            "weather-forecast",
            id=f"weather-forecast-{date.today()}",
            task_queue=weather.TASK_QUEUE,
        )

        print(f"Result: {result}")

    except WorkflowFailureError:
        print("Got expected exception: ", traceback.format_exc())


if __name__ == "__main__":
    asyncio.run(main())
