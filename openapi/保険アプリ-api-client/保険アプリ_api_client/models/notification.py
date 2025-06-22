import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..types import UNSET, Unset

T = TypeVar("T", bound="Notification")


@_attrs_define
class Notification:
    """
    Attributes:
        message_id (Union[Unset, str]):  Example: notif001.
        title (Union[Unset, str]):  Example: 重要なお知らせ.
        content (Union[Unset, str]):  Example: 保険料が改定されます。.
        published_at (Union[Unset, datetime.datetime]):  Example: 2025-06-01T00:00:00Z.
        is_read (Union[Unset, bool]):
    """

    message_id: Union[Unset, str] = UNSET
    title: Union[Unset, str] = UNSET
    content: Union[Unset, str] = UNSET
    published_at: Union[Unset, datetime.datetime] = UNSET
    is_read: Union[Unset, bool] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        message_id = self.message_id

        title = self.title

        content = self.content

        published_at: Union[Unset, str] = UNSET
        if not isinstance(self.published_at, Unset):
            published_at = self.published_at.isoformat()

        is_read = self.is_read

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if message_id is not UNSET:
            field_dict["message_id"] = message_id
        if title is not UNSET:
            field_dict["title"] = title
        if content is not UNSET:
            field_dict["content"] = content
        if published_at is not UNSET:
            field_dict["published_at"] = published_at
        if is_read is not UNSET:
            field_dict["is_read"] = is_read

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        message_id = d.pop("message_id", UNSET)

        title = d.pop("title", UNSET)

        content = d.pop("content", UNSET)

        _published_at = d.pop("published_at", UNSET)
        published_at: Union[Unset, datetime.datetime]
        if isinstance(_published_at, Unset):
            published_at = UNSET
        else:
            published_at = isoparse(_published_at)

        is_read = d.pop("is_read", UNSET)

        notification = cls(
            message_id=message_id,
            title=title,
            content=content,
            published_at=published_at,
            is_read=is_read,
        )

        notification.additional_properties = d
        return notification

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
