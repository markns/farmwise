import datetime
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.sex_enum import SexEnum
from ..types import UNSET, Unset

T = TypeVar("T", bound="Animal")


@_attrs_define
class Animal:
    """
    Attributes:
        animal_type (str): Species/breed of the animal. Required field.
        nickname (list[str]): List of nicknames for the animal.
        sex (SexEnum):
        birthdate (Union[None, Unset, datetime.datetime]): Birthdate provided as a Unix timestamp or ISO date string.
        is_castrated (Union[None, Unset, bool]): Indicates if the animal has been castrated. Default: False.
    """

    animal_type: str
    nickname: list[str]
    sex: SexEnum
    birthdate: Union[None, Unset, datetime.datetime] = UNSET
    is_castrated: Union[None, Unset, bool] = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        animal_type = self.animal_type

        nickname = self.nickname

        sex = self.sex.value

        birthdate: Union[None, Unset, str]
        if isinstance(self.birthdate, Unset):
            birthdate = UNSET
        elif isinstance(self.birthdate, datetime.datetime):
            birthdate = self.birthdate.isoformat()
        else:
            birthdate = self.birthdate

        is_castrated: Union[None, Unset, bool]
        if isinstance(self.is_castrated, Unset):
            is_castrated = UNSET
        else:
            is_castrated = self.is_castrated

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "animal_type": animal_type,
                "nickname": nickname,
                "sex": sex,
            }
        )
        if birthdate is not UNSET:
            field_dict["birthdate"] = birthdate
        if is_castrated is not UNSET:
            field_dict["is_castrated"] = is_castrated

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        d = src_dict.copy()
        animal_type = d.pop("animal_type")

        nickname = cast(list[str], d.pop("nickname"))

        sex = SexEnum(d.pop("sex"))

        def _parse_birthdate(data: object) -> Union[None, Unset, datetime.datetime]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                birthdate_type_0 = isoparse(data)

                return birthdate_type_0
            except:  # noqa: E722
                pass
            return cast(Union[None, Unset, datetime.datetime], data)

        birthdate = _parse_birthdate(d.pop("birthdate", UNSET))

        def _parse_is_castrated(data: object) -> Union[None, Unset, bool]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, bool], data)

        is_castrated = _parse_is_castrated(d.pop("is_castrated", UNSET))

        animal = cls(
            animal_type=animal_type,
            nickname=nickname,
            sex=sex,
            birthdate=birthdate,
            is_castrated=is_castrated,
        )

        animal.additional_properties = d
        return animal

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
