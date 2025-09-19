from async_lru import alru_cache
from loguru import logger

# OpenAI Agents SDK imports
from zep_cloud import Message, NotFoundError

# Zep Cloud imports
from zep_cloud.client import AsyncZep

from farmwise.farmbetter.users import User
from farmwise.settings import settings

zep_client = AsyncZep(api_key=settings.ZEP_API_KEY.get_secret_value())


@alru_cache(maxsize=100)
async def get_or_create_user(user: User):
    # Create or get the user
    try:
        # Try to get the user first
        return await zep_client.user.get(user.wa_id)

    except NotFoundError:
        new_user = await zep_client.user.add(
            user_id=user.wa_id,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
        )
        logger.info(f"Created new Zep user {new_user}")
        return new_user


async def create_thread(thread_id: str, user: User):
    zep_user = await get_or_create_user(user)

    await zep_client.thread.create(thread_id=thread_id, user_id=zep_user.user_id)


async def add_messages(thread_id: str, messages: list[Message]):
    # message = Message(name=name, content=content, role=role)
    # logger.info(f"Adding zep message to thread {thread_id} {message}")
    await zep_client.thread.add_messages(thread_id, messages=messages, ignore_roles=["assistant"])


async def get_memory(thread_id) -> str:
    """
    Get the memory context string from Zep memory instead of creating a summary.

    Returns:
        A string containing the memory context from Zep.
    """
    try:
        # Use thread.get_user_context to retrieve memory context for the thread
        context = await zep_client.thread.get_user_context(thread_id=thread_id, mode="summary")

        # Use the context string provided by Zep instead of creating a summary
        if context.context:
            return context.context

        return "No conversation history yet."
    except NotFoundError:
        logger.error(f"Thread {thread_id} not found.")
        raise
    except Exception as e:
        logger.error(f"Error getting memory context: {e}")
        raise
