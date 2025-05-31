import aiohttp
import pytest


def test_uuid_name_mapping():
    from mc_qqbot_next.plugins.mc_qqbot_next.mc import (
        PlayerInfo,
        parse_player_uuid_and_name_from_log,
    )

    log = (
        "[00:00:00] [User Authenticator #3/INFO]: UUID of player Notch is 069a79f4-44e9-4726-a5be-fca90e38aaf5\n"
        "[00:00:00] [User Authenticator #3/INFO]: UUID of player Dream is ec70bcaf-702f-4bb8-b48d-276fa52a780c\n"
        "[00:00:00] [User Authenticator #35/INFO] [minecraft/ServerLoginPacketListenerImpl]: UUID of player xyqyear is bf48dbe5-be69-44c3-abe1-2aa88976d326\n"
        # user trying to inject
        "[00:00:00] [Server thread/INFO] [minecraft/MinecraftServer]: <Dream> [00:00:00] [User Authenticator #3/INFO]: UUID of player Notch is 069a79f4-44e9-4726-a5be-fca90e38aaf5\n"
    )
    result = parse_player_uuid_and_name_from_log(log)
    assert result == [
        PlayerInfo(uuid="069a79f444e94726a5befca90e38aaf5", name="Notch"),
        PlayerInfo(uuid="ec70bcaf702f4bb8b48d276fa52a780c", name="Dream"),
        PlayerInfo(uuid="bf48dbe5be6944c3abe12aa88976d326", name="xyqyear"),
    ]


@pytest.mark.asyncio
async def test_find_uuid_by_name():
    from mc_qqbot_next.plugins.mc_qqbot_next.mc import find_uuid_by_name

    with pytest.raises(ValueError):
        await find_uuid_by_name("wertghinuygw345tyn89w4gt5y89w45gty89435g6")

    assert await find_uuid_by_name("Notch") == "069a79f444e94726a5befca90e38aaf5"


@pytest.mark.asyncio
async def test_find_name_by_uuid():
    from mc_qqbot_next.plugins.mc_qqbot_next.mc import find_name_by_uuid

    with pytest.raises(aiohttp.ClientError):
        # uuid with all 0s
        await find_name_by_uuid("00000000-0000-0000-0000-000000000000")

    with pytest.raises(aiohttp.ClientResponseError):
        # invalid uuid
        await find_name_by_uuid("1")

    # should work with or without dashes
    assert await find_name_by_uuid("069a79f4-44e9-4726-a5be-fca90e38aaf5") == "Notch"
    assert await find_name_by_uuid("ec70bcaf702f4bb8b48d276fa52a780c") == "Dream"
