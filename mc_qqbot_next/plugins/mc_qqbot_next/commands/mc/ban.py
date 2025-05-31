from nonebot import on_command
from nonebot.params import Depends
from nonebot.permission import SUPERUSER, Permission

from ...dependencies import CommandTarget, extract_arg_and_target
from ...docker import send_rcon_command
from ...log import logger
from ...permission import group_admin_or_owner
from ...rules import is_from_configured_group

ban = on_command(
    "ban",
    rule=is_from_configured_group,
    permission=SUPERUSER | Permission(group_admin_or_owner),
)


@ban.handle()
async def handle_ban(
    command_target: CommandTarget = Depends(extract_arg_and_target),
):
    command_content, target_server = command_target.arg, command_target.target_server
    logger.info(f"Trying to ban {command_content} on {target_server}")
    result = await send_rcon_command(target_server, f"ban {command_content}")
    await ban.finish(result)
