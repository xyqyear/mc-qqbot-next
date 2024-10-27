from nonebot import on_command
from nonebot.params import Depends
from nonebot.permission import SUPERUSER, Permission

from ...dependencies import extract_arg_and_target
from ...docker import docker_mc_manager
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
    result = await docker_mc_manager.get_instance(target_server).send_command_rcon(
        f"pardon {command_content}"
    )
    await unban.finish(result)
