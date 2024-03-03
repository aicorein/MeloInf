import hashlib
from typing import Tuple

from melobot import send_reply
from melobot.types import BotException

from ..env import BOT_INFO
from ..public_utils import async_http, get_headers

appid, salt, key = (
    BOT_INFO.baidu_translate_appid,
    BOT_INFO.hash_salt,
    BOT_INFO.baidu_translate_key,
)
headers = get_headers()
headers["Content-Type"] = "application/x-www-form-urlencoded"


async def get_translated_text(text: str, target_lang: str) -> Tuple[str, str, str]:
    sign = appid + text + salt + key
    md5 = hashlib.md5()
    md5.update(sign.encode("utf-8"))
    data = {
        "q": text,
        "from": "auto",
        "to": target_lang,
        "appid": appid,
        "salt": salt,
        "sign": md5.hexdigest(),
    }
    url = "https://fanyi-api.baidu.com/api/trans/vip/translate"
    async with async_http(url, method="post", headers=headers, data=data) as resp:
        if resp.status != 200:
            await send_reply("翻译获取失败...请稍后再试，或联系 bot 管理员解决")
            raise BotException(f"请求失败：{resp.status}")
        try:
            data = await resp.json()
            return data["from"], data["to"], data["trans_result"][0]["dst"]
        except Exception as e:
            await send_reply("翻译获取失败...请稍后再试，或联系 bot 管理员解决")
            raise BotException(f"{e.__class__.__name__} {e}")
