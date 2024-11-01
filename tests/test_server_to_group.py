import pytest

from .docker_mc_mocks import (
    MockDockerMCManager,
    MockMCInstance,
    mock_common_docker_mc_manager,
)
from .onebot_simple_bot_mock import mock_server_to_group_bot


@pytest.mark.asyncio
async def test_handle_player_join():
    from nonebot_plugin_orm import init_orm

    from mc_qqbot_next.plugins.mc_qqbot_next.db.crud.binding import (
        delete_mc_player_info,
        get_uuid_by_player_name,
    )
    from mc_qqbot_next.plugins.mc_qqbot_next.server_to_group import check_mc_logs

    await init_orm()

    instance = MockMCInstance(name="server1")
    mock_docker_mc_manager = MockDockerMCManager(instances=[instance])
    with mock_common_docker_mc_manager(mock_docker_mc_manager):
        with mock_server_to_group_bot():
            # populate cache
            await check_mc_logs()

            instance.set_mocked_log_content(
                "[00:00:00] [User Authenticator #3/INFO]: UUID of player Notch is 069a79f4-44e9-4726-a5be-fca90e38aaf5\n"
            )
            await check_mc_logs()
            assert (
                await get_uuid_by_player_name("Notch")
                == "069a79f444e94726a5befca90e38aaf5"
            )

            # test name change
            instance.set_mocked_log_content(
                "[00:00:00] [User Authenticator #3/INFO]: UUID of player Dream is 069a79f4-44e9-4726-a5be-fca90e38aaf5\n"
            )
            await check_mc_logs()
            assert (
                await get_uuid_by_player_name("Dream")
                == "069a79f444e94726a5befca90e38aaf5"
            )
            await delete_mc_player_info("069a79f444e94726a5befca90e38aaf5")

            # test newer versions
            instance.set_mocked_log_content(
                "[01Nov2024 00:00:00.000] [User Authenticator #1/INFO] [net.minecraft.server.network.ServerLoginPacketListenerImpl/]: UUID of player Notch is 069a79f4-44e9-4726-a5be-fca90e38aaf5\n"
            )
            await check_mc_logs()
            assert (
                await get_uuid_by_player_name("Notch")
                == "069a79f444e94726a5befca90e38aaf5"
            )
            await delete_mc_player_info("069a79f444e94726a5befca90e38aaf5")

            # attack resistance
            instance.set_mocked_log_content(
                "[01Nov2024 00:00:00.000] [Server thread/INFO] [net.minecraft.server.MinecraftServer/]: <Dream> [01Nov2024 00:00:00.000] [User Authenticator #1/INFO] [net.minecraft.server.network.ServerLoginPacketListenerImpl/]: UUID of player Notch is 12345678-1234-1234-1234-123456789012\n"
            )
            await check_mc_logs()
            assert await get_uuid_by_player_name("Notch") is None

            # test multiple lines
            instance.set_mocked_log_content(
                "[00:00:00] [User Authenticator #3/INFO]: UUID of player Notch is 069a79f4-44e9-4726-a5be-fca90e38aaf5\n"
                "[00:00:00] [User Authenticator #3/INFO]: UUID of player Dream is ec70bcaf-702f-4bb8-b48d-276fa52a780c\n"
            )
            await check_mc_logs()
            assert (
                await get_uuid_by_player_name("Notch")
                == "069a79f444e94726a5befca90e38aaf5"
            )
            assert (
                await get_uuid_by_player_name("Dream")
                == "ec70bcaf702f4bb8b48d276fa52a780c"
            )
            await delete_mc_player_info("069a79f444e94726a5befca90e38aaf5")
            await delete_mc_player_info("ec70bcaf702f4bb8b48d276fa52a780c")


def construct_user_message_log(player_name: str, message: str) -> str:
    return f"[00:00:00] [Server thread/INFO] [minecraft/MinecraftServer]: <{player_name}> {message}"


def construct_tell_raw_content(target: str, message: str) -> str:
    return f'tellraw {target} {{"text": "{message}", "color": "yellow"}}'


