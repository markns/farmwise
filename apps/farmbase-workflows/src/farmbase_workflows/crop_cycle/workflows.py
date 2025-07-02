from datetime import datetime, timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

from ..whatsapp.activities import WhatsAppActivities
from ..whatsapp.shared import SimpleContact
from .activities import CropCycleActivities
from .schema import CropCycleEvent


@workflow.defn
class CropCycleWorkflow:
    def __init__(self):
        self._sent_events: set[str] = set()

    @workflow.run
    async def run(
        self, contact: SimpleContact, planting_date: datetime, events: list[CropCycleEvent], demo: bool = False
    ) -> str:
        retry_policy = RetryPolicy(
            maximum_attempts=3,
            maximum_interval=timedelta(seconds=2),
            non_retryable_error_types=[],
        )

        # Sort events by start_day
        events.sort(key=lambda x: x.start_day)

        current_date = workflow.now()

        # Calculate which events should have already been sent
        for event in events:
            event_start_date = planting_date + timedelta(days=event.start_day)
            event_end_date = planting_date + timedelta(days=event.end_day)
            # If current date is within the event window, and we haven't sent it
            if (
                current_date >= event_start_date
                and current_date <= event_end_date
                and event.identifier not in self._sent_events
            ):
                # Send the message immediately for events we've missed or are currently in
                await self._send_event_message(contact, event, retry_policy)
                self._sent_events.add(event.identifier)

        # Now schedule future events
        for event in events:
            if event.identifier in self._sent_events:
                continue

            if demo:
                info = workflow.info()
                event_start_date = info.start_time + timedelta(minutes=event.start_day)
            else:
                event_start_date = planting_date + timedelta(days=event.start_day)

            # If the event is in the future, sleep until the start date
            if current_date < event_start_date:
                sleep_duration = event_start_date - current_date
                await workflow.sleep(sleep_duration)

                # Send the message
                await self._send_event_message(contact, event, retry_policy)
                self._sent_events.add(event.identifier)

        return f"Crop cycle workflow completed for contact {contact.name}"

    async def _send_event_message(self, contact: SimpleContact, event: CropCycleEvent, retry_policy: RetryPolicy):
        """Send WhatsApp template message for a crop cycle event"""

        await workflow.execute_activity_method(
            WhatsAppActivities.send_whatsapp_template,
            args=[
                contact,
                "harvesting",
                event.title,
                [
                    event.event_type,
                    event.identifier.split("_")[0],  # todo: this is a hack
                    event.description.replace("\n", "\r"),
                ],
            ],
            start_to_close_timeout=timedelta(seconds=10),
            retry_policy=retry_policy,
        )

        # Log that the event was sent
        await workflow.execute_activity_method(
            CropCycleActivities.log_event_sent,
            args=[contact.id, event.identifier, event.title],
            start_to_close_timeout=timedelta(seconds=5),
            retry_policy=retry_policy,
        )
