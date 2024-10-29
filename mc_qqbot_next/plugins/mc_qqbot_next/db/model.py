from nonebot_plugin_orm import Model
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class QQUUIDMapping(Model):
    __tablename__ = "qq_uuid_mapping"
    qq_id: Mapped[str] = mapped_column(primary_key=True)
    uuid: Mapped[str] = mapped_column(ForeignKey("uuid_name_mapping.uuid"), unique=True)
    mc_player_info: Mapped["MCPlayerInfo"] = relationship(
        back_populates="qq_uuid_mapping"
    )


class MCPlayerInfo(Model):
    __tablename__ = "uuid_name_mapping"
    uuid: Mapped[str] = mapped_column(primary_key=True, autoincrement=False)
    name: Mapped[str]
    qq_uuid_mapping: Mapped["QQUUIDMapping"] = relationship(
        back_populates="mc_player_info"
    )


class MessageTarget(Model):
    __tablename__ = "message_target"
    message_id: Mapped[int] = mapped_column(primary_key=True)
    target_server: Mapped[str | None] = mapped_column(default=None)
    target_player: Mapped[str | None] = mapped_column(default=None)
