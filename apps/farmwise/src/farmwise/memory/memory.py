from farmbase_client.api.contacts import contacts_add_memory, contacts_get_all_memories
from farmbase_client.models import ContactRead, MemoryCreate, Message

from farmwise.farmbase import farmbase_api_client


# nb. this is not the function used in the user context currently
async def retrieve_memories(contact: ContactRead):
    memories = await contacts_get_all_memories.asyncio(
        organization=contact.organization.slug, contact_id=contact.id, client=farmbase_api_client
    )
    return memories.results


async def add_memory(contact: ContactRead, messages: list[Message]):
    memories = await contacts_add_memory.asyncio(
        organization=contact.organization.slug,
        contact_id=contact.id,
        client=farmbase_api_client,
        body=MemoryCreate(messages=messages, metadata=None),
    )
    return memories.results
