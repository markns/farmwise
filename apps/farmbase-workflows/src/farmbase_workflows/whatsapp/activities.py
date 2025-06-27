from sqlalchemy import insert
from sqlalchemy.ext.asyncio import async_sessionmaker
from temporalio import activity, workflow

from .shared import SimpleContact

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

        body_values = [
            Template.TextValue(s.replace("\n", " ").replace("\r", " ").replace("    ", " ")[:500]) for s in body_values
        ]
        resp: SentTemplate = await self.whatsapp.send_template(
            to=contact.phone_number,
            template=Template(
                name=template_name,
                language=Template.Language.ENGLISH,
                header=Template.TextValue(header.replace("\n", " ")) if header else None,
                body=body_values,
                # buttons=[
                #   Template.UrlButtonValue(value="iphone15"),
                #   Template.QuickReplyButtonData(data="unsubscribe_from_marketing_messages"),
                #   Template.QuickReplyButtonData(data="unsubscribe_from_all_messages"),
                # ],
            ),
        )

        # TODO: Log/alert when message sending failed.
        logger.info(f"Response for message to {contact.phone_number}: {resp}")

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

    @activity.defn
    async def save_message(self, contact: SimpleContact, text: str):
        from farmbase.auth.models import FarmbaseUserOrganization
        from farmbase.database.core import engine
        from farmbase.farm.models import FarmContact
        from farmbase.contact.message.models import Message

        # TODO: fake import
        FarmbaseUserOrganization.organization
        FarmContact.id

        organization = "default"
        schema = f"farmbase_organization_{organization}"
        schema_engine = engine.execution_options(schema_translate_map={None: schema})
        async_session_factory = async_sessionmaker(
            bind=schema_engine,
            expire_on_commit=False,
        )

        async with async_session_factory() as session:
            stmt = insert(Message).values(contact_id=contact.id, text=text).returning(Message.id)
            result = await session.execute(stmt)
            new_id = result.scalar_one()
            await session.commit()
            return new_id
