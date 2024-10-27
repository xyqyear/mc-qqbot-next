import asyncio
import time

from nonebot import on_command
from nonebot.params import Depends
from nonebot.permission import SUPERUSER, Permission

from ...config import config
from ...dependencies import extract_arg_and_target
from ...docker import docker_mc_manager
from ...permission import group_admin_or_owner
from ...rules import is_from_configured_group

restart = on_command(
    "restart",
    rule=is_from_configured_group,
    permission=SUPERUSER | Permission(group_admin_or_owner),
)


@restart.handle()
async def handle_restart(
    arg_and_target: tuple[str, str] = Depends(extract_arg_and_target),
):
    _, target_server = arg_and_target
    await docker_mc_manager.get_instance(target_server).restart()
    await restart.send(f"[{target_server}] 正在重启")
    before_time = time.perf_counter()
    # we only wait for 10 minutes for the server to be healthy
    while time.perf_counter() - before_time < config.restart_wait_seconds:
        if await docker_mc_manager.get_instance(target_server).healthy():
            await restart.finish(f"[{target_server}] 重启完成")
            return
        await asyncio.sleep(1)
    await restart.finish(
        f"[{target_server}] 坏了，好像过了{config.restart_wait_seconds//60}分钟了还没重启好"
    )
