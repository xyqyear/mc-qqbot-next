from contextlib import asynccontextmanager

from nonebot_plugin_orm import get_session


@asynccontextmanager
async def get_session_scope():
    session = get_session()
    async with session.begin():
        yield session
