from datetime import timedelta
from textwrap import dedent

from temporalio import workflow
from temporalio.common import RetryPolicy

from ..whatsapp.activities import WhatsAppActivities
from .activities import AlertActivities

# Always pass through external modules to the sandbox that you know are safe for
# workflow use
with workflow.unsafe.imports_passed_through():
    pass


@workflow.defn
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
            return "No recent notes found in the last hour"

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
                # Format the complete alert message
                full_message = dedent(f"""
                🚨 FARM ALERT - {note_details.farm_name}

                {alert_message.summary}

                📋 RECOMMENDED ACTIONS:
                """)
                for i, action in enumerate(alert_message.actions, 1):
                    full_message += f"{i}. {action}\n"

                full_message += f"\n📍 Distance: {farm.distance_km}km from affected area"

                for contact in farm.contacts:
                    if contact.phone_number.startswith("X"):
                        continue

                    await workflow.execute_activity_method(
                        WhatsAppActivities.send_whatsapp_message,
                        args=[contact, full_message],
                        start_to_close_timeout=timedelta(seconds=10),
                    )

                    # Save new messages to db
                    await workflow.execute_activity_method(
                        WhatsAppActivities.save_message,
                        args=[contact, full_message],
                        start_to_close_timeout=timedelta(seconds=10),
                    )

                    total_alerts_sent += 1
            notes_processed += 1

        return f"Processed {notes_processed} notes and sent {total_alerts_sent} alerts"
