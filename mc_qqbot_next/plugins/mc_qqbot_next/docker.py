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
