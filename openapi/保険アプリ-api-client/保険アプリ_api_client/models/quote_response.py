import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="QuoteResponse")


@_attrs_define
class QuoteResponse:
    """
    Attributes:
        quote_id (Union[Unset, str]):  Example: quote_abc123.
        plan_id (Union[Unset, str]):  Example: pension001.
        monthly_premium (Union[Unset, int]):  Example: 20000.
        expected_refund (Union[Unset, int]):  Example: 3100000.
        valid_until (Union[Unset, datetime.datetime]):  Example: 2025-07-01T00:00:00Z.
    """

    quote_id: Union[Unset, str] = UNSET
    plan_id: Union[Unset, str] = UNSET
    monthly_premium: Union[Unset, int] = UNSET
    expected_refund: Union[Unset, int] = UNSET
    valid_until: Union[Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        quote_id = self.quote_id

        plan_id = self.plan_id

        monthly_premium = self.monthly_premium

        expected_refund = self.expected_refund

        valid_until: Union[Unset, str] = UNSET
        if not isinstance(self.valid_until, Unset):
            valid_until = self.valid_until.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if quote_id is not UNSET:
            field_dict["quote_id"] = quote_id
        if plan_id is not UNSET:
            field_dict["plan_id"] = plan_id
        if monthly_premium is not UNSET:
            field_dict["monthly_premium"] = monthly_premium
        if expected_refund is not UNSET:
            field_dict["expected_refund"] = expected_refund
        if valid_until is not UNSET:
            field_dict["valid_until"] = valid_until

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        quote_id = d.pop("quote_id", UNSET)

        plan_id = d.pop("plan_id", UNSET)

        monthly_premium = d.pop("monthly_premium", UNSET)

        expected_refund = d.pop("expected_refund", UNSET)

        _valid_until = d.pop("valid_until", UNSET)
        valid_until: Union[Unset, datetime.datetime]
        if isinstance(_valid_until, Unset):
            valid_until = UNSET
        else:
            valid_until = isoparse(_valid_until)

        quote_response = cls(
            quote_id=quote_id,
            plan_id=plan_id,
            monthly_premium=monthly_premium,
            expected_refund=expected_refund,
            valid_until=valid_until,
        )

        quote_response.additional_properties = d
        return quote_response

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
