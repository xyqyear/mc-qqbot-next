from nonebot.adapters.onebot.v11.event import GroupMessageEvent


async def is_from_configured_group(event: GroupMessageEvent) -> bool:
    return event.group_id == event.group_id
