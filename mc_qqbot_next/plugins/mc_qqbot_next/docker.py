import asyncio

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

    # for easier exception handling
    async def get_online_players(server_info):
        try:
            return await docker_mc_manager.get_instance(server_info.name).list_players()
        except Exception:
            return None

    online_players_list: list[list[str] | None] = await asyncio.gather(
        *[get_online_players(server_info) for server_info in servers_info]
    )
    return {
        server_info.name: players
        for server_info, players in zip(servers_info, online_players_list)
    }
