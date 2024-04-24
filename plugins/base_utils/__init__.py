import io
from typing import Tuple

from melobot import BotPlugin, thisbot
from melobot.context import get_login_info, get_onebot_version
from melobot.models import text_msg

from .utils import txt2img, wrap_s

plugin = BotPlugin("BaseUtils", version="1.3.0")


class PluginSpace:
    bot_name: str = "<尚未获取>"
    bot_id: int = -1
    cq_app_name: str = "<尚未获取>"
    cq_app_ver: str = "<尚未获取>"
    cq_protocol_ver: str = "<尚未获取>"
    cq_other_infos: dict = {}


def share_var(name: str):
    plugin.on_share(name, reflector=lambda: getattr(PluginSpace, name))


share_var("bot_name")
share_var("bot_id")
share_var("cq_app_name")
share_var("cq_app_ver")
share_var("cq_protocol_ver")
share_var("cq_other_infos")


@plugin.on_signal("txt2img")
async def txt_to_img(
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


@plugin.on_signal("txt2msgs")
async def txt2msgs(s: str, one_msg_len: int = 300):
    txt_list = list(map(lambda x: x.strip("\n"), wrap_s(s, one_msg_len)))
    return [text_msg(txt) for txt in txt_list]


@plugin.on_connected
async def login_info() -> None:
    resp = await get_login_info().resp
    if resp.is_ok():
        PluginSpace.bot_name = resp.data["nickname"]
        PluginSpace.bot_id = resp.data["user_id"]
        thisbot.logger.info("成功获得 bot 账号信息并存储")
    else:
        thisbot.logger.warning("获取 bot 账号信息失败")


@plugin.on_connected
async def get_version_info() -> None:
    resp = await get_onebot_version().resp
    if resp.is_ok():
        PluginSpace.cq_app_name = resp.data.pop("app_name")
        PluginSpace.cq_app_ver = resp.data.pop("app_version")
        PluginSpace.cq_protocol_ver = resp.data.pop("protocol_version")
        PluginSpace.cq_other_infos = resp.data
        thisbot.logger.info("成功获得 onebot 实现程序的信息并存储")
    else:
        thisbot.logger.warning("获取 onebot 实现程序的信息失败")
