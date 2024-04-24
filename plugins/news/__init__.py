import asyncio
import datetime

from melobot import BotPlugin, reply_finish, send, thisbot
from melobot.base.tools import async_at, to_task
from melobot.context import send_custom
from melobot.models import image_msg

from ..env import BOT_INFO, COMMON_CHECKER, PARSER_FACTORY
from ..public_utils import async_http, base64_encode, get_headers

plugin = BotPlugin("EveryDayNews", version="1.0.0")

manual_news = plugin.on_message(
    checker=COMMON_CHECKER, parser=PARSER_FACTORY.get(targets=["news", "每日新闻"])
)


class PluginSpace:
    news_api = "https://api.03c3.cn/api/zb?type=img"
    news_time = tuple(map(int, BOT_INFO.news_time.split(":")))
    if len(news_time) != 3:
        raise ValueError("每日新闻时间的配置，必须是完整的 <时:分:秒> 格式")
    news_group = BOT_INFO.news_gruop


async def get_news_image() -> str | None:
    async with async_http(PluginSpace.news_api, "get", headers=get_headers()) as resp:
        if resp.status != 200:
            thisbot.logger.error(f"每日新闻图片获取异常，状态码：{resp.status}")
            return None
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
            data = await get_news_image()
            if data is None:
                return
            for g in PluginSpace.news_group:
                to_task(send_custom(image_msg(data), False, groupId=g))

        try:
            await async_at(news_launch(), news_t.timestamp())
            thisbot.logger.info("每日新闻已发送")
        except asyncio.CancelledError:
            thisbot.logger.info("每日新闻任务已取消")
            return


@manual_news
async def manual_news() -> None:
    data = await get_news_image()
    if data is None:
        await reply_finish("每日新闻图片获取异常，请稍后再试")
    await send(image_msg(data))
