import logging
from datetime import datetime
from typing import Optional
import json

from pywa_async import WhatsApp
from pywa_async.types import FlowRequest, FlowCompletion, FlowResponse, FlowRequestActionType
from upstash_redis.asyncio import Redis

from farmbase_client.api.contacts import contacts_get_contact_by_phone as get_contact_by_phone
from farmbase_client.api.contacts import contacts_patch_contact as patch_contact
from farmbase_client.models import ContactPatch
from farmwise.farmbase import farmbase_api_client
from farmwise.settings import settings

# Dictionary to store user phone numbers by flow token
# In production, you might want to use a proper cache like Redis
# _flow_tokens = {}
redis = Redis(url=settings.UPSTASH_REDIS_REST_URL, token=settings.UPSTASH_REDIS_REST_TOKEN)



async def store_flow_token(flow_token: str, wa_id: str):
    """Store the mapping between flow token and WhatsApp ID."""
    # _flow_tokens[flow_token] = wa_id
    await redis.set(f"flow_token:{flow_token}",  wa_id, ex=settings.SESSION_TTL_SECS)

async def get_flow_token_value(flow_token:str) -> str:
    return await redis.get(f"flow_token:{flow_token}")


@WhatsApp.on_flow_request("/profile-edit-flow")
async def on_profile_edit_request(_: WhatsApp, flow: FlowRequest) -> FlowResponse | None:
    """Handle profile edit flow requests."""
    if flow.has_error:
        logging.error("Profile edit flow request has error: %s", flow.data)
        return

    # For initial request, return current user data
    if flow.action == FlowRequestActionType.INIT:
        # Get user data from database using WhatsApp ID from flow token
        user_data = await get_user_profile_data(flow.flow_token)
        
        return FlowResponse(
            version=flow.version,
            screen="PROFILE_EDIT",
            data={
                "current_name": user_data.get("name", ""),
                "current_preferred_address": user_data.get("preferred_form_of_address", ""),
                "current_gender": user_data.get("gender", ""),
                "current_date_of_birth": user_data.get("date_of_birth", ""),
                # "current_estimated_age": str(user_data.get("estimated_age", "")),
                "current_role": user_data.get("role", ""),
                # "current_experience": int(user_data.get("experience", "")),
                "current_email": user_data.get("email", ""),
            },
        )


@WhatsApp.on_flow_completion()
async def handle_profile_edit_completion(_: WhatsApp, flow: FlowCompletion):
    """Handle profile edit flow completion."""
    print(f"Profile edit flow completed for token: {flow.token}")
    print(f"Updated data: {flow.response}")
    
    # Update user profile in database
    await update_user_profile(flow.token, flow.response)
    
    # Send confirmation message
    await _.send_message(
        to=flow.from_user.wa_id,
        text="✅ Your profile has been updated successfully!"
    )


async def get_user_profile_data(flow_token: str) -> dict:
    """Get user profile data from farmbase API using flow token."""
    try:
        # Get WhatsApp ID from flow token
        wa_id = await get_flow_token_value(flow_token)
        if not wa_id:
            print(f"No WhatsApp ID found for flow token: {flow_token}")
            return {}
        
        # Get contact from farmbase API
        contact = await get_contact_by_phone.asyncio(
            client=farmbase_api_client,
            organization="default",  # TODO: Get proper organization
            phone=wa_id,
        )
        
        if contact:
            return {
                "name": contact.name or "",
                "preferred_form_of_address": contact.preferred_form_of_address or "",
                "gender": contact.gender.value if contact.gender else "",
                "date_of_birth": contact.date_of_birth.isoformat() if contact.date_of_birth else "",
                "estimated_age": contact.estimated_age or "",
                "role": contact.role.value if contact.role else "",
                "experience": contact.experience or "",
                "email": contact.email or "",
            }
        else:
            print(f"No contact found for WhatsApp ID: {wa_id}")
            return {}
    except Exception as e:
        print(f"Error getting user profile data: {e}")
        return {}


async def update_user_profile(flow_token: str, profile_data: dict):
    """Update user profile using farmbase API."""
    try:
        # Get WhatsApp ID from flow token
        wa_id = await get_flow_token_value(flow_token)
        if not wa_id:
            print(f"No WhatsApp ID found for flow token: {flow_token}")
            return
        
        # Get contact from farmbase API to get ID and organization
        contact = await get_contact_by_phone.asyncio(
            client=farmbase_api_client,
            organization="default",  # TODO: Get proper organization
            phone=wa_id,
        )
        
        if contact:
            # Prepare contact patch data
            contact_patch = ContactPatch(
                name=profile_data.get("name") if profile_data.get("name") else None,
                preferred_form_of_address=profile_data.get("preferred_form_of_address") if profile_data.get("preferred_form_of_address") else None,
                gender=profile_data.get("gender") if profile_data.get("gender") else None,
                date_of_birth=datetime.strptime(profile_data.get("date_of_birth"), "%Y-%m-%d").date() if profile_data.get("date_of_birth") else None,
                estimated_age=int(profile_data.get("estimated_age")) if profile_data.get("estimated_age") and profile_data.get("estimated_age").isdigit() else None,
                role=profile_data.get("role") if profile_data.get("role") else None,
                experience=int(profile_data.get("experience")) if profile_data.get("experience") and profile_data.get("experience").isdigit() else None,
                email=profile_data.get("email") if profile_data.get("email") else None,
            )
            
            # Update contact via farmbase API
            updated_contact = await patch_contact.asyncio(
                client=farmbase_api_client,
                organization=contact.organization.slug,
                contact_id=contact.id,
                body=contact_patch,
            )
            
            if updated_contact:
                print(f"Profile updated successfully for contact: {updated_contact.name}")
            else:
                print("Error updating profile - no response from API")
        else:
            print(f"No contact found for WhatsApp ID: {wa_id}")
    except Exception as e:
        print(f"Error updating user profile: {e}")
