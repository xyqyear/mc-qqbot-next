from nonebot import on_message
from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.params import Depends

from ...dependencies import get_player_name, get_target_server_from_reply
from ...rules import is_from_configured_group
from .say import actual_send_message

reply_say = on_message(
    rule=is_from_configured_group,
    block=False,
)


@reply_say.handle()
async def handle_reply_say(
    event: MessageEvent,
    target_server: str | None = Depends(get_target_server_from_reply),
    player_name: str | None = Depends(get_player_name),
):
    if target_server is None:
        return

    message = event.get_plaintext()
    message_id = event.message_id

    await actual_send_message(
        matcher=reply_say,
        message=message,
        message_id=message_id,
        target_server=target_server,
        player_name=player_name,
    )
