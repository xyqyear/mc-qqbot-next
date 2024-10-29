import pytest
from sqlalchemy.exc import IntegrityError


@pytest.mark.asyncio
async def test_message_target():
    from nonebot_plugin_orm import init_orm

    from mc_qqbot_next.plugins.mc_qqbot_next.db.crud.message import (
        create_message_target,
        delete_message_target_by_message_id,
        get_message_target_by_message_id,
    )

    await init_orm()
    await create_message_target(123456)
    message_target = await get_message_target_by_message_id(123456)
    assert message_target is not None
    assert message_target.target_server is None
    assert message_target.target_player is None
    await create_message_target(654321, "server", "player")
    message_target = await get_message_target_by_message_id(654321)
    assert message_target is not None
    assert message_target.target_server == "server"
    assert message_target.target_player == "player"

    await delete_message_target_by_message_id(123456)
    assert await get_message_target_by_message_id(123456) is None
    await delete_message_target_by_message_id(654321)


@pytest.mark.asyncio
async def test_uuid_name_mapping():
    from nonebot_plugin_orm import init_orm

    from mc_qqbot_next.plugins.mc_qqbot_next.db.crud.binding import (
        create_or_update_mc_player_info,
        delete_mc_player_info,
        get_uuid_by_player_name,
    )

    await init_orm()
    await create_or_update_mc_player_info("069a79f444e94726a5befca90e38aaf5", "Notch")
    assert await get_uuid_by_player_name("Notch") == "069a79f444e94726a5befca90e38aaf5"
    await create_or_update_mc_player_info("069a79f444e94726a5befca90e38aaf5", "Dream")
    assert await get_uuid_by_player_name("Dream") == "069a79f444e94726a5befca90e38aaf5"
    await delete_mc_player_info("069a79f444e94726a5befca90e38aaf5")


@pytest.mark.asyncio
async def test_avoid_duplicated_binding():
    from nonebot_plugin_orm import init_orm

    from mc_qqbot_next.plugins.mc_qqbot_next.db.crud.binding import (
        create_qq_uuid_mapping_by_player_name,
        delete_mc_player_info,
        delete_qq_uuid_mapping,
    )

    await init_orm()
    await create_qq_uuid_mapping_by_player_name("123456", "Notch")
    with pytest.raises(IntegrityError):
        await create_qq_uuid_mapping_by_player_name("654321", "Notch")
    with pytest.raises(IntegrityError):
        await create_qq_uuid_mapping_by_player_name("123456", "Dream")
    await delete_qq_uuid_mapping("123456")
    await delete_mc_player_info("069a79f444e94726a5befca90e38aaf5")


@pytest.mark.asyncio
async def test_all():
    from nonebot_plugin_orm import init_orm

    from mc_qqbot_next.plugins.mc_qqbot_next.db.crud.binding import (
        create_qq_uuid_mapping,
        create_qq_uuid_mapping_by_player_name,
        delete_mc_player_info,
        delete_qq_uuid_mapping,
        get_player_name_by_qq_id,
        get_qq_by_player_name,
        get_uuid_by_player_name,
    )

    await init_orm()
    await create_qq_uuid_mapping_by_player_name("123456", "Notch")
    assert await get_player_name_by_qq_id("123456") == "Notch"
    assert await get_qq_by_player_name("Notch") == "123456"
    assert await get_uuid_by_player_name("Notch") == "069a79f444e94726a5befca90e38aaf5"

    await delete_qq_uuid_mapping("123456")
    assert await get_player_name_by_qq_id("123456") is None
    assert await get_qq_by_player_name("Notch") is None

    await create_qq_uuid_mapping_by_player_name("654321", "Notch")
    assert await get_player_name_by_qq_id("654321") == "Notch"

    await delete_qq_uuid_mapping("654321")
    await delete_mc_player_info("069a79f444e94726a5befca90e38aaf5")

    assert await get_player_name_by_qq_id("654321") is None

    # ---

    await create_qq_uuid_mapping("123456", "069a79f444e94726a5befca90e38aaf5")
    assert await get_player_name_by_qq_id("123456") == "Notch"

    await delete_qq_uuid_mapping("123456")
    await delete_mc_player_info("069a79f444e94726a5befca90e38aaf5")


def test_true():
    assert True