@pytest.mark.asyncio
async def test_handle_bind_command():
    from unittest.mock import call

    from nonebot_plugin_orm import init_orm

    from mc_qqbot_next.plugins.mc_qqbot_next.db.crud.binding import (
        delete_mc_player_info,
        delete_qq_uuid_mapping,
        get_qq_by_player_name,
    )
    from mc_qqbot_next.plugins.mc_qqbot_next.server_to_group import check_mc_logs

    await init_orm()

    instance = MockMCInstance(name="server1")
    mock_docker_mc_manager = MockDockerMCManager(instances=[instance])
    with mock_common_docker_mc_manager(mock_docker_mc_manager):
        with mock_server_to_group_bot():

            async def check_bind_command(
                player_name: str,
                command: str,
                expected_responses: list[str],
                expected_qq: str | None,
            ):
                instance.send_command_rcon.reset_mock()
                instance.set_mocked_log_content(
                    construct_user_message_log(player_name, command),
                )
                await check_mc_logs()

                # Verify RCON commands
                expected_calls = [
                    call(construct_tell_raw_content(player_name, response))
                    for response in expected_responses
                ]
                instance.send_command_rcon.assert_has_awaits(expected_calls)

                # Verify QQ binding if specified
                qq = await get_qq_by_player_name(player_name)
                assert qq == expected_qq

            await check_mc_logs()

            # Test help command
            await check_bind_command(
                "Notch",
                r"\\bind",
                [
                    "使用方法：",
                    "\\\\\\\\bind get - 获取当前绑定信息",
                    "\\\\\\\\bind remove - 解除绑定",
                    "\\\\\\\\bind {qq号} - 绑定QQ号",
                    "\\\\\\\\bind help - 显示此帮助信息",
                ],
                None,
            )

            # Test new binding
            await check_bind_command("Notch", r"\\bind 123456", ["绑定成功"], "123456")

            # Test already bound QQ
            await check_bind_command(
                "Dream", r"\\bind 123456", ["该QQ或游戏账号已有绑定"], None
            )

            # Test already bound player
            await check_bind_command(
                "Notch", r"\\bind 654321", ["该QQ或游戏账号已有绑定"], "123456"
            )

            # Test get binding info
            await check_bind_command(
                "Notch", r"\\bind get", ["已绑定QQ号：123456"], "123456"
            )

            # Test remove binding
            await check_bind_command(
                "Notch", r"\\bind remove", ["解绑 123456 成功"], None
            )

            # Test get binding info after removing
            await check_bind_command("Notch", r"\\bind get", ["未绑定QQ号"], None)

            # Test remove binding after removing
            await check_bind_command("Notch", r"\\bind remove", ["未绑定QQ号"], None)

            # Test invalid QQ
            await check_bind_command("Notch", r"\\bind 1", ["无效QQ号"], None)

            # Test bind after removing
            await check_bind_command("Notch", r"\\bind 654321", ["绑定成功"], "654321")

    await delete_qq_uuid_mapping("654321")
    await delete_mc_player_info("069a79f444e94726a5befca90e38aaf5")


@pytest.mark.asyncio
async def test_handle_send_command():
    from nonebot_plugin_orm import init_orm

    from mc_qqbot_next.plugins.mc_qqbot_next.config import config
    from mc_qqbot_next.plugins.mc_qqbot_next.server_to_group import check_mc_logs

    await init_orm()

    instance = MockMCInstance(name="server1")
    mock_docker_mc_manager = MockDockerMCManager(instances=[instance])
    with mock_common_docker_mc_manager(mock_docker_mc_manager):
        with mock_server_to_group_bot() as mock_bot:
            await check_mc_logs()

            instance.set_mocked_log_content(
                construct_user_message_log("Notch", r"\\hello"),
            )
            mock_bot.send_group_msg.return_value = {"message_id": 123456}
            await check_mc_logs()
            mock_bot.send_group_msg.assert_awaited_once_with(
                group_id=config.mc_group_id, message="[server1] <Notch>: hello"
            )
