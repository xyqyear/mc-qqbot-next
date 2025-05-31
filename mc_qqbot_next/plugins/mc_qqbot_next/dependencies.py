import re
from dataclasses import dataclass

from nonebot.adapters import Event
from nonebot.adapters.onebot.v11 import Message, MessageEvent
from nonebot.matcher import Matcher
from nonebot.params import CommandArg

from .config import config
from .db.crud.binding import get_player_name_by_qq_id
from .db.crud.message import get_message_target_by_message_id
from .docker import (
    get_running_server_name_with_lowest_port,
    locate_server_name_with_prefix,
)
from .log import logger


@dataclass
class CommandTarget:
    """
    表示命令的参数和目标服务器信息
    
    Attributes:
        arg (str): 命令参数内容
        target_server (str): 目标服务器名称
        is_explicit (bool): 是否显式指定了目标服务器
    """
    arg: str
    target_server: str
    is_explicit: bool


async def extract_content_and_target_from_str(command: str) -> tuple[str, str | None]:
    """
    见 extract_content_and_target
    
    Returns:
        tuple[str, str | None, bool]: (command_content, target_server)
    """
    match = re.search(r"\s*/(\S+)$", command)
    if match:
        command_content = command[: match.start()]
        potential_target = match.group(1)
        target_server = await locate_server_name_with_prefix(potential_target)
        return command_content, target_server
    return command, None


async def extract_arg_and_target(
    matcher: Matcher, msg: Message = CommandArg()
) -> CommandTarget:
    """
    从消息中提取命令内容和目标服务器名称

    Args:
        msg (Message): 输入的消息对象

    Returns:
        CommandTarget: 包含命令参数、目标服务器和是否显式指定的信息

    Examples:
        >>> "hello /s"
        CommandTarget(arg='hello', target_server='s', is_explicit=True)
        >>> "hello"
        CommandTarget(arg='hello', target_server='default_server', is_explicit=False)
        >>> "message /test"
        CommandTarget(arg='message', target_server='test', is_explicit=True)
        >>> "/hello /test"
        CommandTarget(arg='/hello', target_server='test', is_explicit=True)
    """
    text = msg.extract_plain_text()
    command_content, target_server = await extract_content_and_target_from_str(text)
    is_explicit = target_server is not None
    
    if target_server is None:
        if config.mc_default_server is None:
            logger.info(
                "No default server specified, trying to get the first running server"
            )
            first_running_server = await get_running_server_name_with_lowest_port()
            if first_running_server is None:
                await matcher.finish("没有运行中的服务器")
            target_server = first_running_server
        else:
            target_server = config.mc_default_server
    
    return CommandTarget(
        arg=command_content,
        target_server=target_server,
        is_explicit=is_explicit
    )


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
