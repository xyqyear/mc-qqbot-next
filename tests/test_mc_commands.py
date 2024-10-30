from dataclasses import dataclass
from typing import Literal

import nonebot
import pytest
from nonebot.adapters.onebot.v11 import Adapter as Onebot11Adapter
from nonebot.adapters.onebot.v11 import Bot as Onebot11Bot
from nonebot.matcher import Matcher
from nonebug import App

from .docker_mc_mocks import (
    MockDockerMCManager,
    MockMCInstance,
    mock_common_docker_mc_manager,
)
from .onebot_message_factory import create_group_message_event


@dataclass
class CommandTestCase:
    command: str  # The command string to test (e.g. "/ban user123 /server1")
    mc_command: str  # The expected Minecraft command (e.g. "ban user123")
    mock_response: str  # The mock response from the server
    matcher: type[Matcher]  # The command matcher to test
    requires_permission_check: bool = True
    group_id: int = 321
    role: Literal["owner", "admin", "member"] = "admin"


async def run_command_test(app: App, test_case: CommandTestCase):
    """Common test function for Minecraft command tests"""

    if test_case.requires_permission_check:
        from .common_permission_test import basic_permission_check

        await basic_permission_check(app, test_case.matcher)

    mock_manager = MockDockerMCManager(
        instances=[
            MockMCInstance(
                name="server1", send_command_rcon_response=test_case.mock_response
            )
        ]
    )

    with mock_common_docker_mc_manager(mock_manager):
        event = create_group_message_event(
            test_case.command,
            sender_id=123456,
            group_id=test_case.group_id,
            role=test_case.role,
        )

        async with app.test_matcher(test_case.matcher) as ctx:
            adapter = nonebot.get_adapter(Onebot11Adapter)
            bot = ctx.create_bot(base=Onebot11Bot, adapter=adapter)
            ctx.receive_event(bot, event)
            ctx.should_pass_permission(test_case.matcher)
            ctx.should_pass_rule(test_case.matcher)
            ctx.should_call_send(event, test_case.mock_response, result=None)
            ctx.should_finished(test_case.matcher)

        mock_instance = mock_manager.instances_dict["server1"]
        mock_instance.send_command_rcon.assert_awaited_once_with(test_case.mc_command)


@pytest.mark.asyncio
async def test_ban_command(app: App):
    from mc_qqbot_next.plugins.mc_qqbot_next.commands.mc.ban import ban

    await run_command_test(
        app,
        CommandTestCase(
            command="/ban user123 /server1",
            mc_command="ban user123",
            mock_response="User banned successfully.",
            matcher=ban,
        ),
    )


@pytest.mark.asyncio
async def test_unban_command(app: App):
    from mc_qqbot_next.plugins.mc_qqbot_next.commands.mc.unban import unban

    await run_command_test(
        app,
        CommandTestCase(
            command="/unban user123 /server1",
            mc_command="pardon user123",
            mock_response="User unbanned successfully.",
            matcher=unban,
        ),
    )


@pytest.mark.asyncio
async def test_banlist_command(app: App):
    from mc_qqbot_next.plugins.mc_qqbot_next.commands.mc.banlist import banlist

    await run_command_test(
        app,
        CommandTestCase(
            command="/banlist /server1",
            mc_command="banlist",
            mock_response="Banned users:\n- user123\n- user456",
            matcher=banlist,
            requires_permission_check=False,
        ),
    )


@pytest.mark.asyncio
async def test_whitelist_commands(app: App):
    from mc_qqbot_next.plugins.mc_qqbot_next.commands.mc.whitelist import (
        whitelist_add,
        whitelist_list,
        whitelist_remove,
    )

    # Test whitelist add
    await run_command_test(
        app,
        CommandTestCase(
            command="/whitelist add user123 /server1",
            mc_command="whitelist add user123",
            mock_response="Player added to whitelist.",
            matcher=whitelist_add,
        ),
    )

    # Test whitelist remove
    await run_command_test(
        app,
        CommandTestCase(
            command="/whitelist remove user123 /server1",
            mc_command="whitelist remove user123",
            mock_response="Player removed from whitelist.",
            matcher=whitelist_remove,
        ),
    )

    # Test whitelist list
    await run_command_test(
        app,
        CommandTestCase(
            command="/whitelist list /server1",
            mc_command="whitelist list",
            mock_response="Whitelist:\n- user123\n- user456",
            matcher=whitelist_list,
        ),
    )
