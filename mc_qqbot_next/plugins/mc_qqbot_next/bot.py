from nonebot import get_bots
from nonebot.adapters.onebot.v11.bot import Bot


def get_onebot_bot() -> Bot | None:
    bots = get_bots()
    for bot in bots.values():
        if isinstance(bot, Bot):
            return bot
    return None
