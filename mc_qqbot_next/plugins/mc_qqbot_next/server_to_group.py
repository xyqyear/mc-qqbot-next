from minecraft_docker_manager_lib.instance import MCInstance, MCPlayerMessage
from nonebot.adapters.onebot.v11.bot import Bot
from nonebot.log import logger

from .bot import get_onebot_bot
from .config import config
from .docker import docker_mc_manager

server_log_pointer_dict = dict[str, int]()


async def check_mc_logs():
    logger.trace("Checking mc logs")
    bot = get_onebot_bot()
    if bot is None:
        logger.trace("No onebot bot fount, skip checking mc logs")
        return
    for server_name in await docker_mc_manager.get_running_server_names():
        instance = docker_mc_manager.get_instance(server_name)
        if server_name not in server_log_pointer_dict:
            server_log_pointer_dict[
                server_name
            ] = await instance.get_log_file_end_pointer()
            continue
        log_pointer = server_log_pointer_dict[server_name]
        log = await instance.get_logs_from_file(log_pointer)
        server_log_pointer_dict[server_name] = log.pointer

        await handle_new_log(bot, server_name, log.content)


async def handle_new_log(
    bot: Bot,
    server_name: str,
    log_content: str,
):
    player_messages = MCInstance.parse_player_messages_from_log(log_content)
    logger.trace(f"Player messages: {player_messages}")
    await handle_player_messages(bot, server_name, player_messages)


async def handle_player_messages(
    bot: Bot,
    server_name: str,
    player_messages: list[MCPlayerMessage],
):
    for player_message in player_messages:
        startswith_candidate = (r"\\", "、、")
        for startswith in startswith_candidate:
            if player_message.message.startswith(startswith):
                command = player_message.message[len(startswith) :]
                await handle_command(
                    bot=bot,
                    server_name=server_name,
                    player_name=player_message.player,
                    command=command,
                )
                break


async def handle_command(
    bot: Bot,
    server_name: str,
    player_name: str,
    command: str,
):
    if command.startswith("bind "):
        arg = command[len("bind ") :]
        await handle_bind_command(
            bot=bot,
            player_name=player_name,
            arg=arg,
        )
    elif command == "unbind":
        await handle_unbind_command(
            bot=bot,
            player_name=player_name,
        )
    else:
        await handle_send_command(
            bot=bot,
            server_name=server_name,
            player_name=player_name,
            message=command,
        )


async def handle_send_command(
    bot: Bot,
    server_name: str,
    player_name: str,
    message: str,
):
    await bot.send_group_msg(
        group_id=config.group_id,
        message=f"[{server_name}] <{player_name}>: {message}",
    )


# TODO
async def handle_bind_command(
    bot: Bot,
    player_name: str,
    arg: str,
): ...


async def handle_unbind_command(
    bot: Bot,
    player_name: str,
): ...


async def handle_player_join(
    bot: Bot,
    server_name: str,
    player_name: str,
    join: bool,
): ...
