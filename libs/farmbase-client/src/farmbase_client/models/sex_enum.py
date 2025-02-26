from enum import Enum


class SexEnum(str, Enum):
    F = "F"
    M = "M"

    def __str__(self) -> str:
        return str(self.value)
