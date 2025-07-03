from enum import Enum

from pywa.types import SectionList, Section, SectionRow, Command


# TODO: load these commands from the FarmWise service
class Commands(Enum):
    SHOW_MENU = Command(name="menu", description="Show activities")
    SHOW_PROFILE = Command(name="profile", description="Show profile")
    # REGISTER_FIELD = Command(name="Register a field", description="Register a new field")
    # SELECT_MAIZE_VARIETY = Command(name="Select a maize seed variety", description="Select a maize seed variety")
    # SHOW_SUITABLE_CROPS = Command(name="Show suitable crops", description="Show suitable crops for a location")


activities = SectionList(
    button_title="Select activity",
    sections=[
        Section(
            title="Agronomy",
            rows=[
                SectionRow(title="Choose seed variety", callback_data="Choose seed variety"),
                SectionRow(title="Crop suitability", callback_data="Crop suitability"),
                SectionRow(title="Soil advice", callback_data="Get soil advice"),
                SectionRow(title="Disease & pest advice", callback_data="Disease & pest advice"),
            ],
        ),
        Section(
            title="Farm Management",
            rows=[
                SectionRow(title="Get market prices", callback_data="Get market prices"),
                SectionRow(title="Register field", callback_data="Register field"),
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

