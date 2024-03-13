from urllib.parse import quote

from melobot import (
    AttrSessionRule,
    Plugin,
    PluginStore,
    cooldown,
    finish,
    msg_event,
    pause,
    reply_finish,
    send,
)
from melobot.context.action import send_forward
from melobot.models.cq import custom_msg_node
from melobot.types.exceptions import SessionHupTimeout

from ..env import BOT_INFO, COMMON_CHECKER, PARSER_GEN
from ..public_utils import async_http, get_headers

anime_recognize = Plugin.on_message(
    checker=COMMON_CHECKER,
    parser=PARSER_GEN.gen(["番剧识别", "anime"]),
    session_rule=AttrSessionRule("sender", "id"),
    direct_rouse=True,
    conflict_cb=lambda: send("你已触发一个识番任务，拒绝再次触发"),
)


class AnimeSearcher(Plugin):
    def __init__(self) -> None:
        super().__init__()
        self.bot_id = PluginStore.get("BaseUtils", "bot_id")
        self.anime_search_url = (
            "https://api.trace.moe/search?anilistInfo&cutBorders&url="
        )

    @anime_recognize
    @cooldown(
        lambda: send("当前有一个识番任务运行中，稍候再试~"),
        lambda t: send("识番功能冷却中，剩余：%.2fs" % t),
        interval=10,
    )
    async def anime_recogize(self) -> None:
        await send("【欢迎使用识番功能】\n现在请发送番剧截图")
        try:
            await pause(overtime=20)
        except SessionHupTimeout:
            await reply_finish("等待发送图片超时，识番任务已取消")

        params = msg_event().get_cq_params("image", "url")
        if len(params) <= 0:
            await reply_finish("发送的消息未识别到图片，识番功能已退出")
        req_url = self.anime_search_url + quote(params.pop(0))
        async with async_http(req_url, method="get", headers=get_headers()) as resp:
            if resp.status != 200:
                self.LOGGER.error(f"识别番剧 api 返回结果异常，状态码：{resp.status}")
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
                lambda x: custom_msg_node(
                    x, sendName=BOT_INFO.bot_name, sendId=self.bot_id.val
                ),
                outputs,
            )
        )
        await send_forward(nodes)
