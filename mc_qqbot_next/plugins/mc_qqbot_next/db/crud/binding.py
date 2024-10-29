from sqlalchemy import select

from ...mc import find_name_by_uuid, find_uuid_by_name
from ..model import MCPlayerInfo, QQUUIDMapping
from . import get_session_scope


async def get_player_name_by_qq_id(qq_id: str) -> str | None:
    async with get_session_scope() as session:
        query = (
            select(MCPlayerInfo.name)
            .select_from(QQUUIDMapping)
            .join(QQUUIDMapping.mc_player_info)
            .where(QQUUIDMapping.qq_id == qq_id)
        )
        return await session.scalar(query)


async def get_qq_by_player_name(
    player_name: str,
) -> str | None:
    async with get_session_scope() as session:
        query = (
            select(QQUUIDMapping.qq_id)
            .select_from(QQUUIDMapping)
            .join(QQUUIDMapping.mc_player_info)
            .where(MCPlayerInfo.name == player_name)
        )
        return await session.scalar(query)


async def get_uuid_by_player_name(
    player_name: str,
) -> str | None:
    async with get_session_scope() as session:
        query = select(MCPlayerInfo.uuid).where(MCPlayerInfo.name == player_name)
        return await session.scalar(query)


async def create_qq_uuid_mapping_by_player_name(qq_id: str, name: str) -> None:
    """
    Create a QQ-UUID mapping by player name.

    Raises:
        ValueError: If the player name is invalid.
        aiohttp.ClientError: If an error occurs while fetching data from Mojang API.
        asyncio.TimeoutError: If the request to Mojang API times out.
    """
    async with get_session_scope() as session:
        mc_player_info_query_result = await session.execute(
            select(MCPlayerInfo).where(MCPlayerInfo.name == name)
        )
        mc_player_info = mc_player_info_query_result.scalar()
        if mc_player_info:
            player_uuid = mc_player_info.uuid
        else:
            player_uuid = await find_uuid_by_name(name)
            mc_player_info = MCPlayerInfo(uuid=player_uuid, name=name)
            session.add(mc_player_info)
        mapping = QQUUIDMapping(qq_id=qq_id, uuid=player_uuid)
        session.add(mapping)


async def create_qq_uuid_mapping(qq_id: str, uuid: str) -> None:
    """
    Create a QQ-UUID mapping.

    Raises:
        ValueError: If the UUID is invalid.
        aiohttp.ClientError: If an error occurs while fetching data from Mojang API.
        asyncio.TimeoutError: If the request to Mojang API times out.
    """
    async with get_session_scope() as session:
        mc_player_info = await session.get(MCPlayerInfo, uuid)
        if not mc_player_info:
            player_name = await find_name_by_uuid(uuid)
            mc_player_info = MCPlayerInfo(uuid=uuid, name=player_name)
            session.add(mc_player_info)
        mapping = QQUUIDMapping(qq_id=qq_id, uuid=uuid)
        session.add(mapping)


async def delete_qq_uuid_mapping(qq_id: str) -> None:
    """
    Remove a QQ-UUID mapping.
    """
    async with get_session_scope() as session:
        if result := await session.get(QQUUIDMapping, qq_id):
            await session.delete(result)


async def create_or_update_mc_player_info(uuid: str, name: str) -> None:
    """
    Create or update a player.
    """
    async with get_session_scope() as session:
        if result := await session.get(MCPlayerInfo, uuid):
            result.name = name
        else:
            mc_player_info = MCPlayerInfo(uuid=uuid, name=name)
            session.add(mc_player_info)


async def delete_mc_player_info(uuid: str) -> None:
    """
    Remove a player.

    This function is only used in test.
    because there is no need to remove uuid and player name mapping.
    """
    async with get_session_scope() as session:
        if result := await session.get(MCPlayerInfo, uuid):
            await session.delete(result)
