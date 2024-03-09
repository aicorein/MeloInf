import io
from typing import Tuple

from melobot import Plugin, PluginBus, bot, get_login_info, text_msg

from .utils import txt2img, wrap_s


class BaseUtils(Plugin):
    def __init__(self) -> None:
        super().__init__()
        self.SHARES.extend(["bot_name", "bot_id"])

        self.bot_name = None
        self.bot_id = None

    @PluginBus.on("BaseUtils", "txt2img")
    async def _txt2img(
        self,
        s: str,
        wrap_len: int = 70,
        font_size: int = 18,
        bg_color: str = "white",
        color: str = "black",
        margin: Tuple[int, int] = (10, 10),
    ) -> bytes:
        lines = s.split("\n")
        for idx, l in enumerate(lines):
            if len(l) > wrap_len:
                lines[idx] = "\n".join(wrap_s(l, wrap_len))
        text = "\n".join(lines)
        img = txt2img(text, font_size, bg_color, color, margin)
        imgio = io.BytesIO()
        img.save(imgio, format="JPEG", quality=95)
        return imgio.getvalue()

    @PluginBus.on("BaseUtils", "txt2msgs")
    async def txt2msgs(self, s: str, one_msg_len: int = 300):
        txt_list = list(map(lambda x: x.strip("\n"), wrap_s(s, one_msg_len)))
        return [text_msg(txt) for txt in txt_list]

    @bot.on_connected()
    async def get_login_info(self) -> None:
        resp = await get_login_info()
        if resp.is_ok():
            self.bot_name = resp.data["nickname"]
            self.bot_id = resp.data["user_id"]
            self.LOGGER.info("成功获得 bot 账号信息并存储")
        else:
            self.LOGGER.warning("获取 bot 账号信息失败")
