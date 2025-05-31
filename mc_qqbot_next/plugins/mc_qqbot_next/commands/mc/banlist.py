from nonebot import on_command
from nonebot.params import Depends

from ...dependencies import CommandTarget, extract_arg_and_target
from ...docker import send_rcon_command
from ...log import logger

banlist = on_command(
    "banlist",
)


@banlist.handle()
async def handle_banlist(
    command_target: CommandTarget = Depends(extract_arg_and_target),
):
    target_server = command_target.target_server
    logger.info(f"Trying to get banlist on {target_server}")
    result = await send_rcon_command(target_server, "banlist")
    await banlist.finish(result)
