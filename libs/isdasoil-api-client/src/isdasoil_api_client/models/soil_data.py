from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.soil_property_depth import SoilPropertyDepth
    from ..models.soil_property_value import SoilPropertyValue
    from ..models.uncertainty import Uncertainty


T = TypeVar("T", bound="SoilData")


@_attrs_define
class SoilData:
    """
    Attributes:
        value (SoilPropertyValue):
        depth (SoilPropertyDepth):
        uncertainty (Union['Uncertainty', None, Unset, list['Uncertainty']]): The measure of uncertainty associated with
            the data value, given at different confidence intervals this object is only returned if the data was created
            using predictive machine learning, otherwise the returned value is null
    """

    value: "SoilPropertyValue"
    depth: "SoilPropertyDepth"
    uncertainty: Union["Uncertainty", None, Unset, list["Uncertainty"]] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.uncertainty import Uncertainty

        value = self.value.to_dict()

        depth = self.depth.to_dict()

        uncertainty: Union[None, Unset, dict[str, Any], list[dict[str, Any]]]
        if isinstance(self.uncertainty, Unset):
            uncertainty = UNSET
        elif isinstance(self.uncertainty, list):
            uncertainty = []
            for uncertainty_type_0_item_data in self.uncertainty:
                uncertainty_type_0_item = uncertainty_type_0_item_data.to_dict()
                uncertainty.append(uncertainty_type_0_item)

        elif isinstance(self.uncertainty, Uncertainty):
            uncertainty = self.uncertainty.to_dict()
        else:
            uncertainty = self.uncertainty

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "value": value,
                "depth": depth,
            }
        )
        if uncertainty is not UNSET:
            field_dict["uncertainty"] = uncertainty

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.soil_property_depth import SoilPropertyDepth
        from ..models.soil_property_value import SoilPropertyValue
        from ..models.uncertainty import Uncertainty

        d = dict(src_dict)
        value = SoilPropertyValue.from_dict(d.pop("value"))

        depth = SoilPropertyDepth.from_dict(d.pop("depth"))

        def _parse_uncertainty(data: object) -> Union["Uncertainty", None, Unset, list["Uncertainty"]]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                uncertainty_type_0 = []
                _uncertainty_type_0 = data
                for uncertainty_type_0_item_data in _uncertainty_type_0:
                    uncertainty_type_0_item = Uncertainty.from_dict(uncertainty_type_0_item_data)

                    uncertainty_type_0.append(uncertainty_type_0_item)

                return uncertainty_type_0
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                uncertainty_type_1 = Uncertainty.from_dict(data)

                return uncertainty_type_1
            except:  # noqa: E722
                pass
            return cast(Union["Uncertainty", None, Unset, list["Uncertainty"]], data)

        uncertainty = _parse_uncertainty(d.pop("uncertainty", UNSET))

        soil_data = cls(
            value=value,
            depth=depth,
            uncertainty=uncertainty,
        )

        soil_data.additional_properties = d
        return soil_data

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
