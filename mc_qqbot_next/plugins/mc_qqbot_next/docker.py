import asyncio
from typing import Literal

from minecraft_docker_manager_lib.manager import DockerMCManager

from .config import config
from .log import logger

docker_mc_manager = DockerMCManager(config.mc_servers_root_path)


async def get_running_server_names():
    """
    获取所有运行中的 Minecraft 服务器名称
    会过滤掉 config.excluded_servers 中的服务器
    """
    running_servers = await docker_mc_manager.get_running_server_names()
    return list(
        filter(
            lambda server_name: server_name not in config.mc_excluded_servers,
            running_servers,
        )
    )


async def get_port_sorted_running_server_names():
    """
    获取所有运行中的 Minecraft 服务器名称，并按照端口号排序
    会过滤掉 config.excluded_servers 中的服务器
    """
    running_servers = await get_running_server_names()
    servers_info = await asyncio.gather(
        *[
            docker_mc_manager.get_instance(server_name).get_server_info()
            for server_name in running_servers
        ]
    )
    servers_info = sorted(servers_info, key=lambda server_info: server_info.game_port)
    return [server_info.name for server_info in servers_info]


async def get_running_server_name_with_lowest_port():
    """
    获取端口号最小的运行中的 Minecraft 服务器名称
    会过滤掉 config.excluded_servers 中的服务器
    """
    running_servers = await get_port_sorted_running_server_names()
    if running_servers:
        return running_servers[0]
    return None


async def send_rcon_command(server_name: str, command: str):
    """
    向 Minecraft 服务器发送 RCON 命令
    """
    logger.info(f"Sending RCON command to {server_name}: {command}")
    result = await docker_mc_manager.get_instance(server_name).send_command_rcon(
        command
    )
    logger.info(f"RCON command result: {result}")
    return f"[{server_name}] {result}"


async def restart_server(server_name: str):
    """
    重启 Minecraft 服务器
    """
    logger.info(f"Restarting {server_name}")
    return await docker_mc_manager.get_instance(server_name).restart()


async def healthy(server_name: str):
    """
    检查 Minecraft 服务器是否健康
    """
    logger.trace(f"Checking health of {server_name}")
    return await docker_mc_manager.get_instance(server_name).healthy()


async def get_instance(server_name: str):
    """
    获取 Minecraft 服务器实例
    """
    logger.trace(f"Getting instance of {server_name}")
    return docker_mc_manager.get_instance(server_name)


async def locate_server_name_with_prefix(prefix: str):
    """
    通过前缀查找匹配的服务器名称

    Args:
        prefix (str): 要查找的服务器名称前缀

    Returns:
        str | None:
            - 如果找到完全匹配的服务器名称，返回该名称
            - 如果找到前缀匹配的服务器名称，返回第一个匹配的名称
            - 如果没有找到匹配的服务器名称，返回 None

    Example:
        假设服务器列表为 ['test1', 'test2', 'prod']
        - locate_server_name('test1') 返回 'test1'
        - locate_server_name('test') 返回 'test1'
        - locate_server_name('dev') 返回 None
    """
    logger.debug(f"Locating server name with prefix: {prefix}")
    all_server_names = await get_port_sorted_running_server_names()
    if prefix in all_server_names:
        logger.debug(f"Found exact match: {prefix}")
        return prefix
    for server_name in all_server_names:
        if server_name.startswith(prefix):
            logger.debug(f"Found prefix match: {server_name}")
            return server_name
    logger.debug("No match found")
    return None


async def list_players(
    server_name: str, timeout: int = config.mc_list_players_timeout_seconds
):
    """
    获取 Minecraft 服务器在线玩家列表

    Args:
        server_name (str): 服务器名称
        timeout (int): 超时时间

    Returns:
        list[str] | None: 在线玩家列表或获取失败时为 None
    """
    instance = docker_mc_manager.get_instance(server_name)
    if await instance.paused():
        logger.warning(f"Server {server_name} is paused")
        return list[str]()
    task = instance.list_players()
    try:
        return await asyncio.wait_for(task, timeout)
    except asyncio.TimeoutError:
        logger.warning(
            f"Timeout when listing players for {server_name}. timeout={timeout}"
        )
        return None
    except RuntimeError as e:
        logger.warning(f"Error when listing players for {server_name}: {e}")
        return None


async def list_players_for_all_servers():
    """
    获取所有运行中的 Minecraft 服务器及其在线玩家列表

    Returns:
        dict[str, list[str] | None]:
            - 键为服务器名称 (str)
            - 值为在线玩家列表 (list[str]) 或获取失败时为 None

    Example:
        假设有三个服务器运行中：
        {
            "survival": ["player1", "player2"],
            "creative": ["player3"],
            "minigames": None  # 获取玩家列表失败
        }
    """
    server_name_list = await get_port_sorted_running_server_names()

    online_players_list = await asyncio.gather(
        *[list_players(server_name) for server_name in server_name_list],
        return_exceptions=True,
    )

    online_players_list = [
        players if not isinstance(players, BaseException) else None
        for players in online_players_list
    ]

    return {
        server_name: players
        for server_name, players in zip(server_name_list, online_players_list)
    }


ColorsT = Literal[
    "black",
    "dark_blue",
    "dark_green",
    "dark_aqua",
    "dark_red",
    "dark_purple",
    "gold",
    "gray",
    "dark_gray",
    "blue",
    "green",
    "aqua",
    "red",
    "light_purple",
    "yellow",
    "white",
]


async def tell_raw(
    message: str,
    server_name: str,
    target: str = "@a",
    color: ColorsT = "yellow",
):
    message = message.replace("\\", "\\\\").replace('"', '\\"')
    for line in message.splitlines():
        await send_rcon_command(
            server_name, f'tellraw {target} {{"text": "{line}", "color": "{color}"}}'
        )


async def send_message(
    message: str,
    target_server: str | None = None,
    target_player: str | None = None,
    color: ColorsT = "yellow",
):
    """
    向 Minecraft 服务器发送消息

    Args:
        message (str): 要发送的消息
        target_server (str | None): 目标服务器名称
        target_player (str): 目标玩家，默认为 "@a"
        color (ColorsT): 消息颜色，默认为 "yellow"

    Returns:
        list[str]: 发送失败的服务器名称列表
    """
    if target_server is None:
        target_servers = await get_running_server_names()
    else:
        target_servers = [target_server]

    if target_player is None:
        target_player = "@a"

    logger.info(f"Sending {message} to {target_player} in {target_servers}")
    tasks = [
        tell_raw(message, server_name, target_player, color)
        for server_name in target_servers
    ]
    result = await asyncio.gather(*tasks, return_exceptions=True)

    return [
        server_name
        for server_name, r in zip(target_servers, result)
        if isinstance(r, BaseException)
    ]
