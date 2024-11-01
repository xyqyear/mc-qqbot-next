from nonebot import get_bots
from nonebot.adapters.onebot.v11.bot import Bot
from nonebot.adapters.onebot.v11.message import MessageSegment


def get_onebot_bot() -> Bot | None:
    bots = get_bots()
    for bot in bots.values():
        if isinstance(bot, Bot):
            return bot
    return None


def construct_single_forward_message_segment(message_content: str):
    bot = get_onebot_bot()
    if not bot:
        return None
    return MessageSegment.node_custom(
        user_id=int(bot.self_id), nickname="", content=message_content
    )
