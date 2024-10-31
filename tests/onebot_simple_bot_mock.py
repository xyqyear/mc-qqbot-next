from contextlib import contextmanager
from unittest.mock import AsyncMock, MagicMock, patch


@contextmanager
def mock_server_to_group_bot():
    with patch(
        "mc_qqbot_next.plugins.mc_qqbot_next.server_to_group.get_onebot_bot",
        new=MagicMock(),
    ) as mock_bot:
        mock_bot.send_group_msg = AsyncMock()
        yield mock_bot
