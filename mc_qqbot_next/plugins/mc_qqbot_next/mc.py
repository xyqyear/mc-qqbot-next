import re
from dataclasses import dataclass
from typing import Literal

import aiohttp
from aiohttp import ClientTimeout
from pydantic import BaseModel

from .log import logger


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
            f"https://sessionserver.mojang.com/session/minecraft/profile/{uuid.replace('-', '')}",
            timeout=ClientTimeout(total=timeout),
        ) as response:
            # make sure the response code is 200 OK
            response.raise_for_status()
            if response.status != 200:
                logger.error(
                    f"Failed to fetch profile for UUID {uuid}: {response.status}"
                )
                raise aiohttp.ClientError("Failed to fetch profile from Mojang API")
            profile_data = await response.json()
            profile = MinecraftProfile(**profile_data)
            logger.debug(f"Got name for {profile.id} from Mojang API: {profile.name}")
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
            logger.debug(f"Got UUID for {profile.name} from Mojang API: {profile.id}")
            return profile.id


@dataclass
class PlayerInfo:
    uuid: str
    name: str


def parse_player_uuid_and_name_from_log(log_content: str):
    """
    Parse player UUID and name from log content.
    The uuid in return object is without dashes.

    Examples:
        [00:00:00] [User Authenticator #1/INFO]: UUID of player Notch is 069a79f4-44e9-4726-a5be-fca90e38aaf5
        [00:00:00] [User Authenticator #1/INFO]: UUID of player Notch is 069a79f4-44e9-4726-a5be-fca90e38aaf5

    Returns:
        list[PlayerInfo]: List of player UUID and name.
    """
    # ^\[[^\]]+\]                 # Match the first bracket with any characters except ']'
    # \s+                         # One or more whitespace characters
    # \[User Authenticator.*?\]:  # Match 'User Authenticator' in the second bracket
    # UUID of player (\w+) is ([a-f0-9\-]{36})$  # Capture username and UUID
    pattern = re.compile(
        r"^\[[^\]]+\]\s+\[User Authenticator.*?\]: UUID of player (\w+) is ([a-f0-9\-]{36})$"
    )

    player_info_list = list[PlayerInfo]()
    for line in log_content.splitlines():
        match = pattern.match(line)
        if match:
            name, uuid = match.groups()
            player_info_list.append(PlayerInfo(uuid=uuid.replace("-", ""), name=name))

    return player_info_list
