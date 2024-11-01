import nonebot
import pytest
from nonebot.adapters.onebot.v11 import Adapter as Onebot11Adapter
from nonebot.adapters.onebot.v11 import Bot as Onebot11Bot
from nonebug import App

from .docker_mc_mocks import (
    MockDockerMCManager,
    MockMCInstance,
    mock_common_docker_mc_manager,
)
from .onebot_message_factory import create_group_message_event
from .onebot_mock_send import bot_receive_event


@pytest.mark.asyncio
async def test_extract_arg_and_target(app: App):
    from mc_qqbot_next.plugins.mc_qqbot_next.commands.mc.ban import ban
    from mc_qqbot_next.plugins.mc_qqbot_next.config import config

    config.mc_default_server = "server1"
    config.mc_excluded_servers = ["excluded"]

    send_command_response = "User banned successfully."
    mock_docker_mc_manager = MockDockerMCManager(
        instances=[
            MockMCInstance(
                name="server1",
                send_command_response=send_command_response,
                game_port=25565,
            ),
            MockMCInstance(
                name="server2",
                send_command_response=send_command_response,
                game_port=25566,
            ),
            MockMCInstance(
                name="ser", send_command_response=send_command_response, game_port=25567
            ),
            MockMCInstance(
                name="other",
                send_command_response=send_command_response,
                game_port=25568,
            ),
            MockMCInstance(
                name="excluded",
                send_command_response=send_command_response,
                game_port=25569,
            ),
        ],
    )

    with mock_common_docker_mc_manager(mock_docker_mc_manager):

        async def run_test(message_str, expected_target):
            excepted_player, expected_server = expected_target
            await bot_receive_event(
                app,
                ban,
                create_group_message_event(message_str, role="admin"),
                f"[{expected_server}] {send_command_response}",
            )
            mock_docker_mc_manager.assert_rcon_sent_to_server(
                expected_server, f"ban {excepted_player}"
            )
            mock_docker_mc_manager.reset_mocks()

        # test default server
        await run_test("/ban player", ("player", "server1"))
        # make sure excluded server is not selected
        await run_test("/ban player /o", ("player", "other"))
        await run_test("/ban player /e", ("player", "server1"))

        # test specified server
        await run_test("/ban player /server2", ("player", "server2"))
        await run_test("/ban player /s", ("player", "server1"))
        await run_test("/ban player /ser", ("player", "ser"))


@pytest.mark.asyncio
async def test_extract_arg_and_target_bare_command(app: App):
    from mc_qqbot_next.plugins.mc_qqbot_next.commands.mc.restart import restart
    from mc_qqbot_next.plugins.mc_qqbot_next.config import config

    config.mc_default_server = "server1"
    config.mc_excluded_servers = ["excluded"]

    send_command_response = "Restarting"
    mock_docker_mc_manager = MockDockerMCManager(
        instances=[
            MockMCInstance(
                name="server1",
                send_command_response=send_command_response,
                game_port=25565,
            ),
            MockMCInstance(
                name="server2",
                send_command_response=send_command_response,
                game_port=25566,
            ),
            MockMCInstance(
                name="ser", send_command_response=send_command_response, game_port=25567
            ),
            MockMCInstance(
                name="other",
                send_command_response=send_command_response,
                game_port=25568,
            ),
            MockMCInstance(
                name="excluded",
                send_command_response=send_command_response,
                game_port=25569,
            ),
        ],
    )

    with mock_common_docker_mc_manager(mock_docker_mc_manager):

        async def run_test(message_str, target_server):
            event = create_group_message_event(message_str, role="admin")
            async with app.test_matcher(restart) as ctx:
                adapter = nonebot.get_adapter(Onebot11Adapter)
                bot = ctx.create_bot(base=Onebot11Bot, adapter=adapter)
                ctx.receive_event(bot, event)
                ctx.should_pass_permission(restart)
                ctx.should_pass_rule(restart)
                ctx.should_call_send(event, f"[{target_server}] 正在重启", result=None)
                ctx.should_call_send(event, f"[{target_server}] 重启完成", result=None)
                ctx.should_finished(restart)

            mock_docker_mc_manager.instances_dict[
                target_server
            ].restart.assert_awaited_once()
            mock_docker_mc_manager.reset_mocks()

        # test default server
        await run_test("/restart", "server1")
        # make sure excluded server is not selected
        await run_test("/restart /o", "other")
        await run_test("/restart /e", "server1")

        # test specified server
        await run_test("/restart /server2", "server2")
        await run_test("/restart /s", "server1")
        await run_test("/restart /ser", "ser")


@pytest.mark.asyncio
async def test_extract_arg_and_target_no_default_server(app: App):
    from mc_qqbot_next.plugins.mc_qqbot_next.commands.mc.ban import ban
    from mc_qqbot_next.plugins.mc_qqbot_next.config import config

    config.mc_default_server = None

    send_command_response = "User banned successfully."
    mock_docker_mc_manager = MockDockerMCManager(
        instances=[
            MockMCInstance(
                name="server2",
                send_command_response=send_command_response,
                game_port=25566,
            ),
            MockMCInstance(
                name="server1",
                send_command_response=send_command_response,
                game_port=25565,
            ),
        ],
    )

    with mock_common_docker_mc_manager(mock_docker_mc_manager):

        async def run_test(message_str, expected_target):
            excepted_player, expected_server = expected_target
            await bot_receive_event(
                app,
                ban,
                create_group_message_event(message_str, role="admin"),
                f"[{expected_server}] {send_command_response}",
            )
            mock_docker_mc_manager.assert_rcon_sent_to_server(
                expected_server, f"ban {excepted_player}"
            )
            mock_docker_mc_manager.reset_mocks()

        # test default server
        await run_test("/ban player", ("player", "server1"))
        mock_docker_mc_manager.instances_dict["server1"].running_response = False
        await run_test("/ban player", ("player", "server2"))
        mock_docker_mc_manager.instances_dict["server2"].running_response = False
        await bot_receive_event(
            app,
            ban,
            create_group_message_event("/ban player", role="admin"),
            "没有运行中的服务器",
        )
        mock_docker_mc_manager.assert_rcon_not_sent_to_any_server()
