from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Plan")


@_attrs_define
class Plan:
    """
    Attributes:
        plan_id (Union[Unset, str]):  Example: pension001.
        name (Union[Unset, str]):  Example: 個人年金保険.
        description (Union[Unset, str]):  Example: 老後の生活資金を確保するための保険です。.
        image_key (Union[Unset, str]):  Example: pension001.jpg.
    """

    plan_id: Union[Unset, str] = UNSET
    name: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    image_key: Union[Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        plan_id = self.plan_id

        name = self.name

        description = self.description

        image_key = self.image_key

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if plan_id is not UNSET:
            field_dict["plan_id"] = plan_id
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if image_key is not UNSET:
            field_dict["image_key"] = image_key

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        plan_id = d.pop("plan_id", UNSET)

        name = d.pop("name", UNSET)

        description = d.pop("description", UNSET)

        image_key = d.pop("image_key", UNSET)

        plan = cls(
            plan_id=plan_id,
            name=name,
            description=description,
            image_key=image_key,
        )

        plan.additional_properties = d
        return plan

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
