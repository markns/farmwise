import asyncio
import traceback
from uuid import uuid4

from temporalio import workflow
from temporalio.client import Client, WorkflowFailureError

from farmbase_workflows import weather
from farmbase_workflows.settings import settings
from workflows import SendWeatherWorkflow

with workflow.unsafe.imports_passed_through():
    from temporalio.contrib.pydantic import pydantic_data_converter


async def main() -> None:
    client: Client = await Client.connect(settings.TEMPORAL_ENDPOINT,
                                          data_converter=pydantic_data_converter)
    try:
        result = await client.execute_workflow(
            SendWeatherWorkflow.run,
            id=f"weather-forecast-{uuid4()}",
            task_queue=weather.TASK_QUEUE,
        )

        print(f"Result: {result}")

    except WorkflowFailureError:
        print("Got expected exception: ", traceback.format_exc())


if __name__ == "__main__":
    asyncio.run(main())
