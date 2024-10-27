from nonebot import on_command
from nonebot.params import Depends

from ...dependencies import extract_arg_and_target
from ...docker import docker_mc_manager

banlist = on_command(
    "banlist",
)


@banlist.handle()
async def handle_banlist(
    arg_and_target: tuple[str, str] = Depends(extract_arg_and_target),
):
    command_content, target_server = arg_and_target
    result = await docker_mc_manager.get_instance(target_server).send_command_rcon(
        "banlist"
    )
    await banlist.finish(result)
