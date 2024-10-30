import nonebot
from nonebot.adapters import Event
from nonebot.adapters.onebot.v11 import Adapter as Onebot11Adapter
from nonebot.adapters.onebot.v11 import Bot as Onebot11Bot
from nonebot.matcher import Matcher
from nonebug import App


async def bot_should_respond(
    app: App, matcher: type[Matcher], event: Event, mock_response: str | None = None
):
    async with app.test_matcher(matcher) as ctx:
        adapter = nonebot.get_adapter(Onebot11Adapter)
        bot = ctx.create_bot(base=Onebot11Bot, adapter=adapter)
        ctx.receive_event(bot, event)
        ctx.should_pass_permission(matcher)
        ctx.should_pass_rule(matcher)
        if mock_response:
            ctx.should_call_send(event, mock_response, result=None)
            ctx.should_finished(matcher)
