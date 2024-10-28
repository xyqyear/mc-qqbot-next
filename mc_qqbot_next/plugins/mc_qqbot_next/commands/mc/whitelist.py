from nonebot import CommandGroup
from nonebot.params import Depends
from nonebot.permission import SUPERUSER, Permission

from ...dependencies import extract_arg_and_target
from ...docker import docker_mc_manager
from ...permission import group_admin_or_owner
from ...rules import is_from_configured_group

whitelist = CommandGroup(
    "whitelist",
    rule=is_from_configured_group,
    permission=SUPERUSER | Permission(group_admin_or_owner),
)
whitelist_add = whitelist.command(
    "add",
)
whitelist_remove = whitelist.command(
    "remove",
)
whitelist_list = whitelist.command(
    "list",
)


@whitelist_add.handle()
async def handle_whitelist_add(
    arg_and_target: tuple[str, str] = Depends(extract_arg_and_target),
):
    command_content, target_server = arg_and_target
    result = await docker_mc_manager.get_instance(target_server).send_command_rcon(
        f"whitelist add {command_content}"
    )
    await whitelist_add.finish(result)


@whitelist_remove.handle()
async def handle_whitelist_remove(
    arg_and_target: tuple[str, str] = Depends(extract_arg_and_target),
):
    command_content, target_server = arg_and_target
    result = await docker_mc_manager.get_instance(target_server).send_command_rcon(
        f"whitelist remove {command_content}"
    )
    await whitelist_remove.finish(result)


@whitelist_list.handle()
async def handle_whitelist_list(
    arg_and_target: tuple[str, str] = Depends(extract_arg_and_target),
):
    target_server = arg_and_target[1]
    result = await docker_mc_manager.get_instance(target_server).send_command_rcon(
        "whitelist list"
    )
    await whitelist_list.finish(result)
