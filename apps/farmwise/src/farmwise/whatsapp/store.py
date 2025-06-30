from dataclasses import asdict
from datetime import datetime, UTC

from pywa_async.types import CallbackSelection, CallbackButton
from pywa_async.types.message import Message
from pywa_async.types.sent_message import SentMessage

from farmbase_client.api.contacts import contacts_create_message
from farmbase_client.models import ContactRead, MessageCreate, MessageDirection, MessageType
from farmwise.farmbase import FarmbaseClient
from farmwise.whatsapp.utils import asdict_with_exclusions


async def record_outbound_message(contact: ContactRead, msg: SentMessage, text):
    async with FarmbaseClient() as client:
        await contacts_create_message.asyncio(contact.organization.slug,
                                              contact_id=contact.id,
                                              client=client.raw,
                                              body=MessageCreate(
                                                  direction=MessageDirection.OUTBOUND,
                                                  whatsapp_message_id=msg.id,
                                                  timestamp=datetime.now(UTC),
                                                  type=MessageType.TEXT,
                                                  text=text,
                                                  contact_id=contact.id
                                              ))


async def record_inbound_message(contact: ContactRead, msg: Message, storage: dict = None):
    async with FarmbaseClient() as client:
        await contacts_create_message.asyncio(organization=contact.organization.slug,
                                              contact_id=contact.id,
                                              client=client.raw,
                                              body=MessageCreate(
                                                  direction=MessageDirection.INBOUND,
                                                  whatsapp_message_id=msg.id,
                                                  timestamp=msg.timestamp,
                                                  type=msg.type,
                                                  forwarded=msg.forwarded,
                                                  forwarded_many_times=msg.forwarded_many_times,
                                                  text=msg.text,
                                                  caption=msg.caption,
                                                  image=asdict_with_exclusions(msg.image, excluded={"_client"}),
                                                  video=asdict_with_exclusions(msg.video, excluded={"_client"}),
                                                  sticker=asdict_with_exclusions(msg.sticker, excluded={"_client"}),
                                                  document=asdict_with_exclusions(msg.document, excluded={"_client"}),
                                                  audio=asdict_with_exclusions(msg.audio, excluded={"_client"}),
                                                  storage=storage,
                                                  reaction=msg.reaction,
                                                  location=msg.location,
                                                  contacts=msg.contacts,
                                                  order=msg.order,
                                                  system=msg.system,
                                                  metadata=asdict(msg.metadata),
                                                  from_user={"wa_id": msg.from_user.wa_id,
                                                             "name": msg.from_user.name},
                                                  reply_to_message=msg.reply_to_message,
                                                  error=msg.error,
                                                  contact_id=contact.id
                                              ))


async def record_callback_selection(contact: ContactRead, sel: CallbackSelection):
    async with FarmbaseClient() as client:
        await contacts_create_message.asyncio(organization=contact.organization.slug,
                                              contact_id=contact.id,
                                              client=client.raw,
                                              body=MessageCreate(
                                                  direction=MessageDirection.INBOUND,
                                                  whatsapp_message_id=sel.id,
                                                  timestamp=sel.timestamp,
                                                  type=sel.type,
                                                  metadata=asdict(sel.metadata),
                                                  from_user={"wa_id": sel.from_user.wa_id,
                                                             "name": sel.from_user.name},
                                                  reply_to_message=asdict(sel.reply_to_message),
                                                  data=sel.data,
                                                  title=sel.title,
                                                  description=sel.description,
                                                  contact_id=contact.id
                                              ))


async def record_callback_button(contact: ContactRead, button: CallbackButton):
    async with FarmbaseClient() as client:
        await contacts_create_message.asyncio(organization=contact.organization.slug,
                                              contact_id=contact.id,
                                              client=client.raw,
                                              body=MessageCreate(
                                                  direction=MessageDirection.INBOUND,
                                                  whatsapp_message_id=button.id,
                                                  timestamp=button.timestamp,
                                                  type=button.type,
                                                  metadata=asdict(button.metadata),
                                                  from_user={"wa_id": button.from_user.wa_id,
                                                             "name": button.from_user.name},
                                                  reply_to_message=asdict(button.reply_to_message),
                                                  data=button.data,
                                                  title=button.title,
                                                  contact_id=contact.id
                                              ))
