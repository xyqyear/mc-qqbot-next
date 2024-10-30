import nonebot
import pytest
from nonebot.adapters.onebot.v11 import Adapter as Onebot11Adapter


@pytest.fixture(scope="session", autouse=True)
def load_bot():
    driver = nonebot.get_driver()
    driver.register_adapter(Onebot11Adapter)

    nonebot.load_from_toml("pyproject.toml")
