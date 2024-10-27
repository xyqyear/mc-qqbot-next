from nonebot_plugin_orm import Model
from sqlalchemy.orm import Mapped, mapped_column


class QQUUIDMapping(Model):
    qq_id: Mapped[str] = mapped_column(primary_key=True)
    uuid: Mapped[str] = mapped_column(unique=True)
    player_name: Mapped[str]
