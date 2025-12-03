import asyncio

import httpx
from pywa_async import WhatsApp

from assistant.settings import settings
from assistant.whatsapp.flows.courses.courses import create_or_update_flows

if __name__ == "__main__":
    wa = WhatsApp(
        session=httpx.AsyncClient(timeout=10),
        # webhook_challenge_delay=60,
        phone_id=settings.WHATSAPP_PHONE_ID,
        token=settings.WHATSAPP_TOKEN,
        # server=app,
        # callback_url=settings.WHATSAPP_CALLBACK_URL,
        verify_token=settings.WHATSAPP_VERIFY_TOKEN,
        app_id=settings.WHATSAPP_APP_ID,
        app_secret=settings.WHATSAPP_APP_SECRET,
        # handlers_modules=[handlers, edit_profile_handlers],
        business_account_id=settings.WHATSAPP_BUSINESS_ACCOUNT_ID,
        business_private_key=settings.WHATSAPP_BUSINESS_PRIVATE_KEY,
        business_private_key_password=settings.WHATSAPP_BUSINESS_PRIVATE_KEY_PASSWORD,
    )

    asyncio.run(create_or_update_flows(wa))
