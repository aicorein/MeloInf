from urllib.parse import quote

from melobot import finish, msg_event, pause, reply_finish, send, thisbot
from melobot.base.exceptions import BotSessionTimeout
from melobot.base.tools import cooldown
from melobot.context import send_forward
from melobot.models import custom_msg_node

from ..env import BOT_INFO
from ..public_utils import async_http, get_headers
from ._iface import PluginSpace, anime_recognize


@anime_recognize
@cooldown(
    lambda: send("当前有一个识番任务运行中，稍候再试~"),
    lambda t: send("识番功能冷却中，剩余：%.2fs" % t),
    interval=10,
)
async def anime_recogize() -> None:
    bot_id = await thisbot.get_share("BaseUtils", "bot_id").val

    await send("【欢迎使用识番功能】\n现在请发送番剧截图")
    try:
        await pause(overtime=20)
    except BotSessionTimeout:
        await reply_finish("等待发送图片超时，识番任务已取消")

    params = msg_event().get_datas("image", "url")
    if len(params) <= 0:
        await reply_finish("发送的消息未识别到图片，识番功能已退出")
    req_url = PluginSpace.anime_search_url + quote(params[0])
    async with async_http(req_url, method="get", headers=get_headers()) as resp:
        if resp.status != 200:
            thisbot.logger.error(f"识别番剧 api 返回结果异常，状态码：{resp.status}")
            await finish("识别番剧 api 返回结果异常，请联系 bot 管理员或稍后再试")
        results = await resp.json()

    outputs = []
    for res in results["result"]:
        res["from"], res["to"] = round(res["from"]), round(res["to"])
        _from, to = (
            f"{res['from'] // 60}:{res['from'] % 60}",
            f"{res['to'] // 60}:{res['to'] % 60}",
        )
        filename, sim, title = (
            res["filename"],
            round(res["similarity"] * 100, 2),
            res["anilist"]["title"]["native"],
        )
        res_str = "【番名：{}】\n相似度：{}%\n对应文件：{}\n起始时间：{}~{}".format(
            title, sim, filename, _from, to
        )
        outputs.append(res_str)
    nodes = list(
        map(
            lambda x: custom_msg_node(x, sendName=BOT_INFO.bot_name, sendId=bot_id),
            outputs,
        )
    )
    await send_forward(nodes)
