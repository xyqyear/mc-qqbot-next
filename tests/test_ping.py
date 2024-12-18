import asyncio

import pytest
from nonebug import App

from .docker_mc_mocks import (
    MockDockerMCManager,
    MockMCInstance,
    mock_common_docker_mc_manager,
)
from .onebot_message_factory import create_group_message_event
from .onebot_mock_send import bot_receive_event


@pytest.mark.asyncio
async def test_ping(app: App):
    from nonebot_plugin_orm import init_orm

    from mc_qqbot_next.plugins.mc_qqbot_next.commands.mc.ping import ping
    from mc_qqbot_next.plugins.mc_qqbot_next.config import config

    await init_orm()

    mock_docker_mc_manager = MockDockerMCManager(
        instances=[
            MockMCInstance(
                name="server1",
                game_port=25566,
            ),
            MockMCInstance(
                name="server2",
                game_port=25565,
            ),
            MockMCInstance(
                name="server3",
                game_port=25567,
            ),
        ]
    )
    with mock_common_docker_mc_manager(mock_docker_mc_manager):
        event = create_group_message_event(
            "/list",
            message_id=1,
            sender_id=123456,
        )
        await bot_receive_event(
            app, ping, event, "没人: [server2], [server1], [server3]"
        )

        for instance in mock_docker_mc_manager.instances_dict.values():
            instance.list_players.assert_awaited_once()

        mock_docker_mc_manager.instances_dict["server1"].list_players_response = [
            "player1",
            "player2",
        ]
        mock_docker_mc_manager.instances_dict["server2"].list_players_response = [
            "player3"
        ]
        mock_docker_mc_manager.instances_dict["server3"].healthy_response = False

        await bot_receive_event(
            app,
            ping,
            event,
            "[server2]: player3\n[server1]: player1, player2\n无响应: [server3]",
        )

        # test timeout and error

        async def mock_list_players1(*args, **kwargs):
            raise RuntimeError("Error")

        mock_docker_mc_manager.instances_dict[
            "server1"
        ].list_players.side_effect = mock_list_players1

        await bot_receive_event(
            app,
            ping,
            event,
            "[server2]: player3\n无响应: [server1], [server3]",
        )

        async def mock_list_players2(*args, **kwargs):
            await asyncio.sleep(2)

        config.mc_list_players_timeout_seconds = 1
        mock_docker_mc_manager.instances_dict[
            "server1"
        ].list_players.side_effect = mock_docker_mc_manager.instances_dict[
            "server1"
        ]._list_players
        mock_docker_mc_manager.instances_dict[
            "server2"
        ].list_players.side_effect = mock_list_players2

        await bot_receive_event(
            app,
            ping,
            event,
            "[server1]: player1, player2\n无响应: [server2], [server3]",
        )
