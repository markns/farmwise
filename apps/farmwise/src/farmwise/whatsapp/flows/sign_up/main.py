from pywa import WhatsApp
from pywa.errors import FlowUpdatingError
from pywa.types.flows import FlowCategory

from farmwise.settings import settings
from farmwise.whatsapp.flows.sign_up.flow_json import SIGN_UP_FLOW_JSON


def create_flow(wa):

    flow_id = wa.create_flow(
        name="Sign Up Flow",
        categories=[FlowCategory.SIGN_IN, FlowCategory.SIGN_UP],
    )

    wa.update_flow_metadata(
        flow_id=flow_id,
        endpoint_uri=f"{settings.WHATSAPP_CALLBACK_URL}/sign-up-flow",
    )

    try:
        wa.update_flow_json(
            flow_id=flow_id,
            flow_json=SIGN_UP_FLOW_JSON,
        )
        print("Flow updated successfully")
    except FlowUpdatingError as e:
        print("Flow updating failed")
        print(wa.get_flow(flow_id=flow_id).validation_errors)


def main():
    wa = WhatsApp(
        phone_id=settings.WHATSAPP_PHONE_ID,
        token=settings.WHATSAPP_TOKEN,
        callback_url=settings.WHATSAPP_CALLBACK_URL,
        verify_token=settings.WHATSAPP_VERIFY_TOKEN,
        app_id=settings.WHATSAPP_APP_ID,
        app_secret=settings.WHATSAPP_APP_SECRET,
        business_account_id=settings.WHATSAPP_BUSINESS_ACCOUNT_ID,
        business_private_key=settings.WHATSAPP_BUSINESS_PRIVATE_KEY,
        business_private_key_password=settings.WHATSAPP_BUSINESS_PRIVATE_KEY_PASSWORD
    )

    create_flow(wa)



if __name__ == '__main__':
    main()
