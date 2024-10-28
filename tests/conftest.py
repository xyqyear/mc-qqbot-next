import os
import shutil

import nonebot
import nonebot.config
import pytest
from nonebot.adapters.onebot.v11 import Adapter as OnebotAdapter


@pytest.fixture(scope="session", autouse=True)
def load_bot():
    if os.path.exists("data_test"):
        shutil.rmtree("data_test")

    nonebot.init()
    driver = nonebot.get_driver()
    driver.register_adapter(OnebotAdapter)

    nonebot.load_from_toml("pyproject.toml")
