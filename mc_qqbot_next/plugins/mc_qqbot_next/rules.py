from nonebot.adapters.onebot.v11.event import GroupMessageEvent

from .config import config
from .log import logger


async def is_from_configured_group(event: GroupMessageEvent) -> bool:
    logger.trace(
        f"Checking if {event.group_id} is in {config.mc_group_id}. Message: {event.message.extract_plain_text()}"
    )
    return event.group_id == config.mc_group_id


async def has_reply(event: GroupMessageEvent) -> bool:
    logger.trace(f"Checking if {event.reply} has reply")
    return event.reply is not None
