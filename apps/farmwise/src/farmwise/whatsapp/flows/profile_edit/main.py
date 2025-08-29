import json
import os
from pywa import WhatsApp
from pywa.errors import FlowUpdatingError
from pywa.types.flows import FlowCategory

from farmwise.settings import settings
from farmwise.whatsapp.flows.profile_edit.flow_json import PROFILE_EDIT_FLOW_JSON

# File to store flow ID
FLOW_ID_FILE = os.path.join(os.path.dirname(__file__), "flow_id.json")


def save_flow_id(flow_id: str):
    """Save the flow ID to a file."""
    with open(FLOW_ID_FILE, "w") as f:
        json.dump({"flow_id": flow_id}, f)


def load_flow_id() -> str | None:
    """Load the flow ID from file."""
    try:
        with open(FLOW_ID_FILE, "r") as f:
            data = json.load(f)
            return data.get("flow_id")
    except FileNotFoundError:
        return None

PROFILE_EDIT_FLOW_NAME = "Profile Edit Flow"

def create_flow(wa):
    flow_id = wa.create_flow(
        name=PROFILE_EDIT_FLOW_NAME,
        categories=[FlowCategory.OTHER],
    )

    wa.update_flow_metadata(
        flow_id=flow_id,
        endpoint_uri=f"{settings.WHATSAPP_CALLBACK_URL}/profile-edit-flow",
    )

    try:
        wa.update_flow_json(
            flow_id=flow_id,
            flow_json=PROFILE_EDIT_FLOW_JSON,
        )
        print("Profile edit flow updated successfully")
        save_flow_id(flow_id)
    except FlowUpdatingError as e:
        print("Profile edit flow updating failed")
        print(wa.get_flow(flow_id=flow_id).validation_errors)

    return flow_id


def update_existing_flow(wa, flow_id):
    """Update an existing flow."""
    try:
        wa.update_flow_json(
            flow_id=flow_id,
            flow_json=PROFILE_EDIT_FLOW_JSON,
        )
        print(f"Profile edit flow {flow_id} updated successfully")
    except FlowUpdatingError as e:
        print(f"Profile edit flow {flow_id} updating failed")
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

    # Check if flow already exists
    existing_flow_id = load_flow_id()
    if existing_flow_id:
        print(f"Found existing flow ID: {existing_flow_id}")
        update_existing_flow(wa, existing_flow_id)
    else:
        flow_id = create_flow(wa)
        print(f"Profile edit flow created with ID: {flow_id}")


if __name__ == '__main__':
    main()