import pytest
from nonebug import App

from .docker_mc_mocks import (
    MockDockerMCManager,
    MockMCInstance,
    mock_common_docker_mc_manager,
)
from .onebot_fake_send import bot_should_respond
from .onebot_message_factory import create_group_message_event


@pytest.mark.asyncio
async def test_say_unbound_user(app: App):
    from nonebot_plugin_orm import init_orm

    from mc_qqbot_next.plugins.mc_qqbot_next.commands.mc.say import say
    from mc_qqbot_next.plugins.mc_qqbot_next.db.crud.binding import (
        create_qq_uuid_mapping_by_player_name,
        delete_qq_uuid_mapping,
    )

    await init_orm()

    mock_manager = MockDockerMCManager(instances=[MockMCInstance(name="server1")])

    with mock_common_docker_mc_manager(mock_manager):
        event = create_group_message_event(
            "/s hello",
            sender_id=123456,
        )
        await bot_should_respond(
            app, say, event, '在任意服务器输入 "\\\\bind QQ号" 来绑定游戏账号'
        )

        mock_instance = mock_manager.instances_dict["server1"]
        mock_instance.send_command_rcon.assert_not_called()

        await create_qq_uuid_mapping_by_player_name("123456", "Notch")

        event = create_group_message_event(
            "/s hello",
            sender_id=123456,
        )
        await bot_should_respond(app, say, event)

        mock_instance.send_command_rcon.assert_called_once_with(
            'tellraw @a {"text": "*<Notch> hello", "color": "yellow"}'
        )

        mock_instance.healthy_response = False
        event = create_group_message_event(
            "/s hello",
            sender_id=123456,
        )
        await bot_should_respond(app, say, event, "发送失败：server1")

        await delete_qq_uuid_mapping("123456")
