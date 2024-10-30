from typing import Literal, Optional

from nonebot.adapters.onebot.v11 import Message
from nonebot.adapters.onebot.v11.event import (
    GroupMessageEvent,
    MessageEvent,
    PrivateMessageEvent,
    Reply,
    Sender,
)

message_id_increment = 0


def create_sender(
    user_id: Optional[int] = 123456,
    nickname: Optional[str] = "TestUser",
    sex: Optional[str] = "unknown",
    age: Optional[int] = 25,
    card: Optional[str] = None,
    area: Optional[str] = None,
    level: Optional[str] = None,
    role: Optional[Literal["owner", "admin", "member"]] = None,
    title: Optional[str] = None,
) -> Sender:
    return Sender(
        user_id=user_id,
        nickname=nickname,
        sex=sex,
        age=age,
        card=card,
        area=area,
        level=level,
        role=role,
        title=title,
    )


def create_reply(
    message_id: int | None = None,
    message_type: Literal["private", "group"] = "group",
    message: Message = Message("Test message"),
    sender_id: int = 123456,
    sender_nickname: str = "TestUser",
) -> Reply:
    global message_id_increment
    if message_id is None:
        message_id_increment += 1
        message_id = message_id_increment

    return Reply(
        time=0,
        message_type=message_type,
        message_id=message_id,
        real_id=0,
        sender=create_sender(sender_id, sender_nickname),
        message=message,
    )


def create_private_message_event(
    message: str,
    message_id: int | None = None,
    sender_id: int = 123456,
    sender_nickname: str = "TestUser",
    sub_type: Literal["friend", "group", "other"] = "friend",
    to_me: bool = True,
    reply: Optional[Reply] = None,
) -> MessageEvent:
    global message_id_increment
    if message_id is None:
        message_id_increment += 1
        message_id = message_id_increment

    sender = create_sender(user_id=sender_id, nickname=sender_nickname)
    return PrivateMessageEvent(
        time=0,
        self_id=0,
        post_type="message",
        sub_type=sub_type,
        user_id=sender_id,
        message_type="private",
        message_id=message_id,
        message=Message(message),
        original_message=Message(message),
        raw_message=message,
        font=0,
        sender=sender,
        to_me=to_me,
        reply=reply,
    )


def create_group_message_event(
    message: str,
    message_id: int | None = None,
    sender_id: int = 123456,
    sender_nickname: str = "TestUser",
    group_id: int = 321,
    role: Literal["owner", "admin", "member"] = "member",
    sub_type: Literal["normal", "anonymous", "other"] = "normal",
    to_me: bool = False,
    reply: Optional[Reply] = None,
) -> GroupMessageEvent:
    """
    Please note that the default group_id is 321, which should be the configured group.
    """
    global message_id_increment
    if message_id is None:
        message_id_increment += 1
        message_id = message_id_increment

    sender = create_sender(user_id=sender_id, nickname=sender_nickname, role=role)
    return GroupMessageEvent(
        time=0,
        self_id=0,
        post_type="message",
        sub_type=sub_type,
        user_id=sender_id,
        group_id=group_id,
        message_type="group",
        message_id=message_id,
        message=Message(message),
        original_message=Message(message),
        raw_message=message,
        font=0,
        sender=sender,
        to_me=to_me,
        reply=reply,
    )
