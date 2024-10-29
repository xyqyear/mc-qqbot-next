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
