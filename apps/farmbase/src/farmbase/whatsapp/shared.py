from dataclasses import dataclass


@dataclass
class Contact:
    id: int
    phone_number: str
    name: str
    location: str
