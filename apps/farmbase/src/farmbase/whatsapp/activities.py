import os

from sqlalchemy import insert
from sqlalchemy.ext.asyncio import async_sessionmaker
from temporalio import activity

from .shared import Contact


class WhatsAppActivities:

    def __init__(self, whatsapp_client):
        self.whatsapp = whatsapp_client

    @activity.defn
    async def send_whatsapp_message(self, contact: Contact, message: str):
        from loguru import logger

        # TODO: This should be a template message: https://pywa.readthedocs.io/en/latest/content/examples/template.html
        resp = await self.whatsapp.send_message(to=contact.phone_number, text=message)
        # TODO: Log/alert when message sending failed.
        logger.info(f"Response for message to {contact.phone_number}: {resp}")

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
