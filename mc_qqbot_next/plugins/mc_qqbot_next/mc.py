from typing import Literal

import aiohttp
from aiohttp import ClientTimeout
from pydantic import BaseModel


class TextureProperty(BaseModel):
    name: str
    value: str


class MinecraftProfile(BaseModel):
    id: str
    name: str
    properties: list[TextureProperty]
    profileActions: list[Literal["FORCED_NAME_CHANGE", "USING_BANNED_SKIN"]]


async def find_name_by_uuid(uuid: str, timeout: int = 5):
    """
    Raises:
        ValueError: If the UUID is invalid.
        aiohttp.ClientError: If an error occurs while fetching data from Mojang API.
        asyncio.TimeoutError: If the request to Mojang API times out.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f'https://sessionserver.mojang.com/session/minecraft/profile/{uuid.replace("-", "")}',
            timeout=ClientTimeout(total=timeout),
        ) as response:
            profile_data = await response.json()
            if "errorMessage" in profile_data:
                raise ValueError("Invalid UUID")
            profile = MinecraftProfile(**profile_data)
            return profile.name


class MinecraftIDName(BaseModel):
    id: str
    name: str


async def find_uuid_by_name(name: str, timeout: int = 5):
    """
    Raises:
        ValueError: If the player name is invalid.
        aiohttp.ClientError: If an error occurs while fetching data from Mojang API.
        asyncio.TimeoutError: If the request to Mojang API times out.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://api.mojang.com/users/profiles/minecraft/{name}",
            timeout=ClientTimeout(total=timeout),
        ) as response:
            profile_data = await response.json()
            if "errorMessage" in profile_data:
                raise ValueError("Invalid Name")
            profile = MinecraftIDName(**profile_data)
            return profile.id
