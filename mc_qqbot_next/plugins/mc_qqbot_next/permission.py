from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.adapters.onebot.v11.bot import Bot
from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER
from nonebot.matcher import Matcher

group_admin_or_owner_permission = GROUP_ADMIN | GROUP_OWNER


async def group_admin_or_owner(
    matcher: Matcher, bot: Bot, msg: GroupMessageEvent
) -> bool:
    permission_passed = await group_admin_or_owner_permission(bot, msg)
    if not permission_passed:
        await matcher.finish("权限不足")
    return True
