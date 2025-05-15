from dataclasses import dataclass

# MONEY_TRANSFER_TASK_QUEUE_NAME = "TRANSFER_MONEY_TASK_QUEUE"
DEFAULT_TASK_QUEUE = "DEFAULT_TASK_QUEUE"


@dataclass
class LocationQuery:
    location: str


@dataclass
class ForecastDetails:
    location: str
    country: str
    hourly_descriptions: list[str]

@dataclass
class Contact:
    id: int
    phone_number: str
    name: str
    location: str
