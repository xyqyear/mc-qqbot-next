from nonebot import on_command
from nonebot.params import Depends
from nonebot.permission import SUPERUSER, Permission

from ...dependencies import extract_arg_and_target
from ...docker import send_rcon_command
from ...log import logger
from ...permission import group_admin_or_owner
from ...rules import is_from_configured_group

unban = on_command(
    "unban",
    rule=is_from_configured_group,
    permission=SUPERUSER | Permission(group_admin_or_owner),
)


@unban.handle()
async def handle_unban(
    arg_and_target: tuple[str, str] = Depends(extract_arg_and_target),
):
    command_content, target_server = arg_and_target
    logger.info(f"Trying to unban {command_content} on {target_server}")
    result = await send_rcon_command(target_server, f"pardon {command_content}")
    await unban.finish(result)
