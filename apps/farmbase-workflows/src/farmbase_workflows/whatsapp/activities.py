
from sqlalchemy.ext.asyncio import async_sessionmaker
from temporalio import activity, workflow


from .schema import SimpleContact

# Always pass through external modules to the sandbox that you know are safe for
# workflow use
with workflow.unsafe.imports_passed_through():
    from pywa_async import WhatsApp


class WhatsAppActivities:
    def __init__(self, whatsapp_client: WhatsApp):
        self.whatsapp = whatsapp_client

    @activity.defn
    async def send_whatsapp_template(
            self, contact: SimpleContact, template_name: str, header: str, body_values: list[str]
    ):
        from loguru import logger
        from pywa_async.types import Template
        from pywa_async.types.sent_message import SentTemplate
        from farmbase.database.core import engine
        from farmbase.contact.message.service import create
        from datetime import datetime, UTC
        from farmbase.contact.message.models import MessageDirection, MessageType
        from farmbase.contact.message.schemas import MessageCreate

        body_values = [
            Template.TextValue(s.replace("\n", " ").replace("\r", " ").replace("    ", " ")[:500]) for s in body_values
        ]
        template = Template(
                name=template_name,
                language=Template.Language.ENGLISH,
                header=Template.TextValue(header.replace("\n", " ")) if header else None,
                body=body_values,
            )

        sent_template: SentTemplate = await self.whatsapp.send_template(
            to=contact.phone_number,
            template=template
        )

        # TODO: Log/alert when message sending failed.
        logger.info(f"Response for message to {contact.phone_number}: {sent_template}")

        organization = "default"
        schema = f"farmbase_organization_{organization}"
        schema_engine = engine.execution_options(schema_translate_map={None: schema})
        async_session_factory = async_sessionmaker(
            bind=schema_engine,
            expire_on_commit=False,
        )

        async with async_session_factory() as session:
            await create(db_session=session,
                         message_in=MessageCreate(
                             contact_id=contact.id,
                             direction=MessageDirection.OUTBOUND,
                             whatsapp_message_id=sent_template.id,
                             timestamp=datetime.now(UTC),
                             type=MessageType.TEXT,
                             text=str(template),
                         ))

    @activity.defn
    async def send_whatsapp_message(self, contact: SimpleContact, message: str):
        from loguru import logger
        from pywa_async.types.sent_message import SentMessage

        resp: SentMessage = await self.whatsapp.send_message(
            to=contact.phone_number,
            text=message,
        )

        # TODO: Log/alert when message sending failed.
        logger.info(f"Response for message to {contact.phone_number}: {resp}")
