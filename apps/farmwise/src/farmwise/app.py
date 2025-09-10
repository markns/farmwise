import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger
from loguru_logging_intercept import setup_loguru_logging_intercept
from pywa_async import WhatsApp

from farmwise.settings import settings
from farmwise.whatsapp import commands, handlers

logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    filter={
        "httpcore": False,
    },
    level="DEBUG",
)

# Intercept standard logging and route to loguru
setup_loguru_logging_intercept(level=logging.DEBUG)


@asynccontextmanager
async def lifespan(_):
    logger.info("Startup: Initializing resources...")
    logger.info(f"Whatsapp phone ID: {wa.phone_id}")
    # Ice breakers don't allow emojis when set via API, so set these in the WhatsApp Manager
    # ice_breakers = [
    #     "🌻 What crops are suitable for my area",
    #     "🌤️ Give me a weather forecast",
    #     "🌱 Calculate fertilizer for my field",
    # ]
    # TODO: It's all or nothing with conversational automation, so we can't set commands and not ice breakers
    await wa.update_conversational_automation(
        enable_chat_opened=True,
        # ice_breakers=ice_breakers,
        commands=commands.commands,
    )

    yield  # Run the application
    print("Shutdown: Cleaning up resources...")


app = FastAPI(debug=settings.is_dev(), lifespan=lifespan)

wa = WhatsApp(
    phone_id=settings.WHATSAPP_PHONE_ID,
    token=settings.WHATSAPP_TOKEN,
    server=app,
    callback_url=settings.WHATSAPP_CALLBACK_URL,
    verify_token=settings.WHATSAPP_VERIFY_TOKEN,
    app_id=settings.WHATSAPP_APP_ID,
    app_secret=settings.WHATSAPP_APP_SECRET,
    handlers_modules=[
        handlers,
        # profile_edit_handlers
    ],
    business_account_id=settings.WHATSAPP_BUSINESS_ACCOUNT_ID,
    # business_private_key=settings.WHATSAPP_BUSINESS_PRIVATE_KEY,
    # business_private_key_password=settings.WHATSAPP_BUSINESS_PRIVATE_KEY_PASSWORD,
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
