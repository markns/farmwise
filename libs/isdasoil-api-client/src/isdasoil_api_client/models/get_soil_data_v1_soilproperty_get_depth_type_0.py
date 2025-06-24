from enum import Enum


class GetSoilDataV1SoilpropertyGetDepthType0(str, Enum):
    VALUE_0 = "0-20"
    VALUE_1 = "0-50"
    VALUE_2 = "20-50"
    VALUE_3 = "0-200"
    VALUE_4 = "0"

    def __str__(self) -> str:
        return str(self.value)
