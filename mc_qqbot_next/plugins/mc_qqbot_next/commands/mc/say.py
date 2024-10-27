"""
from utils.request_utils import uuid2name
from config_manager import config

from nonebot import CommandSession

permissions = ('say', )
commands = ('say', 's')


async def get_command(session: CommandSession, parsed_message, command_say_bindings=None):
    if not command_say_bindings:
        command_say_bindings = config.command_say_bindings

    if session.event.user_id in command_say_bindings:
        sender_uuid = command_say_bindings[session.event.user_id]
        player_name = await uuid2name(sender_uuid)
        escaped_message = parsed_message.args.replace('\\', '\\\\').replace('"', '\\"')

        return f'tellraw @a {{"text": "*<{player_name}> {escaped_message}", "color": "yellow"}}', 'say'
    else:
        return '', 'You have no in-game character bound'


def parse_response(permission, response):
    if response == 'No player was found':
        return 'No player is online'
    else:
        return response
"""

from nonebot import on_command
from nonebot.params import Depends

from ...db.model import QQUUIDMapping
from ...dependencies import extract_arg_and_target, mc_mapping
from ...docker import docker_mc_manager
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
    mapping: QQUUIDMapping | None = Depends(mc_mapping),
):
    message, target_server = arg_and_target
    if not mapping:
        await say.finish('在任意服务器输入 "\\\\bind QQ号" 来绑定游戏账号')
        return
    escaped_message = message.replace("\\", "\\\\").replace('"', '\\"')
    command = f'tellraw @a {{"text": "*<{mapping.player_name}> {escaped_message}", "color": "yellow"}}'
    try:
        await docker_mc_manager.get_instance(target_server).send_command_rcon(command)
    except RuntimeError:
        await say.finish("发送失败")
