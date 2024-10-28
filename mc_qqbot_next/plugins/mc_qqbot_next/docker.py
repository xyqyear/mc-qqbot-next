import asyncio
from typing import Literal

from minecraft_docker_manager_lib.manager import DockerMCManager

from .config import config

docker_mc_manager = DockerMCManager(config.servers_root_path)


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
    all_server_names = await docker_mc_manager.get_running_server_names()
    if prefix in all_server_names:
        return prefix
    for server_name in all_server_names:
        if server_name.startswith(prefix):
            return server_name
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
    running_servers = await docker_mc_manager.get_running_server_names()
    running_servers = list(
        filter(
            lambda server_name: server_name not in config.excluded_servers,
            running_servers,
        )
    )
    # server_info is used for sorting the servers by game_port
    servers_info = await asyncio.gather(
        *[
            docker_mc_manager.get_instance(server_name).get_server_info()
            for server_name in running_servers
        ]
    )
    servers_info = sorted(servers_info, key=lambda server_info: server_info.game_port)

    online_players_list = await asyncio.gather(
        *[
            docker_mc_manager.get_instance(server_info.name).list_players()
            for server_info in servers_info
        ],
        return_exceptions=True,
    )

    online_players_list = [
        players if not isinstance(players, BaseException) else None
        for players in online_players_list
    ]

    return {
        server_info.name: players
        for server_info, players in zip(servers_info, online_players_list)
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


async def send_message(
    message: str,
    target_server: str | None,
    target_player: str = "@a",
    color: ColorsT = "yellow",
):
    """
    向 Minecraft 服务器发送消息

    Args:
        message (str): 要发送的消息
        target_server (str | None): 目标服务器名称
        target_player (str): 目标玩家，默认为 "@a" (所有玩家)
        color (ColorsT): 消息颜色，默认为 "yellow"

    Returns:
        list[str]: 发送失败的服务器名称列表
    """
    if target_server is None:
        target_servers = await docker_mc_manager.get_running_server_names()
    else:
        target_servers = [target_server]

    tasks = [
        docker_mc_manager.get_instance(server_name).send_command_rcon(
            f'tellraw {target_player} {{"text": "{message}", "color": "{color}"}}'
        )
        for server_name in target_servers
    ]
    result = await asyncio.gather(*tasks, return_exceptions=True)

    return [
        server_name
        for server_name, r in zip(target_servers, result)
        if isinstance(r, BaseException)
    ]
