from random import choice, randint

from melobot import Plugin, cooldown, send, send_reply
from melobot.models import image_msg

from ..env import COMMON_CHECKER, PARSER_GEN
from ..public_utils import async_http, base64_encode, get_headers
from .utils import json_pic1

rpic = Plugin.on_message(
    parser=PARSER_GEN.gen(target=["随机图", "rpic"]),
    checker=COMMON_CHECKER,
    timeout=25,
    overtime_cb=lambda: send_reply("图片获取超时，请稍候再试..."),
)


class RandomPicGen(Plugin):
    def __init__(self) -> None:
        super().__init__()
        self.url_gens = [
            lambda: "https://www.dmoe.cc/random.php",
            lambda: "https://cdn.seovx.com/d/?mom=302",
            lambda: "https://img.xjh.me/random_img.php",
            lambda: "https://api.lyiqk.cn/acg",
            lambda: "https://api.lyiqk.cn/miku",
            lambda: "https://api.r10086.com/樱道随机图片api接口.php?图片系列=动漫综合{}".format(
                randint(1, 18)
            ),
        ]

    async def get_pic_url(self) -> str:
        res = choice(self.url_gens)()
        if not isinstance(res, str):
            return await res
        return res

    @rpic
    @cooldown(
        lambda: send("请等待前一个图片获取任务完成，稍后再试~"),
        lambda t: send("图片获取功能冷却中，剩余：%.2fs" % t),
        interval=10,
    )
    async def random_pic(self) -> None:
        url = await self.get_pic_url()
        async with async_http(url=url, method="get", headers=get_headers()) as resp:
            if resp.status != 200:
                await send_reply("图片获取失败...请稍后再试，或联系 bot 管理员解决")
                self.LOGGER.error(f"请求失败：{resp.status}")
                return
            try:
                data = await resp.read()
                code = base64_encode(data)
                await send(image_msg(code), wait=True)
            except Exception as e:
                await send_reply("图片获取失败...请稍后再试，或联系 bot 管理员解决")
                self.LOGGER.error(f"{e.__class__.__name__} {e}")
