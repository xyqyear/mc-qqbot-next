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


@pytest.mark.asyncio
async def test_banlist_command(app: App):
    from mc_qqbot_next.plugins.mc_qqbot_next.commands.mc.banlist import banlist

    response = "Banned users:\n- user123\n- user456"
    mock_manager = MockDockerMCManager(
        instances=[
            MockMCInstance(
                name="server1",
                send_command_rcon_response=response,
            )
        ]
    )

    with mock_common_docker_mc_manager(mock_manager):
        event = create_group_message_event(
            "/banlist /server1",
            sender_id=123456,
            group_id=1001,
        )

        async with app.test_matcher(banlist) as ctx:
            adapter = nonebot.get_adapter(Onebot11Adapter)
            bot = ctx.create_bot(base=Onebot11Bot, adapter=adapter)
            ctx.receive_event(bot, event)
            ctx.should_pass_permission(banlist)
            ctx.should_pass_rule(banlist)
            ctx.should_call_send(event, response, result=None)
            ctx.should_finished(banlist)

        mock_instance = mock_manager.instances_dict["server1"]
        mock_instance.send_command_rcon.assert_awaited_once_with("banlist")
