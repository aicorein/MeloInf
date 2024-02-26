import asyncio as aio
from random import choice, randint

from melobot import Plugin, finish, image_msg, send, send_reply

from ..env import COMMON_CHECKER, PARSER_GEN, get_headers
from ..public_utils import async_http, base64_encode

rpic = Plugin.on_msg(
    parser=PARSER_GEN.gen(target=["随机图", "rpic"]), checker=COMMON_CHECKER
)


class RandomPicGen(Plugin):
    def __init__(self) -> None:
        super().__init__()
        self.url_gens = [
            lambda: "https://www.dmoe.cc/random.php",
            lambda: "https://cdn.seovx.com/d/?mom=302",
            lambda: "https://api.r10086.com/樱道随机图片api接口.php?图片系列=动漫综合{}".format(
                randint(1, 18)
            ),
            lambda: "https://img.xjh.me/random_img.php",
            lambda: "https://api.lyiqk.cn/acg",
            lambda: "https://api.lyiqk.cn/miku",
        ]
        self.get_pic_lock = aio.Lock()

    @rpic
    async def random_pic(self) -> None:
        if self.get_pic_lock.locked():
            await finish("请等待前一个图片获取任务完成，稍后再试~")
        async with self.get_pic_lock:
            async with async_http(
                url=choice(self.url_gens)(), method="get", headers=get_headers()
            ) as resp:
                if resp.status != 200:
                    await send_reply("图片获取失败...请稍后再试，或联系 bot 管理员解决")
                    RandomPicGen.LOGGER.error(f"请求失败：{resp.status}")
                    return
                try:
                    data = await resp.read()
                    code = base64_encode(data)
                    # path = str(self.ROOT.joinpath(f"{get_id()}.jpg"))
                    # with open(path, 'wb') as fp:
                    #     fp.write(data)
                    await send(image_msg(code), wait=True)
                except Exception as e:
                    await send_reply("图片获取失败...请稍后再试，或联系 bot 管理员解决")
                    RandomPicGen.LOGGER.error(f"{e.__class__.__name__} {e}")
