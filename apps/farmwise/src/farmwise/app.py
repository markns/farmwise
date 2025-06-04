# from agents import set_default_openai_key
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pywa_async import WhatsApp

from farmwise.settings import settings
from farmwise.whatsapp import handlers

# set_default_openai_key(settings.OPENAI_API_KEY.get_secret_value())


@asynccontextmanager
async def lifespan(_):
    print("Startup: Initializing resources...")
    print(f"Whatsapp phone ID: {wa.phone_id}")
    # Ice breakers don't allow emojis when set via API, so set these in the WhatsApp Manager
    # ice_breakers = [
    #     "🌻 What crops are suitable for my area",
    #     "🌤️ Give me a weather forecast",
    #     "🌱 Calculate fertilizer for my field",
    # ]
    # TODO: It's all or nothing with conversational automation, so we can't set commands and not ice breakers
    # await wa.update_conversational_automation(
    #     enable_chat_opened=True,
    #     # ice_breakers=ice_breakers,
    #     commands=[command.value for command in Commands],
    # )

    yield  # Run the application
    print("Shutdown: Cleaning up resources...")


app = FastAPI(debug=settings.is_dev(), lifespan=lifespan)

wa = WhatsApp(
    phone_id=settings.WHATSAPP_PHONE_ID,  # The phone id you got from the API Setup
    token=settings.WHATSAPP_TOKEN,  # The token you got from the API Setup
    server=app,
    callback_url=settings.WHATSAPP_CALLBACK_URL,
    verify_token="xyz123fdsfds",
    app_id=1392339421934377,
    app_secret="b8a5543a9bf425a0e87676641569b2b4",
    handlers_modules=[handlers],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
