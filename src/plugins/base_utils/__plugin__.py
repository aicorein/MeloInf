from melobot import GenericLogger, Plugin, get_bot
from melobot.protocols.onebot.v11 import Adapter, EchoRequireCtx

from .funcs import txt2img, wrap_s
from .shares import (
    Store,
    onebot_app_name,
    onebot_app_ver,
    onebot_id,
    onebot_name,
    onebot_other_infos,
    onebot_protocol_ver,
)


class BaseUtils(Plugin):
    def __init__(self) -> None:
        super().__init__()
        self.version = "1.3.0"
        self.shares = (
            onebot_app_name,
            onebot_app_ver,
            onebot_id,
            onebot_name,
            onebot_other_infos,
            onebot_protocol_ver,
        )
        self.funcs = (txt2img, wrap_s)


bot = get_bot()


@bot.on_loaded
async def get_onebot_login_info(adapter: Adapter, logger: GenericLogger) -> None:
    with EchoRequireCtx().in_ctx(True):
        echo = await (await adapter.get_login_info())[0]
    data = echo.data
    if echo.is_ok():
        Store.onebot_name = data["nickname"]
        Store.onebot_id = data["user_id"]
        logger.info("成功获得 OneBot 账号信息并存储")
    else:
        logger.warning("获取 OneBot 账号信息失败")


@bot.on_loaded
async def get_onebot_app_info(adapter: Adapter, logger: GenericLogger) -> None:
    with EchoRequireCtx().in_ctx(True):
        echo = await (await adapter.get_version_info())[0]
    data = echo.data
    if echo.is_ok():
        Store.onebot_app_name = data.pop("app_name")
        Store.onebot_app_ver = data.pop("app_version")
        Store.onebot_protocol_ver = data.pop("protocol_version")
        Store.onebot_other_infos = data
        logger.info("成功获得 onebot 实现程序的信息并存储")
    else:
        logger.warning("获取 onebot 实现程序的信息失败")
