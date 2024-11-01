import re

from nonebot.adapters import Event
from nonebot.adapters.onebot.v11 import Message, MessageEvent
from nonebot.matcher import Matcher
from nonebot.params import CommandArg

from .config import config
from .db.crud.binding import get_player_name_by_qq_id
from .db.crud.message import get_message_target_by_message_id
from .docker import get_first_running_server_name, locate_server_name_with_prefix


async def extract_content_and_target_from_str(command: str) -> tuple[str, str | None]:
    """
    见 extract_content_and_target
    """
    match = re.search(r"\s+/(\S+)$", command)
    if match:
        command_content = command[: match.start()].rstrip()
        potential_target = match.group(1)
        target_server = await locate_server_name_with_prefix(potential_target)
        return command_content, target_server
    return command, None


async def extract_arg_and_target(
    matcher: Matcher, msg: Message = CommandArg()
) -> tuple[str, str]:
    """
    从消息中提取命令内容和目标服务器名称

    Args:
        msg (Message): 输入的消息对象

    Returns:
        tuple[str, str]:
            - 第一个元素是去除目标服务器后缀的命令内容
            - 第二个元素是目标服务器名称（如果没有指定则使用默认服务器）

    Examples:
        >>> "hello /s"
        ('hello', 's')
        >>> "hello"
        ('hello', 'default_server')
        >>> "message /test"
        ('message', 'test')
        >>> "/hello /test"
        ('/hello', 'test')
    """
    text = msg.extract_plain_text()
    command_content, target_server = await extract_content_and_target_from_str(text)
    if target_server is None:
        if config.mc_default_server is None:
            first_running_server = await get_first_running_server_name()
            if first_running_server is None:
                await matcher.finish("没有运行中的服务器")
            target_server = first_running_server
        else:
            target_server = config.mc_default_server
    return command_content, target_server


async def get_player_name(event: Event) -> str | None:
    """
    从事件中提取发送者的QQ号，并返回对应的玩家名

    Args:
        session (async_scoped_session): 数据库会话
        event (Event): 事件对象

    Returns:
        str | None: 玩家名
    """
    sender_qq_id = event.get_user_id()
    return await get_player_name_by_qq_id(sender_qq_id)


async def get_target_server_from_reply(event: MessageEvent, matcher: Matcher) -> str:
    """
    从回复消息中提取目标服务器名称

    Args:
        event (MessageEvent): 回复消息事件对象

    Returns:
        str: 目标服务器名称
    """
    reply = event.reply
    if reply is None:
        matcher.skip()

    reply_message_id = reply.message_id
    message_target = await get_message_target_by_message_id(reply_message_id)
    if message_target is None:
        matcher.skip()

    if message_target.target_server is None:
        matcher.skip()

    return message_target.target_server
