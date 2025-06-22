from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="QuoteRequest")


@_attrs_define
class QuoteRequest:
    """
    Attributes:
        plan_id (str):  Example: pension001.
        payment_period (int):  Example: 20.
        monthly_premium (int):  Example: 20000.
        refund_condition (str):  Example: 満期一括受取.
    """

    plan_id: str
    payment_period: int
    monthly_premium: int
    refund_condition: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        plan_id = self.plan_id

        payment_period = self.payment_period

        monthly_premium = self.monthly_premium

        refund_condition = self.refund_condition

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "plan_id": plan_id,
                "payment_period": payment_period,
                "monthly_premium": monthly_premium,
                "refund_condition": refund_condition,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        plan_id = d.pop("plan_id")

        payment_period = d.pop("payment_period")

        monthly_premium = d.pop("monthly_premium")

        refund_condition = d.pop("refund_condition")

        quote_request = cls(
            plan_id=plan_id,
            payment_period=payment_period,
            monthly_premium=monthly_premium,
            refund_condition=refund_condition,
        )

        quote_request.additional_properties = d
        return quote_request

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
