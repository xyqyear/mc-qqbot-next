from nonebot import CommandGroup
from nonebot.params import Depends
from nonebot.permission import SUPERUSER, Permission

from ...bot import construct_single_forward_message_segment
from ...dependencies import extract_arg_and_target
from ...docker import send_rcon_command
from ...log import logger
from ...permission import group_admin_or_owner
from ...rules import is_from_configured_group

whitelist = CommandGroup(
    "whitelist",
)
whitelist_add = whitelist.command(
    "add",
    rule=is_from_configured_group,
    permission=SUPERUSER | Permission(group_admin_or_owner),
)
whitelist_remove = whitelist.command(
    "remove",
    rule=is_from_configured_group,
    permission=SUPERUSER | Permission(group_admin_or_owner),
)
whitelist_list = whitelist.command(
    "list",
)


@whitelist_add.handle()
async def handle_whitelist_add(
    arg_and_target: tuple[str, str] = Depends(extract_arg_and_target),
):
    command_content, target_server = arg_and_target
    logger.info(f"Trying to add {command_content} to whitelist on {target_server}")
    result = await send_rcon_command(target_server, f"whitelist add {command_content}")
    await whitelist_add.finish(result)


@whitelist_remove.handle()
async def handle_whitelist_remove(
    arg_and_target: tuple[str, str] = Depends(extract_arg_and_target),
):
    command_content, target_server = arg_and_target
    logger.info(f"Trying to remove {command_content} from whitelist on {target_server}")
    result = await send_rcon_command(
        target_server, f"whitelist remove {command_content}"
    )
    await whitelist_remove.finish(result)


@whitelist_list.handle()
async def handle_whitelist_list(
    arg_and_target: tuple[str, str] = Depends(extract_arg_and_target),
):
    target_server = arg_and_target[1]
    logger.info(f"Trying to list whitelist on {target_server}")
    result = await send_rcon_command(target_server, "whitelist list")
    message = construct_single_forward_message_segment(result)
    await whitelist_list.finish(message)
