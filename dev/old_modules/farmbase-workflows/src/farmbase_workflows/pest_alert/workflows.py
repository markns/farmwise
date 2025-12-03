from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

from .activities import AlertActivities
from ..whatsapp.activities import WhatsAppActivities

# Always pass through external modules to the sandbox that you know are safe for
# workflow use
with workflow.unsafe.imports_passed_through():
    pass


@workflow.defn(name="pest-alert")
class PestAlertWorkflow:
    @workflow.run
    async def run(self) -> str:
        """
        Main workflow that:
        1. Finds notes created in the last hour
        2. For each note, finds nearby farms within 5km
        3. Generates alert messages using OpenAI
        4. Sends alerts to contacts associated with nearby farms
        """
        retry_policy = RetryPolicy(
            maximum_attempts=3,
            maximum_interval=timedelta(seconds=2),
            non_retryable_error_types=[],
        )

        # Step 1: Get recent notes
        recent_notes = await workflow.execute_activity_method(
            AlertActivities.get_recent_notes,
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=retry_policy,
        )

        if not recent_notes:
            return "No recent notes found in the last 24 hours"

        total_alerts_sent = 0
        notes_processed = 0

        # Step 2-4: Process each note
        for note_details in recent_notes:
            print(f"Processing note: {note_details}")
            # Find nearby farms
            nearby_farms = await workflow.execute_activity_method(
                AlertActivities.find_nearby_farms,
                args=[note_details, 5.0],  # 5km radius
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=retry_policy,
            )

            print(f"Found {len(nearby_farms)} nearby farms: {nearby_farms}")
            if not nearby_farms:
                continue  # Skip if no nearby farms found

            # Generate alert message using OpenAI
            alert_message = await workflow.execute_activity_method(
                AlertActivities.generate_alert_message,
                args=[note_details],
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=retry_policy,
            )

            for farm in nearby_farms:
                for contact in farm.contacts:

                    # TODO: Use subscriptions here
                    if contact.phone_number.startswith("X"):
                        continue

                    body_vars = [
                        alert_message.summary,
                        alert_message.actions.replace("\n", " "),
                        "2"  # TODO: actual distance
                    ]

                    print(body_vars)
                    await workflow.execute_activity_method(
                        WhatsAppActivities.send_whatsapp_template,
                        args=[contact, "crop_pest_alert", alert_message.header, body_vars],
                        start_to_close_timeout=timedelta(seconds=10),
                    )

                    total_alerts_sent += 1
            notes_processed += 1

        return f"Processed {notes_processed} notes and sent {total_alerts_sent} alerts"
