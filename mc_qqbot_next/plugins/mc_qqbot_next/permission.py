from nonebot.adapters.onebot.v11 import GroupMessageEvent
from nonebot.adapters.onebot.v11.bot import Bot
from nonebot.adapters.onebot.v11.permission import GROUP_ADMIN, GROUP_OWNER

group_admin_or_owner_permission = GROUP_ADMIN | GROUP_OWNER


async def group_admin_or_owner(bot: Bot, msg: GroupMessageEvent) -> bool:
    permission_passed = await group_admin_or_owner_permission(bot, msg)
    if not permission_passed:
        await bot.send_group_msg(group_id=msg.group_id, message="权限不足")
        return False
    return True
