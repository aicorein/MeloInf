import platform

from melobot import GenericLogger, MetaInfo, Plugin, get_bot, send_text
from melobot.protocols.onebot.v11 import Adapter, EchoRequireCtx, on_message

from ...env import ENVS
from ...platform.onebot import COMMON_CHECKER, PARSER_FACTORY
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
        self.flows = (reply_info,)
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


@on_message(parser=PARSER_FACTORY.get(targets=["info", "信息"]), checker=COMMON_CHECKER)
async def reply_info() -> None:
    output = Store.bot_info.format(
        ENVS.bot.bot_nicknames[0],
        MetaInfo.name,
        MetaInfo.ver,
        ENVS.bot.proj_name,
        ENVS.bot.proj_ver,
        ENVS.bot.proj_src.lstrip("https://"),
        platform.python_version(),
        platform.system(),
        f'[{", ".join(a.protocol for a in bot.get_adapters(lambda _: True))}]',
        f'[{", ".join(bot.get_plugins())}]',
    )
    await send_text(output)

    output = Store.onebot_info_str.format(
        Store.onebot_app_name,
        Store.onebot_app_ver,
        Store.onebot_protocol_ver,
        Store.onebot_other_infos,
    )
    await send_text(output)
