from farmbase_client.api.contacts import contacts_get_all_memories, contacts_add_memory
from farmbase_client.models import ContactRead, MemoryCreate, Message
from farmwise.farmbase import FarmbaseClient


# nb. this is not the function used in the user context currently
async def retrieve_memories(contact: ContactRead):
    async with FarmbaseClient() as client:
        memories = await contacts_get_all_memories.asyncio(
            organization=contact.organization.slug,
            contact_id=contact.id,
            client=client.raw)
        return memories.results


async def add_memory(contact: ContactRead, messages: list[Message]):
    async with FarmbaseClient() as client:
        memories = await contacts_add_memory.asyncio(
            organization=contact.organization.slug,
            contact_id=contact.id,
            client=client.raw,
            body=MemoryCreate(messages=messages, metadata=None))
        return memories.results
