import nonebot
from nonebot.adapters import Event
from nonebot.adapters.onebot.v11 import Adapter as Onebot11Adapter
from nonebot.adapters.onebot.v11 import Bot as Onebot11Bot
from nonebot.adapters.onebot.v11.message import MessageSegment
from nonebot.matcher import Matcher
from nonebug import App


async def bot_receive_event(
    app: App,
    matcher: type[Matcher],
    event: Event,
    mock_response: str | None = None,
    should_pass_permission: bool = True,
    should_pass_rule: bool = True,
    respond_in_forward_message: bool = False,
):
    async with app.test_matcher(matcher) as ctx:
        adapter = nonebot.get_adapter(Onebot11Adapter)
        bot = ctx.create_bot(base=Onebot11Bot, adapter=adapter, self_id="111111")
        ctx.receive_event(bot, event)
        if should_pass_permission:
            ctx.should_pass_permission(matcher)
        else:
            ctx.should_not_pass_permission(matcher)
        if should_pass_rule:
            ctx.should_pass_rule(matcher)
        else:
            ctx.should_not_pass_rule(matcher)
        if mock_response:
            if respond_in_forward_message:
                ctx.should_call_send(
                    event,
                    MessageSegment.node_custom(
                        user_id=int(bot.self_id), nickname="", content=mock_response
                    ),
                    result=None,
                )
            else:
                ctx.should_call_send(event, mock_response, result=None)
            ctx.should_finished(matcher)
