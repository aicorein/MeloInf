import asyncio as aio
import json

from melobot import thisbot
from melobot.base.exceptions import BotException

from ..public_utils import async_http, get_headers


async def json_pic1() -> str:
    url = "http://api.xn--7gqa009h.top/api/sjdm"
    async with async_http(
        url, method="get", headers=get_headers(), proxy=False
    ) as resp:
        if resp.status != 200:
            err = f"从 api 获取图片网址失败，状态码：{resp.status}"
            thisbot.logger.error(err)
            raise BotException(err)
        else:
            res = await resp.text()
            res = json.loads(res)
            if res["code"] == 1:
                await aio.sleep(3)
                return await json_pic1()
            else:
                return res["url"]
