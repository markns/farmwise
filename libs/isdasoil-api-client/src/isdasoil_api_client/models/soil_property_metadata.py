from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.layers_depth import LayersDepth
    from ..models.soil_property_metadata_value import SoilPropertyMetadataValue


T = TypeVar("T", bound="SoilPropertyMetadata")


@_attrs_define
class SoilPropertyMetadata:
    """
    Attributes:
        description (str):
        theme (str):
        unit (Union[None, str]):
        value (SoilPropertyMetadataValue):
        depths (LayersDepth):
        uncertainty (Union[None, Unset, bool]):
    """

    description: str
    theme: str
    unit: Union[None, str]
    value: "SoilPropertyMetadataValue"
    depths: "LayersDepth"
    uncertainty: Union[None, Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        description = self.description

        theme = self.theme

        unit: Union[None, str]
        unit = self.unit

        value = self.value.to_dict()

        depths = self.depths.to_dict()

        uncertainty: Union[None, Unset, bool]
        if isinstance(self.uncertainty, Unset):
            uncertainty = UNSET
        else:
            uncertainty = self.uncertainty

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "description": description,
                "theme": theme,
                "unit": unit,
                "value": value,
                "depths": depths,
            }
        )
        if uncertainty is not UNSET:
            field_dict["uncertainty"] = uncertainty

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.layers_depth import LayersDepth
        from ..models.soil_property_metadata_value import SoilPropertyMetadataValue

        d = dict(src_dict)
        description = d.pop("description")

        theme = d.pop("theme")

        def _parse_unit(data: object) -> Union[None, str]:
            if data is None:
                return data
            return cast(Union[None, str], data)

        unit = _parse_unit(d.pop("unit"))

        value = SoilPropertyMetadataValue.from_dict(d.pop("value"))

        depths = LayersDepth.from_dict(d.pop("depths"))

        def _parse_uncertainty(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        uncertainty = _parse_uncertainty(d.pop("uncertainty", UNSET))

        soil_property_metadata = cls(
            description=description,
            theme=theme,
            unit=unit,
            value=value,
            depths=depths,
            uncertainty=uncertainty,
        )

        soil_property_metadata.additional_properties = d
        return soil_property_metadata

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
