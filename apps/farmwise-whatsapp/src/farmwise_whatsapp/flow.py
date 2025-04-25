from pywa import WhatsApp
from pywa.types import FlowCategory, FlowJSON
from pywa.types.flows import Layout, Screen, TextHeading

from farmwise_whatsapp.core.config import settings  # Import settings

wa = WhatsApp(
    phone_id=settings.WHATSAPP_PHONE_ID,  # The phone id you got from the API Setup
    token=settings.WHATSAPP_TOKEN,  # The token you got from the API Setup
    # server=app,
    # callback_url="https://421e-105-163-1-38.ngrok-free.app",
    # verify_token="xyz123fdsfds",
    app_id=1392339421934377,
    app_secret="b8a5543a9bf425a0e87676641569b2b4",
    business_account_id="401685599703995",
)

# WhatsApp Business Account ID (WABA) is required
# wa = WhatsApp(..., business_account_id="1234567890123456")

# flow_id = wa.create_flow(name="My New Flow", categories=[FlowCategory.CUSTOMER_SUPPORT, FlowCategory.SURVEY])
# print(wa.get_flow(flow_id))


wa.create_flow(
    name="Feedback",
    categories=[FlowCategory.SURVEY, FlowCategory.OTHER],
    flow_json=FlowJSON(
        version="6.0",
        screens=[
            Screen(
                id="START",
                layout=Layout(
                    children=[
                        TextHeading(
                            text="Hello World",
                        )
                    ],
                ),
            )
        ],
    ),
    publish=True,
)


# FlowDetails(id='1234567890123456', name='My New Flow', status=FlowStatus.DRAFT, ...)
