from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.layers_depth_values_item import LayersDepthValuesItem

T = TypeVar("T", bound="LayersDepth")


@_attrs_define
class LayersDepth:
    """
    Attributes:
        unit (Union[None, str]):
        values (list[LayersDepthValuesItem]):
    """

    unit: Union[None, str]
    values: list[LayersDepthValuesItem]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        unit: Union[None, str]
        unit = self.unit

        values = []
        for values_item_data in self.values:
            values_item = values_item_data.value
            values.append(values_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "unit": unit,
                "values": values,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_unit(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        unit = _parse_unit(d.pop("unit"))

        values = []
        _values = d.pop("values")
        for values_item_data in _values:
            values_item = LayersDepthValuesItem(values_item_data)

            values.append(values_item)

        layers_depth = cls(
            unit=unit,
            values=values,
        )

        layers_depth.additional_properties = d
        return layers_depth

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
