from nonebot import get_plugin_config
from pydantic import BaseModel


class MC(BaseModel):
    servers_root_path: str
    excluded_servers: list[str] = []
    default_server: str
    group_id: int
    restart_wait_seconds: int = 60 * 10


class Config(BaseModel):
    mc: MC


config = get_plugin_config(Config).mc
