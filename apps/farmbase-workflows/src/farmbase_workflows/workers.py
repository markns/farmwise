import asyncio
import signal

from pywa_async import WhatsApp
from temporalio.client import Client

from farmbase_workflows.crop_cycle.worker import crop_cycle_worker
from farmbase_workflows.pest_alert.worker import pest_alert_worker
from farmbase_workflows.weather.worker import weather_worker


async def run_all(client: Client, whatsapp: WhatsApp):
    # 1. Create a global event to signal interruption
    interrupt_event = asyncio.Event()
    loop = asyncio.get_running_loop()

    # The signal handler just sets the event
    def handle_interrupt(sig_):
        print(f"Received signal {sig_}, initiating shutdown...")
        loop.call_soon_threadsafe(interrupt_event.set)

    # 2. Add signal handlers for graceful shutdown on SIGINT (ctrl+c) and SIGTERM
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, handle_interrupt, sig)

    # --- Instantiate your activities and workers ---

    # List of all workers to manage
    workers = [
        pest_alert_worker(client, whatsapp),
        weather_worker(client, whatsapp),
        crop_cycle_worker(client, whatsapp),
    ]

    try:
        print("All workers starting...")
        # 3. Use asyncio.gather to run all workers concurrently
        worker_run_tasks = [w.run() for w in workers]
        run_task = asyncio.gather(*worker_run_tasks)
        # Create a Task for the interrupt event so asyncio.wait can monitor it
        interrupt_task = asyncio.create_task(interrupt_event.wait())

        # Wait for the interrupt event OR for a worker to fail
        await asyncio.wait([run_task, interrupt_task],
                           return_when=asyncio.FIRST_COMPLETED)

    finally:
        print("Shutting down workers...")
        # 4. Use asyncio.gather to shut down all workers concurrently
        await asyncio.gather(*(w.shutdown() for w in workers))
        print("Workers shut down.")
