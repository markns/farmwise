from datetime import datetime, timedelta

from geoalchemy2.functions import ST_Distance, ST_MakePoint, ST_SetSRID, ST_Transform
from geoalchemy2.shape import to_shape
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import selectinload
from temporalio import activity

from ..whatsapp.schema import SimpleContact
from .schema import AlertDetails, AlertMessage, FarmWithContacts


class AlertActivities:
    @activity.defn
    async def get_recent_notes(self) -> list[AlertDetails]:
        """Get notes created in the last hour."""
        # from farmbase.auth.models import FarmbaseUserOrganization
        from farmbase.database.core import engine
        from farmbase.farm.models import Farm
        from farmbase.farm.note.models import Note
        #
        # FarmbaseUserOrganization.organization

        organization = "default"
        schema = f"farmbase_organization_{organization}"
        schema_engine = engine.execution_options(schema_translate_map={None: schema})
        async_session_factory = async_sessionmaker(
            bind=schema_engine,
            expire_on_commit=False,
        )

        one_hour_ago = datetime.utcnow() - timedelta(hours=1)

        async with async_session_factory() as session:
            # Query for notes created in the last hour with farm details
            query = (
                select(Note, Farm)
                .join(Farm, Note.farm_id == Farm.id)
                .filter(Note.created_at >= one_hour_ago)
                .options(selectinload(Note.farm))
            )

            results = await session.execute(query)
            note_farm_pairs = results.all()

        alert_details = []
        for note, farm in note_farm_pairs:
            note_location = ""
            if note.location:
                point = to_shape(note.location)
                note_location = f"{point.y},{point.x}"

            alert_details.append(
                AlertDetails(
                    note_id=note.id,
                    note_text=note.note_text,
                    farm_id=farm.id,
                    farm_name=farm.farm_name,
                    note_location=note_location,
                    tags=note.tags,
                    created_at=note.created_at.isoformat(),
                )
            )

        print(alert_details)
        return alert_details

    @activity.defn
    async def find_nearby_farms(self, note_details: AlertDetails, radius_km: float = 5.0) -> list[FarmWithContacts]:
        """Find farms within the specified radius of the note's farm location."""
        from farmbase.auth.models import FarmbaseUserOrganization
        from farmbase.database.core import engine
        from farmbase.farm.models import Farm, FarmContact

        FarmbaseUserOrganization.organization

        organization = "default"
        schema = f"farmbase_organization_{organization}"
        schema_engine = engine.execution_options(schema_translate_map={None: schema})
        async_session_factory = async_sessionmaker(
            bind=schema_engine,
            expire_on_commit=False,
        )

        if not note_details.note_location:
            return []

        lat, lon = map(float, note_details.note_location.split(","))

        async with async_session_factory() as session:
            # Create a point from the farm location
            origin_point = ST_SetSRID(ST_MakePoint(lon, lat), 4326)

            # Find farms within radius (excluding the original farm)
            distance_query = ST_Distance(
                ST_Transform(Farm.location, 3857),  # Transform to meters
                ST_Transform(origin_point, 3857),
            )

            query = (
                select(
                    Farm,
                    (distance_query / 1000).label("distance_km"),  # Convert to kilometers
                )
                .filter(
                    and_(
                        Farm.id != note_details.farm_id,  # Exclude the original farm
                        Farm.location.isnot(None),  # Only farms with locations
                        distance_query <= radius_km * 1000,  # Within radius in meters
                    )
                )
                .options(selectinload(Farm.contact_associations).selectinload(FarmContact.contact))
            )

            results = await session.execute(query)
            farm_distance_pairs = results.all()

        farms_with_contacts = []
        for farm, distance in farm_distance_pairs:
            # Get contacts for this farm
            contacts = []
            for farm_contact in farm.contact_associations:
                contact = farm_contact.contact
                if contact.phone_number:  # Only contacts with phone numbers
                    contacts.append(
                        SimpleContact(
                            id=contact.id,
                            name=contact.name,
                            phone_number=contact.phone_number,
                        )
                    )

            if contacts:  # Only include farms that have contacts
                farms_with_contacts.append(
                    FarmWithContacts(
                        farm_id=farm.id,
                        farm_name=farm.farm_name,
                        distance_km=round(distance, 2),
                        contacts=contacts,
                    )
                )

        return farms_with_contacts

    @activity.defn
    async def generate_alert_message(self, note_details: AlertDetails) -> AlertMessage:
        """Generate an alert message using OpenAI based on the note content."""
        from openai import OpenAI

        client = OpenAI()

        prompt = f"""
Based on the following farm note, create an alert message for nearby farmers:

Farm: {note_details.farm_name}
Note: {note_details.note_text}
Tags: {note_details.tags or "None"}
Date: {note_details.created_at}

Generate:
1. A brief summary of the situation (1-2 sentences)
2. A list of 2-3 specific actions that nearby farmers should take

Format your response as a JSON object with 'summary' and 'actions' fields.
The 'actions' field should be a list of strings.
Keep the language simple, practical and actionable for farmers.
"""

        response = client.responses.parse(model="gpt-4.1", input=prompt, text_format=AlertMessage)

        return response.output_parsed
