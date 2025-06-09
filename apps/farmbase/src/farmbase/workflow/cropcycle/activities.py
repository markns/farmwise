from temporalio import activity

# Always pass through external modules to the sandbox that you know are safe for
# workflow use
# with workflow.unsafe.imports_passed_through():
#     pass


class CropCycleActivities:
    """Activities for crop cycle workflow operations"""

    @activity.defn
    async def log_event_sent(self, contact_id: int, event_identifier: str, event_title: str):
        """Log that an event message was sent to a contact"""
        from loguru import logger
        
        logger.info(f"Crop cycle event '{event_title}' (ID: {event_identifier}) sent to contact {contact_id}")
        
        # TODO: Could save to database for tracking purposes if needed
        return True