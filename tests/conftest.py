import os
import shutil

import nonebot
import nonebot.drivers
import pytest
from nonebot.adapters.onebot.v11 import Adapter as Onebot11Adapter


@pytest.fixture(scope="session", autouse=True)
def load_bot():
    driver = nonebot.get_driver()
    driver.register_adapter(Onebot11Adapter)

    data_dir = driver.config.localstore_data_dir
    if os.path.exists(data_dir):
        shutil.rmtree(data_dir)

    nonebot.load_from_toml("pyproject.toml")
