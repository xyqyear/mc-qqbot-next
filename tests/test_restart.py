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
async def test_restart(app: App):
    from mc_qqbot_next.plugins.mc_qqbot_next.commands.mc.restart import restart
    from mc_qqbot_next.plugins.mc_qqbot_next.config import config

    await basic_permission_check(app, restart)

    instance = MockMCInstance(name="server1", restart_time=2)
    mock_docker_mc_manager = MockDockerMCManager(
        instances=[instance],
    )

    with mock_common_docker_mc_manager(mock_docker_mc_manager):
        # Test that restart without explicit server fails
        event = create_group_message_event(
            "/restart",
            role="admin",
        )
        config.mc_restart_wait_seconds = 60
        async with app.test_matcher(restart) as ctx:
            adapter = nonebot.get_adapter(Onebot11Adapter)
            bot = ctx.create_bot(base=Onebot11Bot, adapter=adapter)
            ctx.receive_event(bot, event)
            ctx.should_pass_permission(restart)
            ctx.should_pass_rule(restart)
            ctx.should_call_send(event, "重启服务器需要明确指定目标服务器", result=None)
            ctx.should_finished(restart)
        instance.restart.assert_not_called()
        instance.restart.reset_mock()

        # Test that restart with explicit server works
        event = create_group_message_event(
            "/restart /server1",
            role="admin",
        )
        async with app.test_matcher(restart) as ctx:
            adapter = nonebot.get_adapter(Onebot11Adapter)
            bot = ctx.create_bot(base=Onebot11Bot, adapter=adapter)
            ctx.receive_event(bot, event)
            ctx.should_pass_permission(restart)
            ctx.should_pass_rule(restart)
            ctx.should_call_send(event, "[server1] 正在重启", result=None)
            ctx.should_call_send(event, "[server1] 重启完成", result=None)
            ctx.should_finished(restart)
        instance.restart.assert_awaited_once()
        instance.restart.reset_mock()

        # Test timeout scenario with explicit server
        event = create_group_message_event(
            "/restart /server1",
            role="admin",
        )
        config.mc_restart_wait_seconds = 1
        async with app.test_matcher(restart) as ctx:
            adapter = nonebot.get_adapter(Onebot11Adapter)
            bot = ctx.create_bot(base=Onebot11Bot, adapter=adapter)
            ctx.receive_event(bot, event)
            ctx.should_pass_permission(restart)
            ctx.should_pass_rule(restart)
            ctx.should_call_send(event, "[server1] 正在重启", result=None)
            ctx.should_call_send(
                event, "[server1] 坏了，好像过了0分钟了还没重启好", result=None
            )
            ctx.should_finished(restart)

        instance.restart.assert_awaited_once()
