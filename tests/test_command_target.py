import pytest
from nonebug import App

from .docker_mc_mocks import (
    MockDockerMCManager,
    MockMCInstance,
    mock_common_docker_mc_manager,
)


@pytest.mark.asyncio
async def test_extract_content_and_target_from_str(app: App):
    """Test the extract_content_and_target_from_str function with mocked docker manager"""
    from mc_qqbot_next.plugins.mc_qqbot_next.config import config
    from mc_qqbot_next.plugins.mc_qqbot_next.dependencies import (
        CommandTarget,
        extract_content_and_target_from_str,
    )

    config.mc_default_server = "default_server"
    config.mc_excluded_servers = ["excluded"]

    mock_docker_mc_manager = MockDockerMCManager(
        instances=[
            MockMCInstance(
                name="server1",
                game_port=25565,
            ),
            MockMCInstance(
                name="server2", 
                game_port=25566,
            ),
            MockMCInstance(
                name="default_server",
                game_port=25567,
            ),
            MockMCInstance(
                name="ser",
                game_port=25568,
            ),
            MockMCInstance(
                name="excluded",
                game_port=25569,
            ),
        ],
    )

    with mock_common_docker_mc_manager(mock_docker_mc_manager):
        
        async def test_case(input_str: str, expected_content: str, expected_server: str | None):
            """Helper function to test a single case"""
            content, server = await extract_content_and_target_from_str(input_str)
            assert content == expected_content
            assert server == expected_server
            
            # Also test creating CommandTarget object
            result = CommandTarget(
                arg=content, 
                target_server=server or "default", 
                is_explicit=server is not None
            )
            assert result.arg == expected_content
            assert result.is_explicit == (server is not None)
            if server is not None:
                assert result.target_server == server
            else:
                assert result.target_server == "default"

        # Test explicit server specification
        await test_case("hello world /server1", "hello world", "server1")
        
        # Test partial server name matching
        await test_case("hello world /s", "hello world", "server1")  # should match first server starting with 's'
        await test_case("hello world /ser", "hello world", "ser")     # should match exact 'ser'
        
        # Test no server specification
        await test_case("hello world", "hello world", None)
        
        # Test empty command with server
        await test_case("/server1", "", "server1")
        
        # Test server that doesn't exist - should extract content but server is None
        await test_case("hello /nonexistent", "hello", None)
        
        # Test excluded server (should be filtered out, so not found)
        await test_case("hello /excluded", "hello", None)


@pytest.mark.asyncio 
async def test_command_target_edge_cases(app: App):
    """Test edge cases for CommandTarget functionality"""
    from mc_qqbot_next.plugins.mc_qqbot_next.dependencies import (
        extract_content_and_target_from_str,
    )

    mock_docker_mc_manager = MockDockerMCManager(
        instances=[
            MockMCInstance(name="test_server", game_port=25565),
        ],
    )

    with mock_common_docker_mc_manager(mock_docker_mc_manager):
        
        # Test multiple slashes
        content, server = await extract_content_and_target_from_str("hello /world /test_server")
        assert content == "hello /world"
        assert server == "test_server"
        
        # Test trailing whitespace
        content, server = await extract_content_and_target_from_str("hello world /test_server ")
        assert content == "hello world /test_server "  # trailing space should be preserved in non-match
        assert server is None
        
        # Test just a slash
        content, server = await extract_content_and_target_from_str("hello /")
        assert content == "hello /"
        assert server is None
        
        # Test empty string
        content, server = await extract_content_and_target_from_str("")
        assert content == ""
        assert server is None
