import pytest


@pytest.mark.asyncio
async def test_uuid_name_mapping():
    from nonebot_plugin_orm import get_session, init_orm

    from mc_qqbot_next.plugins.mc_qqbot_next.db.crud import (
        create_mc_player_info,
        delete_mc_player_info,
        get_uuid_by_player_name,
    )

    await init_orm()
    session = get_session()
    async with session.begin():
        await create_mc_player_info(
            session, "069a79f444e94726a5befca90e38aaf5", "Notch"
        )
        assert (
            await get_uuid_by_player_name(session, "Notch")
            == "069a79f444e94726a5befca90e38aaf5"
        )
        await delete_mc_player_info(session, "069a79f444e94726a5befca90e38aaf5")


@pytest.mark.asyncio
async def test_all():
    from nonebot_plugin_orm import get_session, init_orm

    from mc_qqbot_next.plugins.mc_qqbot_next.db.crud import (
        create_qq_uuid_mapping,
        create_qq_uuid_mapping_by_player_name,
        delete_mc_player_info,
        delete_qq_uuid_mapping,
        get_player_name_by_qq_id,
        get_qq_by_player_name,
        get_uuid_by_player_name,
    )

    await init_orm()
    session = get_session()
    async with session.begin():
        await create_qq_uuid_mapping_by_player_name(session, "123456", "Notch")
        assert await get_player_name_by_qq_id(session, "123456") == "Notch"
        assert await get_qq_by_player_name(session, "Notch") == "123456"
        assert (
            await get_uuid_by_player_name(session, "Notch")
            == "069a79f444e94726a5befca90e38aaf5"
        )

        await delete_qq_uuid_mapping(session, "123456")
        assert await get_player_name_by_qq_id(session, "123456") is None
        assert await get_qq_by_player_name(session, "Notch") is None

        await create_qq_uuid_mapping_by_player_name(session, "654321", "Notch")
        assert await get_player_name_by_qq_id(session, "654321") == "Notch"

        await delete_qq_uuid_mapping(session, "654321")
        await delete_mc_player_info(session, "069a79f444e94726a5befca90e38aaf5")

        assert await get_player_name_by_qq_id(session, "654321") is None

        # ---

        await create_qq_uuid_mapping(
            session, "123456", "069a79f444e94726a5befca90e38aaf5"
        )
        assert await get_player_name_by_qq_id(session, "123456") == "Notch"
        await delete_qq_uuid_mapping(session, "123456")


def test_true():
    assert True
