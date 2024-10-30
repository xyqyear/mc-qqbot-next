import pytest
from nonebug import App

from .docker_mc_mocks import (
    MockDockerMCManager,
    MockMCInstance,
    mock_common_docker_mc_manager,
)
from .onebot_message_factory import Message


@pytest.mark.asyncio
async def test_ban_command(app: App):
    from mc_qqbot_next.plugins.mc_qqbot_next.dependencies import extract_arg_and_target

    mock_manager = MockDockerMCManager(
        instances=[
            MockMCInstance(
                name="server1", send_command_rcon_response="User banned successfully."
            ),
            MockMCInstance(
                name="server2", send_command_rcon_response="User banned successfully."
            ),
            MockMCInstance(
                name="ser", send_command_rcon_response="User banned successfully."
            ),
            MockMCInstance(
                name="excluded", send_command_rcon_response="User banned successfully."
            ),
        ],
    )

    with mock_common_docker_mc_manager(mock_manager):

        async def run_test(message_str, expected_target):
            arg_and_target = await extract_arg_and_target(Message(message_str))
            assert arg_and_target == expected_target

        # test default server
        await run_test("message", ("message", "server1"))
        # make sure excluded server is not selected
        await run_test("message /e", ("message", "server1"))

        # test specified server
        await run_test("message /server2", ("message", "server2"))
        await run_test("message /s", ("message", "server1"))
        await run_test("message /ser", ("message", "ser"))
