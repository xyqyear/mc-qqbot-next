from nonebot import require
from nonebot.plugin import PluginMetadata

require("nonebot_plugin_apscheduler")
require("nonebot_plugin_orm")
from nonebot_plugin_apscheduler import scheduler  # noqa: E402

from . import commands  # noqa: F401, E402
from .server_to_group import check_mc_logs  # noqa: E402

__plugin_meta__ = PluginMetadata(
    name="mc-qqbot-next",
    description="",
    usage="",
)

scheduler.add_job(check_mc_logs, "interval", seconds=1)
