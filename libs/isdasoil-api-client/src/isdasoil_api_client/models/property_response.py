from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.property_response_property import PropertyResponseProperty


T = TypeVar("T", bound="PropertyResponse")


@_attrs_define
class PropertyResponse:
    """
    Attributes:
        property_ (PropertyResponseProperty):
    """

    property_: "PropertyResponseProperty"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        property_ = self.property_.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "property": property_,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.property_response_property import PropertyResponseProperty

        d = dict(src_dict)
        property_ = PropertyResponseProperty.from_dict(d.pop("property"))

        property_response = cls(
            property_=property_,
        )

        property_response.additional_properties = d
        return property_response

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
