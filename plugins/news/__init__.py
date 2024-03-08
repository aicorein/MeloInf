import datetime
from functools import partial

from melobot import Plugin, bot, image_msg, send, send_custom_msg, to_coro
from melobot.types.exceptions import BotException

from ..env import BOT_INFO, COMMON_CHECKER, PARSER_GEN
from ..public_utils import async_http, base64_encode, get_headers

manual_news = Plugin.on_message(
    checker=COMMON_CHECKER, parser=PARSER_GEN.gen(target=["news", "每日新闻"])
)


class EveryDayNews(Plugin):
    def __init__(self) -> None:
        super().__init__()
        self.news_api = "https://api.03c3.cn/api/zb?type=img"
        self.news_time = tuple(map(int, BOT_INFO.news_time.split(":")))
        if len(self.news_time) != 3:
            raise ValueError("每日新闻时间的配置，必须是完整的 <时:分:秒> 格式")
        self.news_group = BOT_INFO.news_gruop

    async def get_news_image(self) -> str:
        async with async_http(
            self.news_api, method="get", headers=get_headers()
        ) as resp:
            if resp.status != 200:
                raise BotException(f"每日新闻图片获取异常，状态码：{resp.status}")
            data = await resp.content.read()
            data = base64_encode(data)
            return data

    @bot.on_all_loaded()
    async def news_arrange(self) -> None:
        if len(self.news_group) == 0:
            return
        while True:
            cur_t = datetime.datetime.now()
            news_t = datetime.datetime(
                cur_t.year,
                cur_t.month,
                cur_t.day,
                self.news_time[0],
                self.news_time[1],
                self.news_time[2],
            )
            if cur_t > news_t:
                news_t += datetime.timedelta(days=1)

            async def news_launch() -> None:
                image = await self.get_news_image()
                for g in self.news_group:
                    await send_custom_msg(image_msg(image), False, groupId=g)

            await bot.async_at(
                news_launch(),
                news_t.timestamp(),
                exit_cb=to_coro(partial(self.LOGGER.info, "每日新闻任务已取消")),
            )
            self.LOGGER.info("每日新闻已发送")

    @manual_news
    async def manual_news(self) -> None:
        data = await self.get_news_image()
        await send(image_msg(data))
