from nonebot import on_command

from ...mc import list_players_for_all_servers

ping = on_command("ping", aliases={"list"})


@ping.handle()
async def handle_ping():
    """
    列出当前运行中的服务器和在线玩家

    返回格式：
    ---
    [vanilla]: player1, player2
    [other]: player3
    没人: [atm9s], [ftb]
    g了: [badserver1], [badserver2]
    ---
    """
    servers_player_listing = await list_players_for_all_servers()

    servers_with_players = []
    servers_without_players = []
    servers_bad = []

    for server_name, players in servers_player_listing:
        if players is None:
            servers_bad.append(f"[{server_name}]")
            continue
        if players:
            players_str = ", ".join(players)
            servers_with_players.append(f"[{server_name}]: {players_str}")
        else:
            servers_without_players.append(f"[{server_name}]")

    message_parts = []
    if servers_with_players:
        message_parts.extend(servers_with_players)
    if servers_without_players:
        message_parts.append(f"没人: {', '.join(servers_without_players)}")
    if servers_bad:
        message_parts.append(f"g了: {', '.join(servers_bad)}")

    final_message = (
        "\n".join(message_parts) if message_parts else "当前没有运行中的服务器"
    )

    await ping.finish(final_message)
