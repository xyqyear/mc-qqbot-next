from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.adapters.onebot.v11.bot import Bot
from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER

group_admin_or_owner_permission = GROUP_ADMIN | GROUP_OWNER


async def group_admin_or_owner(bot: Bot, event: GroupMessageEvent) -> bool:
    permission_passed = await group_admin_or_owner_permission(bot, event)
    if not permission_passed:
        return False
    return True
