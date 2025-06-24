from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SoilPropertyValue")


@_attrs_define
class SoilPropertyValue:
    """
    Attributes:
        value (Union[None, float, int, str]):
        unit (Union[None, Unset, str]):
        type_ (Union[Unset, str]):  Default: 'float'.
    """

    value: Union[None, float, int, str]
    unit: Union[None, Unset, str] = UNSET
    type_: Union[Unset, str] = "float"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        value: Union[None, float, int, str]
        value = self.value

        unit: Union[None, Unset, str]
        if isinstance(self.unit, Unset):
            unit = UNSET
        else:
            unit = self.unit

        type_ = self.type_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "value": value,
            }
        )
        if unit is not UNSET:
            field_dict["unit"] = unit
        if type_ is not UNSET:
            field_dict["type"] = type_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_value(data: object) -> Union[None, float, int, str]:
            if data is None:
                return data
            return cast(Union[None, float, int, str], data)

        value = _parse_value(d.pop("value"))

        def _parse_unit(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        unit = _parse_unit(d.pop("unit", UNSET))

        type_ = d.pop("type", UNSET)

        soil_property_value = cls(
            value=value,
            unit=unit,
            type_=type_,
        )

        soil_property_value.additional_properties = d
        return soil_property_value

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
