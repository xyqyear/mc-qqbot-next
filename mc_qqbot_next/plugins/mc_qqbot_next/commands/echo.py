from nonebot import on_command
from nonebot.adapters import Message
from nonebot.params import CommandArg

echo = on_command("echo")


@echo.handle()
async def handle_echo(msg: Message = CommandArg()):
    await echo.finish(msg.extract_plain_text())
