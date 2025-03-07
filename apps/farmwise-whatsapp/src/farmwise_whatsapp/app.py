import os
from contextlib import asynccontextmanager
from enum import Enum

from fastapi import FastAPI
from pywa.types import Command, Section, SectionList, SectionRow
from pywa_async import WhatsApp, filters, types

from farmwise_whatsapp.core.config import settings  # Import settings

from farmwise_client import AgentClient


class Commands(Enum):
    REGISTER_FIELD = Command(name="Register a field", description="Register a new field")
    SELECT_COLOUR = Command(name="Select your favorite color", description="Select your favorite color")


@asynccontextmanager
async def lifespan(_: FastAPI):
    print("Startup: Initializing resources...")
    await wa.update_conversational_automation(enable_chat_opened=True,
                                        ice_breakers=[],
                                        commands=[command.value for command in Commands])

    yield  # Run the application
    print("Shutdown: Cleaning up resources...")

app = FastAPI(lifespan=lifespan)

wa = WhatsApp(
    phone_id=settings.WHATSAPP_PHONE_ID,  # The phone id you got from the API Setup
    token=settings.WHATSAPP_TOKEN,  # The token you got from the API Setup
    server=app,
    callback_url="https://821d-105-163-2-210.ngrok-free.app",
    verify_token="xyz123",
    app_id=1392339421934377,
    app_secret="b8a5543a9bf425a0e87676641569b2b4"
)

# TODO: move to dependencies
agent_client = AgentClient(base_url=settings.AGENT_URL)


# flow_id = wa.create_flow(
#     name="My New Flow",
#     categories=[FlowCategory.CUSTOMER_SUPPORT, FlowCategory.SURVEY]
# )
# print(wa.get_flow(flow_id))

@wa.on_message
async def handle_message(client: WhatsApp, msg: types.Message):
    response = await agent_client.ainvoke(
        message=msg.text,
        model="gpt-4o-mini",
        thread_id=msg.metadata.phone_number_id,
    )
    await msg.reply_text(response.content)

@wa.on_message(filters.command(Commands.REGISTER_FIELD.value.name))
async def register_field(client: WhatsApp, msg: types.Message):
    print("In register field handler")
    # await msg.reply_text('Registering your field!')
    response = await agent_client.ainvoke(
        message=msg.text,
        model="gpt-4o-mini",
        thread_id=msg.metadata.phone_number_id,
    )
    await msg.reply_text(response.content)



@wa.on_message(filters.location)
async def location(client: WhatsApp, msg: types.Message):
    await msg.reply_text(
        text=f"Hello {msg}!",
        buttons=[
            # types.Location(),
            types.Button(
                title="Click me!",
                callback_data="id:123"
            )
        ]
    )


@wa.on_message(filters.command(Commands.SELECT_COLOUR.value.name))
async def select_colour(client: WhatsApp, msg: types.Message):
    print("In select colour handler")
    await msg.reply_text(header='Select your favorite color',
                text='Tap a button to select your favorite color:',
                # footer='⚡ Powered by PyWa',
                buttons=SectionList(
                    button_title='Colors',
                    sections=[
                        Section(
                            title='Popular Colors',
                            rows=[
                                SectionRow(
                                    title='🟥 Red',
                                    callback_data='color:red',
                                    description='The color of blood',
                                ),
                                SectionRow(
                                    title='🟩 Green',
                                    callback_data='color:green',
                                    description='The color of grass',
                                ),
                                SectionRow(
                                    title='🟦 Blue',
                                    callback_data='color:blue',
                                    description='The color of the sky',
                                )
                            ],
                        ),
                        Section(
                            title='Other Colors',
                            rows=[
                                SectionRow(
                                    title='🟧 Orange',
                                    callback_data='color:orange',
                                    description='The color of an orange',
                                ),
                                SectionRow(
                                    title='🟪 Purple',
                                    callback_data='color:purple',
                                    description='The color of a grape',
                                ),
                                SectionRow(
                                    title='🟨 Yellow',
                                    callback_data='color:yellow',
                                    description='The color of the sun',
                                )
                            ]
                        )
                    ]
                )
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