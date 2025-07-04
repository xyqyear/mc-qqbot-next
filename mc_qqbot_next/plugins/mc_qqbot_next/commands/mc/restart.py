import asyncio
import time

from nonebot import on_command
from nonebot.params import Depends
from nonebot.permission import SUPERUSER, Permission

from ...config import config
from ...dependencies import CommandTarget, extract_arg_and_target
from ...docker import healthy, restart_server
from ...log import logger
from ...permission import group_admin_or_owner
from ...rules import is_from_configured_group

restart = on_command(
    "restart",
    rule=is_from_configured_group,
    permission=SUPERUSER | Permission(group_admin_or_owner),
)


@restart.handle()
async def handle_restart(
    command_target: CommandTarget = Depends(extract_arg_and_target),
):
    if not command_target.is_explicit:
        await restart.finish("重启服务器需要明确指定目标服务器")
    
    target_server = command_target.target_server
    logger.info(f"Trying to restart {target_server}")
    await restart_server(target_server)
    await restart.send(f"[{target_server}] 正在重启")
    before_time = time.perf_counter()
    # we only wait for 10 minutes for the server to be healthy
    while time.perf_counter() - before_time < config.mc_restart_wait_seconds:
        if await healthy(target_server):
            await restart.finish(f"[{target_server}] 重启完成")
            return
        await asyncio.sleep(1)
    logger.info(
        f"Restarting {target_server} timeout after {config.mc_restart_wait_seconds} seconds"
    )
    await restart.finish(
        f"[{target_server}] 坏了，好像过了{config.mc_restart_wait_seconds//60}分钟了还没重启好"
    )
