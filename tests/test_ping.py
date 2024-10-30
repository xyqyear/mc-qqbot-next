import pytest
from nonebug import App

from .docker_mc_mocks import (
    MockDockerMCManager,
    MockMCInstance,
    MockMCServerInfo,
    mock_common_docker_mc_manager,
)
from .onebot_fake_send import bot_should_respond
from .onebot_message_factory import create_group_message_event


@pytest.mark.asyncio
async def test_say_unbound_user(app: App):
    from nonebot_plugin_orm import init_orm

    from mc_qqbot_next.plugins.mc_qqbot_next.commands.mc.ping import ping

    await init_orm()

    mock_manager = MockDockerMCManager(
        instances=[
            MockMCInstance(
                name="server1",
                get_server_info_response=MockMCServerInfo(
                    game_port=25566,
                ),
            ),
            MockMCInstance(
                name="server2",
                get_server_info_response=MockMCServerInfo(
                    game_port=25565,
                ),
            ),
            MockMCInstance(
                name="server3",
                get_server_info_response=MockMCServerInfo(
                    game_port=25567,
                ),
            ),
        ]
    )
    with mock_common_docker_mc_manager(mock_manager):
        event = create_group_message_event(
            "/list",
            message_id=1,
            sender_id=123456,
        )
        await bot_should_respond(
            app, ping, event, "没人: [server2], [server1], [server3]"
        )

        for instance in mock_manager.instances_dict.values():
            instance.list_players.assert_awaited_once()

        mock_manager.instances_dict["server1"].list_players_response = [
            "player1",
            "player2",
        ]
        mock_manager.instances_dict["server2"].list_players_response = ["player3"]
        mock_manager.instances_dict["server3"].healthy_response = False

        await bot_should_respond(
            app,
            ping,
            event,
            "[server2]: player3\n[server1]: player1, player2\n无响应: [server3]",
        )
