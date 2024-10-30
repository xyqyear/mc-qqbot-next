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
async def test_unban_command(app: App):
    from mc_qqbot_next.plugins.mc_qqbot_next.commands.mc.unban import unban
    from mc_qqbot_next.plugins.mc_qqbot_next.config import config

    await basic_permission_check(app, unban)

    mock_response = "User unbanned successfully."
    mock_manager = MockDockerMCManager(
        instances=[
            MockMCInstance(name="server1", send_command_rcon_response=mock_response),
        ]
    )

    with mock_common_docker_mc_manager(mock_manager):
        event = create_group_message_event(
            "/unban user123 /server1",
            sender_id=123456,
            group_id=config.group_id,
            role="admin",
        )

        async with app.test_matcher(unban) as ctx:
            adapter = nonebot.get_adapter(Onebot11Adapter)
            bot = ctx.create_bot(base=Onebot11Bot, adapter=adapter)
            ctx.receive_event(bot, event)
            ctx.should_pass_permission(unban)
            ctx.should_pass_rule(unban)
            ctx.should_call_send(event, mock_response, result=None)
            ctx.should_finished(unban)

        mock_instance = mock_manager.instances_dict["server1"]
        mock_instance.send_command_rcon.assert_awaited_once_with("pardon user123")
