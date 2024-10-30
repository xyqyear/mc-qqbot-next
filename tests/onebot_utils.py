import nonebot


def get_one_superuser():
    return next(iter(nonebot.get_driver().config.superusers))
