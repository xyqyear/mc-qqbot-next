from nonebot import on_command
from nonebot.params import Depends

from ...dependencies import extract_arg_and_target, get_player_name
from ...docker import send_message
from ...rules import is_from_configured_group

say = on_command(
    "say",
    rule=is_from_configured_group,
    aliases={"s"},
)


# TODO 通过回复消息确定服务器
@say.handle()
async def handle_say(
    arg_and_target: tuple[str, str] = Depends(extract_arg_and_target),
    player_name: str | None = Depends(get_player_name),
):
    message, target_server = arg_and_target
    if player_name is None:
        await say.finish('在任意服务器输入 "\\\\bind QQ号" 来绑定游戏账号')
        return
    sending_message = f"*<{player_name}> {message}"
    failed_servers = await send_message(sending_message, target_server)
    if failed_servers:
        await say.finish(f"发送失败：{', '.join(failed_servers)}")
