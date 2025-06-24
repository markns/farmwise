from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SoilPropertyDepth")


@_attrs_define
class SoilPropertyDepth:
    """
    Attributes:
        value (Union[None, Unset, str]):
        unit (Union[None, Unset, str]):
    """

    value: Union[None, Unset, str] = UNSET
    unit: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        value: Union[None, Unset, str]
        if isinstance(self.value, Unset):
            value = UNSET
        else:
            value = self.value

        unit: Union[None, Unset, str]
        if isinstance(self.unit, Unset):
            unit = UNSET
        else:
            unit = self.unit

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if value is not UNSET:
            field_dict["value"] = value
        if unit is not UNSET:
            field_dict["unit"] = unit

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_value(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        value = _parse_value(d.pop("value", UNSET))

        def _parse_unit(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        unit = _parse_unit(d.pop("unit", UNSET))

        soil_property_depth = cls(
            value=value,
            unit=unit,
        )

        soil_property_depth.additional_properties = d
        return soil_property_depth

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
