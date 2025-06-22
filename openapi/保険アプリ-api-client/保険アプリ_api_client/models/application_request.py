from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ApplicationRequest")


@_attrs_define
class ApplicationRequest:
    """
    Attributes:
        quote_id (str):  Example: quote_abc123.
        user_consent (bool):  Example: True.
    """

    quote_id: str
    user_consent: bool
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        quote_id = self.quote_id

        user_consent = self.user_consent

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "quote_id": quote_id,
                "user_consent": user_consent,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        quote_id = d.pop("quote_id")

        user_consent = d.pop("user_consent")

        application_request = cls(
            quote_id=quote_id,
            user_consent=user_consent,
        )

        application_request.additional_properties = d
        return application_request

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
