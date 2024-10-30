from nonebot.adapters.onebot.v11.event import GroupMessageEvent

from .config import config


async def is_from_configured_group(event: GroupMessageEvent) -> bool:
    return event.group_id == config.group_id
