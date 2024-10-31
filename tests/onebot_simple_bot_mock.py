from contextlib import contextmanager
from unittest.mock import AsyncMock, patch


class MockBot:
    def __init__(self):
        self.send_group_msg = AsyncMock()


@contextmanager
def mock_server_to_group_bot():
    mock_bot = MockBot()
    with patch(
        "mc_qqbot_next.plugins.mc_qqbot_next.server_to_group.get_onebot_bot",
        return_value=mock_bot,
    ):
        yield mock_bot
