import re

from nonebot.adapters import Event, Message
from nonebot.params import CommandArg, Depends, EventMessage
from nonebot_plugin_orm import async_scoped_session

from .config import config
from .db.crud import get_player_name_by_qq_id


def extract_content_and_target_from_str(command: str) -> tuple[str, str | None]:
    """
    见 extract_content_and_target
    """
    match = re.search(r"\s+/(\S+)$", command)
    if match:
        command_content = command[: match.start()].rstrip()
        return command_content, match.group(1)
    return command, None


async def extract_arg_and_target(msg: Message = CommandArg()) -> tuple[str, str]:
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
    command_content, target_server = extract_content_and_target_from_str(text)
    return command_content, (target_server if target_server else config.default_server)


async def get_player_name(
    db_session: async_scoped_session, event: Event = Depends(EventMessage)
) -> str | None:
    """
    从事件中提取发送者的QQ号，并返回对应的玩家名

    Args:
        session (async_scoped_session): 数据库会话
        event (Event): 事件对象

    Returns:
        str | None: 玩家名
    """
    sender_qq_id = event.get_user_id()
    return await get_player_name_by_qq_id(db_session, sender_qq_id)
