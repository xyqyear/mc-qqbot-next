from ..model import MessageTarget
from . import get_session_scope


async def create_message_target(
    message_id: int,
    target_server: str | None = None,
    target_player: str | None = None,
) -> None:
    """
    Create message target
    """
    async with get_session_scope() as session:
        message_target = MessageTarget(
            message_id=message_id,
            target_server=target_server,
            target_player=target_player,
        )
        session.add(message_target)


async def get_message_target_by_message_id(
    message_id: int,
) -> MessageTarget | None:
    """
    Get message target by message id

    becareful, the object return is expunged from session
    """
    async with get_session_scope() as session:
        message_target = await session.get(MessageTarget, message_id)
        session.expunge_all()
        return message_target


# only used in tests currently
async def delete_message_target_by_message_id(
    message_id: int,
) -> None:
    """
    Delete message target by message id
    """
    async with get_session_scope() as session:
        if result := await session.get(MessageTarget, message_id):
            await session.delete(result)
