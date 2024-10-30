from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch


@dataclass
class MockMCServerInfo:
    name: str = "server1"
    game_version: str = "1.16.5"
    game_port: int = 25565
    rcon_port: int = 25575


@dataclass
class MockMCPlayerMessage:
    player: str
    message: str


class MockMCInstance:
    def __init__(
        self,
        name: str = "server1",
        send_command_rcon_response: str = "User banned successfully.",
        list_players_response: list[str] = [],
        get_server_info_response: MockMCServerInfo = MockMCServerInfo(),
        healthy_response: bool = True,
        exists: bool = True,
        created: bool = True,
        running: bool = True,
    ):
        self.name = name

        # Mock methods
        self.send_command_rcon = AsyncMock(return_value=send_command_rcon_response)
        self.list_players = AsyncMock(return_value=list_players_response)
        self.get_server_info = AsyncMock(return_value=get_server_info_response)
        self.healthy = AsyncMock(return_value=healthy_response)
        self.get_name = MagicMock(return_value=self.name)
        self.get_project_path = MagicMock(return_value=Path(f"/mock/path/{self.name}"))
        self.get_compose_manager = MagicMock(return_value=MagicMock())
        self.verify_compose_obj = MagicMock(return_value=True)
        self.get_compose_file_path = AsyncMock(
            return_value=Path(f"/mock/path/{self.name}/docker-compose.yml")
        )
        self.get_compose_obj = AsyncMock(return_value=MagicMock())
        self._get_log_path = MagicMock(
            return_value=Path(f"/mock/path/{self.name}/data/logs/latest.log")
        )
        self.get_log_file_end_pointer = AsyncMock(return_value=100)
        self.get_logs_from_file = AsyncMock(
            return_value={"content": "mock log content", "pointer": 100}
        )
        self.parse_player_messages_from_log = MagicMock(return_value=[])
        self.get_player_messages_from_log = AsyncMock(return_value=([], 100))
        self.get_logs_from_docker = AsyncMock(return_value="mock docker logs")
        self.create = AsyncMock()
        self.update_compose_file = AsyncMock()
        self.remove = AsyncMock()
        self.up = AsyncMock()
        self.down = AsyncMock()
        self.start = AsyncMock()
        self.stop = AsyncMock()
        self.restart = AsyncMock()
        self.exists = AsyncMock(return_value=exists)
        self.created = AsyncMock(return_value=created)
        self.running = AsyncMock(return_value=running)
        self.wait_until_healthy = AsyncMock()


class MockDockerMCManager:
    def __init__(
        self,
        instances: list[MockMCInstance] = [
            MockMCInstance(name="server1"),
            MockMCInstance(name="server2"),
        ],
    ):
        self.instances_dict = {instance.name: instance for instance in instances}

        self.get_running_server_names = AsyncMock(
            side_effect=self._get_running_server_names
        )
        self.get_instance = MagicMock(side_effect=self._get_instance)
        self.get_all_server_names = AsyncMock(
            return_value=list(self.instances_dict.keys())
        )
        self.get_all_instances = AsyncMock(return_value=list(instances))
        self.get_all_server_compose_obj = AsyncMock(return_value=[])
        self.get_all_server_compose_paths = AsyncMock(return_value=[])
        self.get_all_server_info = AsyncMock(return_value=[])
        self.parse_server_name_from_compose_obj = MagicMock(
            side_effect=lambda compose_obj, verify=True: "server1"
        )

    def _get_instance(self, server_name: str) -> MockMCInstance:
        return self.instances_dict.get(server_name, MockMCInstance(name=server_name))

    def _get_running_server_names(self) -> list[str]:
        # accessing return_value to avoid interference with tests
        return [
            name
            for name, instance in self.instances_dict.items()
            if instance.running.return_value
        ]


@contextmanager
def mock_common_docker_mc_manager(mock_manager: MockDockerMCManager):
    with patch(
        "mc_qqbot_next.plugins.mc_qqbot_next.docker.docker_mc_manager",
        new=mock_manager,
    ):
        yield
