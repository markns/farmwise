import os

from pywa_async import WhatsApp, filters, types
from fastapi import FastAPI

fastapi_app = FastAPI()

wa = WhatsApp(
    phone_id=os.environ.get('WHATSAPP_PHONE_ID'),  # The phone id you got from the API Setup
    token=os.environ.get('WHATSAPP_TOKEN'),  # The token you got from the API Setup
    server=fastapi_app,
    callback_url="https://9f6e-105-163-2-210.ngrok-free.app",
    verify_token="xyz123",
    app_id=1392339421934377,
    app_secret="b8a5543a9bf425a0e87676641569b2b4"
)

@wa.on_message(filters.matches("Hello", "Hi"))
async def hello(client: WhatsApp, msg: types.Message):
    await msg.react("👋")
    await msg.reply_text(
        text=f"Hello {msg.from_user.name}!",
        buttons=[
            types.Button(
                title="Click me!",
                callback_data="id:123"
            )
        ]
    )

@wa.on_callback_button(filters.startswith("id"))
async def click_me(client: WhatsApp, clb: types.CallbackButton):
    await clb.reply_text("You clicked me!")