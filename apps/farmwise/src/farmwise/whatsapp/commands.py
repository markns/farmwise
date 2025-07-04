from pywa_async.types import Command

from farmwise.agent import market_price_agent, soil_advisor_agent, maize_variety_selector, \
    crop_pathogen_diagnosis_agent, crop_suitability_agent
from farmwise.schema import SectionList, Section, SectionRow, ActivityData

# TODO: load these commands from the FarmWise service
commands = [
    Command(name="menu", description="Show activities"),
    Command(name="profile", description="Show profile")
]

activities = SectionList(
    button_title="Select activity",
    sections=[
        Section(
            title="Agronomy",
            rows=[
                SectionRow(title="Disease & pest advice",
                           callback_data=ActivityData(agent=crop_pathogen_diagnosis_agent.name,
                                                      text="Disease & pest advice")),
                SectionRow(title="Crop suitability", callback_data=ActivityData(agent=crop_suitability_agent.name,
                                                                                text="Get crop suitability advice")),
                SectionRow(title="Soil advice", callback_data=ActivityData(agent=soil_advisor_agent.name,
                                                                           text="Get soil advice")),
                SectionRow(title="Choose maize variety",
                           callback_data=ActivityData(agent=maize_variety_selector.name,
                                                      text="Choose maize seed variety")),
            ],
        ),
        Section(
            title="Farm Management",
            rows=[
                SectionRow(title="Get market prices",
                           callback_data=ActivityData(agent=market_price_agent.name,
                                                      text="Get market prices")),
                # SectionRow(title="Register field", callback_data="Register field"),
            ],
        ),
        Section(
            title="Settings",
            rows=[
                SectionRow(title="Update product interests", callback_data="Update product interests"),
                SectionRow(title="Notifications", callback_data="/subscriptions"),
                SectionRow(title="Show profile", callback_data="/profile"),
            ],
        ),
    ],
)
