import datetime

from melobot import BotPlugin, send, thisbot
from melobot.context import send_custom_msg
from melobot.models import image_msg
from melobot.types.exceptions import BotException
from melobot.types.tools import async_at, to_coro

from ..env import BOT_INFO, COMMON_CHECKER, PARSER_GEN
from ..public_utils import async_http, base64_encode, get_headers

plugin = BotPlugin("EveryDayNews", version="1.0.0")

manual_news = plugin.on_message(
    checker=COMMON_CHECKER, parser=PARSER_GEN.gen(target=["news", "每日新闻"])
)


class PluginSpace:
    news_api = "https://api.03c3.cn/api/zb?type=img"
    news_time = tuple(map(int, BOT_INFO.news_time.split(":")))
    if len(news_time) != 3:
        raise ValueError("每日新闻时间的配置，必须是完整的 <时:分:秒> 格式")
    news_group = BOT_INFO.news_gruop


async def get_news_image() -> str:
    async with async_http(PluginSpace.news_api, "get", headers=get_headers()) as resp:
        if resp.status != 200:
            raise BotException(f"每日新闻图片获取异常，状态码：{resp.status}")
        data = await resp.content.read()
        data = base64_encode(data)
        return data


@plugin.on_plugins_loaded
async def news_arrange() -> None:
    if len(PluginSpace.news_group) == 0:
        return
    while True:
        cur_t = datetime.datetime.now()
        news_t = datetime.datetime(
            cur_t.year,
            cur_t.month,
            cur_t.day,
            PluginSpace.news_time[0],
            PluginSpace.news_time[1],
            PluginSpace.news_time[2],
        )
        if cur_t > news_t:
            news_t += datetime.timedelta(days=1)

        async def news_launch() -> None:
            image = await get_news_image()
            for g in PluginSpace.news_group:
                await send_custom_msg(image_msg(image), False, groupId=g)

        import asyncio as aio

        try:
            await async_at(news_launch(), news_t.timestamp())
        except aio.CancelledError:
            thisbot.logger.info("每日新闻任务已取消")
            return
        thisbot.logger.info("每日新闻已发送")


@manual_news
async def manual_news() -> None:
    data = await get_news_image()
    await send(image_msg(data))
