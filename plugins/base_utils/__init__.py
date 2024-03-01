import io
import json
from typing import Tuple

from melobot import (
    BotAction,
    BotLife,
    Plugin,
    PluginBus,
    PluginStore,
    bot,
    image_msg,
    session,
    text_msg,
)

from ..public_utils import base64_encode
from .utils import txt2img, wrap_s


class BaseUtils(Plugin):
    __share__ = ["bot_name", "bot_id", "debug_status"]

    def __init__(self) -> None:
        super().__init__()
        self.bot_name = None
        self.bot_id = None
        self.debug_status = False

    @PluginStore.echo("BaseUtils", "debug_status")
    async def _debug_status_change(self, status: bool) -> None:
        self.debug_status = status

    @PluginBus.on("BaseUtils", "txt2img")
    async def _txt2img(
        self,
        s: str,
        wrap_len: int = 70,
        font_size: int = 18,
        bg_color: str = "white",
        color: str = "black",
        margin: Tuple[int, int] = [10, 10],
    ) -> bytes:
        text = "\n".join(wrap_s(s, wrap_len))
        img = txt2img(text, font_size, bg_color, color, margin)
        imgio = io.BytesIO()
        img.save(imgio, format="JPEG", quality=95)
        return imgio.getvalue()

    @PluginBus.on("BaseUtils", "txt2msgs")
    async def txt2msgs(self, s: str, one_msg_len: int = 200):
        txt_list = wrap_s(s, one_msg_len)
        return [text_msg(txt) for txt in txt_list]

    @bot.on(BotLife.CONNECTED)
    async def get_login_info(self) -> None:
        resp = await session.get_login_info()
        if resp.is_ok():
            self.bot_name = resp.data["nickname"]
            self.bot_id = resp.data["user_id"]
            BaseUtils.LOGGER.info("成功获得 bot 账号信息并存储")
        else:
            BaseUtils.LOGGER.warning("获取 bot 账号信息失败")

    @bot.on(BotLife.ACTION_PRESEND)
    async def _action_debug(self, action: BotAction) -> None:
        if hasattr(action, "is_debug"):
            return
        if self.debug_status:
            e_str = (
                json.dumps(action.trigger.raw, ensure_ascii=False, indent=2)
                if action.trigger is not None
                else "<触发事件为空>"
            )
            a_str = action.flatten(indent=2)
            debug_action = action.copy()
            output = f"event:\n{e_str}\n\naction:\n{a_str}"
            if len(output) <= 10000:
                data = await PluginBus.emit(
                    "BaseUtils", "txt2img", output, 200, 14, wait=True
                )
                data = base64_encode(data)
                debug_action.params["message"] = [image_msg(data)]

            else:
                debug_action.params["message"] = [
                    text_msg("[调试输出过长，请使用调试器]")
                ]
            if debug_action.resp_id:
                debug_action.resp_id = None
            debug_action.is_debug = True
            await session.custom_action(debug_action)
