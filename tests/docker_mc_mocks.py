from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from minecraft_docker_manager_lib.instance import LogType


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
        send_command_response: str = "User banned successfully.",
        list_players_response: list[str] = [],
        get_server_info_response: MockMCServerInfo = MockMCServerInfo(),
        mocked_log_content: str = "mock log content",
        healthy_response: bool = True,
        exists_response: bool = True,
        created_response: bool = True,
        running_response: bool = True,
    ):
        self.name = name
        get_server_info_response.name = name
        self.mocked_log_content = mocked_log_content
        self.pointer = 0

        self.send_command_response = send_command_response

        self.healthy_response = healthy_response
        self.exists_response = exists_response
        self.created_response = created_response
        self.running_response = running_response
        self.list_players_response = list_players_response

        # Mock methods
        self.send_command_rcon = AsyncMock(side_effect=self._send_command)
        self.list_players = AsyncMock(side_effect=self._list_players)
        self.get_server_info = AsyncMock(return_value=get_server_info_response)
        self.healthy = AsyncMock(side_effect=self._healthy)
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
        self.get_logs_from_file = AsyncMock(side_effect=self._get_logs_from_file)
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
        self.exists = AsyncMock(side_effect=self._exists)
        self.created = AsyncMock(side_effect=self._created)
        self.running = AsyncMock(side_effect=self._running)
        self.wait_until_healthy = AsyncMock()

    async def _send_command(self, *args, **kwargs):
        if self.healthy_response:
            return self.send_command_response
        else:
            raise Exception("Instance is not healthy")

    async def _list_players(self):
        if self.healthy_response:
            return self.list_players_response
        else:
            raise Exception("Instance is not healthy")

    async def _healthy(self):
        return self.healthy_response

    async def _exists(self):
        return self.exists_response

    async def _created(self):
        return self.created_response

    async def _running(self):
        return self.running_response

    def set_mocked_log_content(self, content: str):
        self.mocked_log_content = content

    async def _get_logs_from_file(self, log_pointer: int):
        self.pointer += len(self.mocked_log_content)
        return LogType(content=self.mocked_log_content, pointer=self.pointer)


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

    def assert_rcon_sent_to_server(self, server_name: str, command: str):
        self.instances_dict[server_name].send_command_rcon.assert_awaited_once_with(
            command
        )

    def assert_rcon_not_sent_to_server(self, server_name: str):
        self.instances_dict[server_name].send_command_rcon.assert_not_called()

    def assert_rcon_not_sent_to_any_server(self):
        for instance in self.instances_dict.values():
            self.assert_rcon_not_sent_to_server(instance.name)

    def reset_mocks(self):
        for instance in self.instances_dict.values():
            instance.send_command_rcon.reset_mock()
            instance.list_players.reset_mock()
            instance.get_server_info.reset_mock()
            instance.healthy.reset_mock()
            instance.get_log_file_end_pointer.reset_mock()
            instance.get_logs_from_file.reset_mock()
            instance.parse_player_messages_from_log.reset_mock()
            instance.get_player_messages_from_log.reset_mock()
            instance.get_logs_from_docker.reset_mock()
            instance.create.reset_mock()
            instance.update_compose_file.reset_mock()
            instance.remove.reset_mock()
            instance.up.reset_mock()
            instance.down.reset_mock()
            instance.start.reset_mock()
            instance.stop.reset_mock()
            instance.restart.reset_mock()
            instance.exists.reset_mock()
            instance.created.reset_mock()
            instance.running.reset_mock()
            instance.wait_until_healthy.reset_mock()

        self.get_running_server_names.reset_mock()
        self.get_instance.reset_mock()
        self.get_all_server_names.reset_mock()
        self.get_all_instances.reset_mock()
        self.get_all_server_compose_obj.reset_mock()
        self.get_all_server_compose_paths.reset_mock()
        self.get_all_server_info.reset_mock()
        self.parse_server_name_from_compose_obj.reset_mock()


@contextmanager
def mock_common_docker_mc_manager(mock_docker_mc_manager: MockDockerMCManager):
    with patch(
        "mc_qqbot_next.plugins.mc_qqbot_next.docker.docker_mc_manager",
        new=mock_docker_mc_manager,
    ):
        yield
