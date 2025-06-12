import asyncio
import traceback

from temporalio import workflow
from temporalio.client import Client, WorkflowFailureError
from workflows import SendWeatherWorkflow

from farmbase_workflows.weather.shared import DEFAULT_TASK_QUEUE

# Always pass through external modules to the sandbox that you know are safe for
# workflow use
with workflow.unsafe.imports_passed_through():
    from temporalio.contrib.pydantic import pydantic_data_converter


async def main() -> None:
    # Create client connected to server at the given address
    client: Client = await Client.connect("localhost:7233", data_converter=pydantic_data_converter)
    try:
        result = await client.execute_workflow(
            SendWeatherWorkflow.run,
            # "my schedule arg",
            id="schedules-workflow-id",
            task_queue=DEFAULT_TASK_QUEUE,
        )

        print(f"Result: {result}")

    except WorkflowFailureError:
        print("Got expected exception: ", traceback.format_exc())


if __name__ == "__main__":
    asyncio.run(main())
