from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Uncertainty")


@_attrs_define
class Uncertainty:
    """
    Attributes:
        confidence_interval (Union[None, Unset, str]): The proportion of the variance of the value (as a percentage)
            covered by the uncertainty measurement.
        lower_bound (Union[None, Unset, float, int, str]): The lower limit of the uncertainty measurement at the given
            confidence interval
        upper_bound (Union[None, Unset, float, int, str]): The upper limit of the uncertainty measurement at the given
            confidence interval
    """

    confidence_interval: Union[None, Unset, str] = UNSET
    lower_bound: Union[None, Unset, float, int, str] = UNSET
    upper_bound: Union[None, Unset, float, int, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        confidence_interval: Union[None, Unset, str]
        if isinstance(self.confidence_interval, Unset):
            confidence_interval = UNSET
        else:
            confidence_interval = self.confidence_interval

        lower_bound: Union[None, Unset, float, int, str]
        if isinstance(self.lower_bound, Unset):
            lower_bound = UNSET
        else:
            lower_bound = self.lower_bound

        upper_bound: Union[None, Unset, float, int, str]
        if isinstance(self.upper_bound, Unset):
            upper_bound = UNSET
        else:
            upper_bound = self.upper_bound

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if confidence_interval is not UNSET:
            field_dict["confidence_interval"] = confidence_interval
        if lower_bound is not UNSET:
            field_dict["lower_bound"] = lower_bound
        if upper_bound is not UNSET:
            field_dict["upper_bound"] = upper_bound

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_confidence_interval(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        confidence_interval = _parse_confidence_interval(d.pop("confidence_interval", UNSET))

        def _parse_lower_bound(data: object) -> Union[None, Unset, float, int, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float, int, str], data)

        lower_bound = _parse_lower_bound(d.pop("lower_bound", UNSET))

        def _parse_upper_bound(data: object) -> Union[None, Unset, float, int, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, float, int, str], data)

        upper_bound = _parse_upper_bound(d.pop("upper_bound", UNSET))

        uncertainty = cls(
            confidence_interval=confidence_interval,
            lower_bound=lower_bound,
            upper_bound=upper_bound,
        )

        uncertainty.additional_properties = d
        return uncertainty

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
