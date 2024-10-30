from nonebot import on_command
from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.matcher import Matcher
from nonebot.params import Depends

from ...db.crud.message import create_message_target
from ...dependencies import extract_arg_and_target, get_player_name
from ...docker import send_message
from ...rules import is_from_configured_group

say = on_command(
    "say",
    rule=is_from_configured_group,
    aliases={"s"},
)


@say.handle()
async def handle_say(
    event: MessageEvent,
    arg_and_target: tuple[str, str] = Depends(extract_arg_and_target),
    player_name: str | None = Depends(get_player_name),
):
    message, target_server = arg_and_target

    await actual_send_message(
        matcher=say,
        message=message,
        message_id=event.message_id,
        target_server=target_server,
        player_name=player_name,
    )


async def actual_send_message(
    matcher: type[Matcher],
    message: str,
    message_id: int,
    target_server: str,
    player_name: str | None,
):
    """
    发送消息到指定服务器

    Args:
        message (str): 消息内容
        target_server (str): 目标服务器名称

    Returns:
        list[str]: 发送失败的服务器列表
    """
    if player_name is None:
        await say.finish('在任意服务器输入 "\\\\bind QQ号" 来绑定游戏账号')
    sending_message = f"*<{player_name}> {message}"

    await create_message_target(
        message_id=message_id,
        target_server=target_server,
    )

    failed_servers = await send_message(sending_message, target_server)
    if failed_servers:
        await matcher.finish(f"发送失败：{', '.join(failed_servers)}")
