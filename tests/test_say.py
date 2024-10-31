import pytest
from nonebug import App

from .docker_mc_mocks import (
    MockDockerMCManager,
    MockMCInstance,
    mock_common_docker_mc_manager,
)
from .onebot_message_factory import create_group_message_event, create_reply
from .onebot_mock_send import bot_receive_event
from .onebot_simple_bot_mock import mock_server_to_group_bot


@pytest.mark.asyncio
async def test_say(app: App):
    from nonebot_plugin_orm import init_orm

    from mc_qqbot_next.plugins.mc_qqbot_next.commands.mc.say import say
    from mc_qqbot_next.plugins.mc_qqbot_next.db.crud.binding import (
        create_qq_uuid_mapping_by_player_name,
        delete_qq_uuid_mapping,
    )
    from mc_qqbot_next.plugins.mc_qqbot_next.db.crud.message import (
        get_message_target_by_message_id,
    )

    await init_orm()

    mock_manager = MockDockerMCManager(instances=[MockMCInstance(name="server1")])

    with mock_common_docker_mc_manager(mock_manager):
        event = create_group_message_event(
            "/s hello",
            sender_id=123456,
        )
        await bot_receive_event(
            app, say, event, '在任意服务器输入 "\\\\bind QQ号" 来绑定游戏账号'
        )
        mock_instance = mock_manager.instances_dict["server1"]
        mock_instance.send_command_rcon.assert_not_called()

        await create_qq_uuid_mapping_by_player_name("123456", "Notch")

        event = create_group_message_event(
            "/s hello",
            sender_id=123456,
        )
        await bot_receive_event(app, say, event)
        mock_instance.send_command_rcon.assert_called_once_with(
            'tellraw @a {"text": "*<Notch> hello", "color": "yellow"}'
        )
        saved_message_target = await get_message_target_by_message_id(event.message_id)
        assert saved_message_target is not None
        assert saved_message_target.target_server == "server1"
        assert saved_message_target.target_player is None

        mock_instance.healthy_response = False
        event = create_group_message_event(
            "/s hello",
            sender_id=123456,
        )
        await bot_receive_event(app, say, event, "发送失败：server1")

        await delete_qq_uuid_mapping("123456")


@pytest.mark.asyncio
async def test_reply_say(app: App):
    from nonebot_plugin_orm import init_orm

    from mc_qqbot_next.plugins.mc_qqbot_next.commands.mc.reply_say import reply_say
    from mc_qqbot_next.plugins.mc_qqbot_next.commands.mc.say import say
    from mc_qqbot_next.plugins.mc_qqbot_next.db.crud.binding import (
        create_qq_uuid_mapping_by_player_name,
        delete_qq_uuid_mapping,
    )
    from mc_qqbot_next.plugins.mc_qqbot_next.server_to_group import (
        handle_send_command,
    )

    await init_orm()

    await create_qq_uuid_mapping_by_player_name("123456", "Notch")

    # if the message is not a reply, the command should not be executed
    event = create_group_message_event(
        "hello",
        sender_id=123456,
    )
    await bot_receive_event(app, reply_say, event, should_pass_rule=False)

    mock_manager = MockDockerMCManager(
        instances=[MockMCInstance(name="server1"), MockMCInstance(name="server2")]
    )
    with mock_common_docker_mc_manager(mock_manager):
        with mock_server_to_group_bot() as mock_bot:
            # if the replied message isn't in the database, the command should not be executed
            event = create_group_message_event(
                "hello1",
                sender_id=123456,
                reply=create_reply(100000),
            )
            await bot_receive_event(app, reply_say, event)
            mock_manager.instances_dict["server1"].send_command_rcon.assert_not_called()

            # if the replied message is in the database, the command should be executed
            # reply to a message sent from server
            mock_bot.send_group_msg.return_value = {"message_id": 100000}
            await handle_send_command(mock_bot, "server1", "Notch", "hello")
            event = create_group_message_event(
                "hello2",
                sender_id=123456,
                reply=create_reply(100000),
            )
            await bot_receive_event(app, reply_say, event)
            mock_manager.instances_dict[
                "server1"
            ].send_command_rcon.assert_called_once_with(
                'tellraw @a {"text": "*<Notch> hello2", "color": "yellow"}'
            )
            mock_manager.instances_dict["server2"].send_command_rcon.assert_not_called()
            mock_manager.instances_dict["server1"].send_command_rcon.reset_mock()

            # reply to a message sending to server
            event = create_group_message_event(
                "/s hello3 /server2",
                sender_id=123456,
            )
            await bot_receive_event(app, say, event)
            mock_manager.instances_dict[
                "server2"
            ].send_command_rcon.assert_called_once_with(
                'tellraw @a {"text": "*<Notch> hello3", "color": "yellow"}'
            )
            mock_manager.instances_dict["server2"].send_command_rcon.reset_mock()

            event = create_group_message_event(
                "hello4",
                sender_id=123456,
                reply=create_reply(event.message_id),
            )
            await bot_receive_event(app, reply_say, event)
            mock_manager.instances_dict[
                "server2"
            ].send_command_rcon.assert_called_once_with(
                'tellraw @a {"text": "*<Notch> hello4", "color": "yellow"}'
            )
            mock_manager.instances_dict["server2"].send_command_rcon.reset_mock()

            # reply to previous reply
            event = create_group_message_event(
                "hello5",
                sender_id=123456,
                reply=create_reply(event.message_id),
            )
            await bot_receive_event(app, reply_say, event)
            mock_manager.instances_dict[
                "server2"
            ].send_command_rcon.assert_called_once_with(
                'tellraw @a {"text": "*<Notch> hello5", "color": "yellow"}'
            )

    await delete_qq_uuid_mapping("123456")
