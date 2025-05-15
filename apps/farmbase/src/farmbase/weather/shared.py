# @@@SNIPSTART python-money-transfer-project-template-shared
from dataclasses import dataclass

# MONEY_TRANSFER_TASK_QUEUE_NAME = "TRANSFER_MONEY_TASK_QUEUE"
DEFAULT_TASK_QUEUE = "DEFAULT_TASK_QUEUE"

#
# @dataclass
# class PaymentDetails:
#     source_account: str
#     target_account: str
#     amount: int
#     reference_id: str


@dataclass
class YourParams:
    greeting: str
    name: str


@dataclass
class LocationQuery:
    location: str


@dataclass
class ForecastDetails:
    location: str
    country: str
    hourly_descriptions: list[str]


# @@@SNIPEND
