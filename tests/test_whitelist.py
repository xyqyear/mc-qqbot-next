import nonebot
import pytest
from nonebot.adapters.onebot.v11 import Adapter as Onebot11Adapter
from nonebot.adapters.onebot.v11 import Bot as Onebot11Bot
from nonebug import App

from .common_permission_test import basic_permission_check
from .docker_mc_mocks import (
    MockDockerMCManager,
    MockMCInstance,
    mock_common_docker_mc_manager,
)
from .onebot_message_factory import create_group_message_event


@pytest.mark.asyncio
async def test_whitelist_add_command(app: App):
    from mc_qqbot_next.plugins.mc_qqbot_next.commands.mc.whitelist import whitelist_add
    from mc_qqbot_next.plugins.mc_qqbot_next.config import config

    await basic_permission_check(app, whitelist_add)

    mock_response = "Player added to whitelist."
    mock_manager = MockDockerMCManager(
        instances=[
            MockMCInstance(name="server1", send_command_rcon_response=mock_response),
        ]
    )

    with mock_common_docker_mc_manager(mock_manager):
        event = create_group_message_event(
            "/whitelist add user123 /server1",
            sender_id=123456,
            group_id=config.group_id,
            role="admin",
        )

        async with app.test_matcher(whitelist_add) as ctx:
            adapter = nonebot.get_adapter(Onebot11Adapter)
            bot = ctx.create_bot(base=Onebot11Bot, adapter=adapter)
            ctx.receive_event(bot, event)
            ctx.should_pass_permission(whitelist_add)
            ctx.should_pass_rule(whitelist_add)
            ctx.should_call_send(event, mock_response, result=None)
            ctx.should_finished(whitelist_add)

        mock_instance = mock_manager.instances_dict["server1"]
        mock_instance.send_command_rcon.assert_awaited_once_with(
            "whitelist add user123"
        )


@pytest.mark.asyncio
async def test_whitelist_remove_command(app: App):
    from mc_qqbot_next.plugins.mc_qqbot_next.commands.mc.whitelist import (
        whitelist_remove,
    )
    from mc_qqbot_next.plugins.mc_qqbot_next.config import config

    await basic_permission_check(app, whitelist_remove)

    mock_response = "Player removed from whitelist."
    mock_manager = MockDockerMCManager(
        instances=[
            MockMCInstance(name="server1", send_command_rcon_response=mock_response),
        ]
    )

    with mock_common_docker_mc_manager(mock_manager):
        event = create_group_message_event(
            "/whitelist remove user123 /server1",
            sender_id=123456,
            group_id=config.group_id,
            role="admin",
        )

        async with app.test_matcher(whitelist_remove) as ctx:
            adapter = nonebot.get_adapter(Onebot11Adapter)
            bot = ctx.create_bot(base=Onebot11Bot, adapter=adapter)
            ctx.receive_event(bot, event)
            ctx.should_pass_permission(whitelist_remove)
            ctx.should_pass_rule(whitelist_remove)
            ctx.should_call_send(event, mock_response, result=None)
            ctx.should_finished(whitelist_remove)

        mock_instance = mock_manager.instances_dict["server1"]
        mock_instance.send_command_rcon.assert_awaited_once_with(
            "whitelist remove user123"
        )


@pytest.mark.asyncio
async def test_whitelist_list_command(app: App):
    from mc_qqbot_next.plugins.mc_qqbot_next.commands.mc.whitelist import whitelist_list

    mock_response = "Whitelist:\n- user123\n- user456"
    mock_manager = MockDockerMCManager(
        instances=[
            MockMCInstance(name="server1", send_command_rcon_response=mock_response),
        ]
    )

    with mock_common_docker_mc_manager(mock_manager):
        event = create_group_message_event(
            "/whitelist list /server1",
            sender_id=123456,
            group_id=1001,
            role="admin",
        )

        async with app.test_matcher(whitelist_list) as ctx:
            adapter = nonebot.get_adapter(Onebot11Adapter)
            bot = ctx.create_bot(base=Onebot11Bot, adapter=adapter)
            ctx.receive_event(bot, event)
            ctx.should_pass_permission(whitelist_list)
            ctx.should_pass_rule(whitelist_list)
            ctx.should_call_send(event, mock_response, result=None)
            ctx.should_finished(whitelist_list)

        mock_instance = mock_manager.instances_dict["server1"]
        mock_instance.send_command_rcon.assert_awaited_once_with("whitelist list")
