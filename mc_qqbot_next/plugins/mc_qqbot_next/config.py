from nonebot import get_driver
from pydantic import BaseModel, ConfigDict, Field


class Config(BaseModel):
    model_config = ConfigDict(extra="ignore")

    mc_servers_root_path: str = Field(None, validate_default=False)
    mc_excluded_servers: list[str] = []
    mc_default_server: str | None = None
    mc_group_id: int = Field(None, validate_default=False)
    mc_restart_wait_seconds: int = 60 * 10


global_config = get_driver().config
config = Config.model_validate(global_config.model_dump())

if config.mc_servers_root_path is None or config.mc_servers_root_path == "":
    raise ValueError("Please set MC_SERVERS_ROOT_PATH")
if config.mc_default_server == []:
    config.mc_default_server = ""
if config.mc_group_id is None or config.mc_group_id == 0:
    raise ValueError("Please set MC_GROUP_ID")
