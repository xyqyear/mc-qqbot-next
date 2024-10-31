import nonebot
from nonebot.adapters.onebot.v11 import Adapter as Onebot11Adapter
from nonebot.adapters.onebot.v11 import Bot as Onebot11Bot
from nonebot.matcher import Matcher
from nonebug import App

from .onebot_message_factory import create_group_message_event
from .onebot_mock_send import bot_receive_event
from .onebot_utils import get_one_superuser


async def basic_permission_check(app: App, matcher: type[Matcher]):
    from mc_qqbot_next.plugins.mc_qqbot_next.config import config

    # test rule fail
    event = create_group_message_event(
        "/ban user123 /server1",
        sender_id=int(get_one_superuser()),
        group_id=123456,
    )
    await bot_receive_event(
        app, matcher, event, should_pass_permission=True, should_pass_rule=False
    )

    # admin should pass
    event = create_group_message_event(
        "/ban user123 /server1",
        sender_id=123456,
        group_id=123456,
        role="admin",
    )
    await bot_receive_event(
        app, matcher, event, should_pass_permission=True, should_pass_rule=False
    )

    # test permission fail
    event = create_group_message_event(
        "/ban user123 /server1",
        sender_id=123456,
        group_id=config.group_id,
    )
    async with app.test_matcher(matcher) as ctx:
        adapter = nonebot.get_adapter(Onebot11Adapter)
        bot = ctx.create_bot(base=Onebot11Bot, adapter=adapter)
        ctx.receive_event(bot, event)
        ctx.should_not_pass_permission(matcher)
        # rule checks happens after permission checks, so no need to check rule here
