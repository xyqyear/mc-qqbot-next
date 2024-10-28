import asyncio
from typing import Literal

import aiohttp
from aiohttp import ClientTimeout
from pydantic import BaseModel

from .config import config
from .docker import docker_mc_manager


class TextureProperty(BaseModel):
    name: str
    value: str


class MinecraftProfile(BaseModel):
    id: str
    name: str
    properties: list[TextureProperty]
    profileActions: list[Literal["FORCED_NAME_CHANGE", "USING_BANNED_SKIN"]]


async def uuid2name(uuid: str, timeout: int = 5):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f'https://sessionserver.mojang.com/session/minecraft/profile/{uuid.replace("-", "")}',
            timeout=ClientTimeout(total=timeout),
        ) as response:
            profile_data = await response.json()
            profile = MinecraftProfile(**profile_data)
            return profile.name


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