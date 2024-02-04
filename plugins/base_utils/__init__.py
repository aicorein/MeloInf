from melobot import Plugin, bot, BotLife, session


class BaseUtils(Plugin):
    __share__ = ["bot_name", "bot_id"]

    def __init__(self) -> None:
        super().__init__()
        self.bot_name = None
        self.bot_id = None

    @bot.on(BotLife.CONNECTED)
    async def get_login_info(self) -> None:
        resp = await session.get_login_info()
        if resp.is_ok():
            self.bot_name = resp.data["nickname"]
            self.bot_id =resp.data["user_id"]
            BaseUtils.LOGGER.info("成功获得 bot 账号信息并存储")
        else:
            BaseUtils.LOGGER.warning("获取 bot 账号信息失败")
