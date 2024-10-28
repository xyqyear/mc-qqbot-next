import nonebot
from nonebot.adapters.onebot.v11 import Adapter as OnebotAdapter

nonebot.init()

driver = nonebot.get_driver()
driver.register_adapter(OnebotAdapter)

nonebot.load_from_toml("pyproject.toml")

if __name__ == "__main__":
    nonebot.run()
