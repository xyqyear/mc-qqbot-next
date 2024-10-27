from nonebot_plugin_orm import async_scoped_session

from .model import QQUUIDMapping


async def get_mapping_by_qq_id(
    session: async_scoped_session, qq_id: str
) -> QQUUIDMapping | None:
    return await session.get(QQUUIDMapping, qq_id)


async def create_qq_uuid_mapping(
    session: async_scoped_session, qq_id: str, uuid: str, name_cache: str
) -> None:
    mapping = QQUUIDMapping(qq_id=qq_id, uuid=uuid, name_cache=name_cache)
    session.add(mapping)


async def update_name_cache(
    session: async_scoped_session, qq_id: str, name_cache: str
) -> None:
    if result := await session.get(QQUUIDMapping, qq_id):
        result.player_name = name_cache
        session.add(result)
