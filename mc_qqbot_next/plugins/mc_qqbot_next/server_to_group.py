import asyncio

from minecraft_docker_manager_lib.instance import MCInstance, MCPlayerMessage
from nonebot.adapters.onebot.v11.bot import Bot
from nonebot.log import logger
from sqlalchemy.exc import IntegrityError

from .bot import get_onebot_bot
from .config import config
from .db.crud.binding import (
    create_or_update_mc_player_info,
    create_qq_uuid_mapping_by_player_name,
    delete_qq_uuid_mapping,
    get_qq_by_player_name,
)
from .docker import get_instance, get_running_server_names, send_message
from .mc import PlayerInfo, parse_player_uuid_and_name_from_log

server_log_pointer_dict = dict[str, int]()


async def check_mc_logs():
    logger.trace("Checking mc logs")
    bot = get_onebot_bot()
    if bot is None:
        logger.trace("No onebot bot fount, skip checking mc logs")
        return
    for server_name in await get_running_server_names():
        instance = await get_instance(server_name)
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
    if player_messages:
        logger.debug(f"Player messages: {player_messages}")
        await handle_player_messages(bot, server_name, player_messages)

    player_info_list = parse_player_uuid_and_name_from_log(log_content)
    if player_info_list:
        logger.debug(f"Player info list (player join): {player_info_list}")
        await handle_player_join(player_info_list)


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
    command = command.strip()
    if command.startswith("bind ") or command == "bind":
        arg = command[len("bind") :]
        arg = arg.strip()
        await handle_bind_command(
            server_name=server_name,
            player_name=player_name,
            arg=arg,
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


async def handle_bind_command(
    server_name: str,
    player_name: str,
    arg: str,
):
    match arg:
        case "" | "help":
            help_message = (
                "使用方法：\n"
                "\\\\bind get - 获取当前绑定信息\n"
                "\\\\bind remove - 解除绑定\n"
                "\\\\bind {qq号} - 绑定QQ号\n"
                "\\\\bind help - 显示此帮助信息"
            )
            await send_message(
                help_message,
                target_server=server_name,
                target_player=player_name,
            )
        case "get":
            qq_id = await get_qq_by_player_name(player_name)
            if qq_id is None:
                await send_message(
                    "未绑定QQ号",
                    target_server=server_name,
                    target_player=player_name,
                )
            else:
                await send_message(
                    f"已绑定QQ号：{qq_id}",
                    target_server=server_name,
                    target_player=player_name,
                )
        case "remove":
            qq_id = await get_qq_by_player_name(player_name)
            if qq_id is None:
                await send_message(
                    "未绑定QQ号",
                    target_server=server_name,
                    target_player=player_name,
                )
            else:
                await delete_qq_uuid_mapping(qq_id)
            await send_message(
                f"解绑 {qq_id} 成功",
                target_server=server_name,
                target_player=player_name,
            )
        case _ if arg.isdigit() and 5 <= len(arg) <= 12:
            try:
                await create_qq_uuid_mapping_by_player_name(
                    qq_id=arg,
                    name=player_name,
                )
            except IntegrityError as e:
                logger.info(e)
                await send_message(
                    "该QQ或游戏账号已有绑定",
                    target_server=server_name,
                    target_player=player_name,
                )

            await send_message(
                "绑定成功",
                target_server=server_name,
                target_player=player_name,
            )
        case _:
            await send_message(
                "无效QQ号",
                target_server=server_name,
                target_player=player_name,
            )


async def handle_player_join(
    plyaer_info_list: list[PlayerInfo],
):
    await asyncio.gather(
        *[
            create_or_update_mc_player_info(player_info.uuid, player_info.name)
            for player_info in plyaer_info_list
        ]
    )
