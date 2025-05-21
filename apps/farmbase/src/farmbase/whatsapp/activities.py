from sqlalchemy import insert
from sqlalchemy.ext.asyncio import async_sessionmaker
from temporalio import activity

from .shared import Contact


class WhatsAppActivities:
    def __init__(self, whatsapp_client):
        self.whatsapp = whatsapp_client

    @activity.defn
    async def send_whatsapp_template(self, contact: Contact, template_name: str, values: list[str]):
        from loguru import logger
        from pywa_async.types import Template
        from pywa_async.types.sent_message import SentTemplate

        resp: SentTemplate = await self.whatsapp.send_template(
            to=contact.phone_number,
            template=Template(
                name=template_name,
                language=Template.Language.ENGLISH,
                # header=Template.TextValue(value="15"),
                body=[Template.TextValue(s) for s in values],
                # buttons=[
                #   Template.UrlButtonValue(value="iphone15"),
                #   Template.QuickReplyButtonData(data="unsubscribe_from_marketing_messages"),
                #   Template.QuickReplyButtonData(data="unsubscribe_from_all_messages"),
                # ],
            ),
        )

        # TODO: Log/alert when message sending failed.
        logger.info(f"Response for message to {contact.phone_number}: {resp}")

        # TODO: Get message body somehow
        # return resp

    @activity.defn
    async def save_message(self, contact: Contact, text: str):
        from farmbase.auth.models import FarmbaseUserOrganization
        from farmbase.database.core import engine
        from farmbase.message.models import Message

        # TODO: fake import
        FarmbaseUserOrganization.organization

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
