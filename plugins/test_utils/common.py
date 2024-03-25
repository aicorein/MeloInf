import asyncio as aio
import json
from random import randint
from typing import cast

from melobot import msg_args, msg_event, send, thisbot
from melobot.base import BotAction
from melobot.base.tools import get_id
from melobot.context import notice_event, send_custom_msg, take_custom_action
from melobot.models import (
    ResponseEvent,
    image_msg,
    poke_msg,
    reply_msg,
    text_msg,
    to_cq_str,
)

from ..public_utils import base64_encode
from ._iface import PluginRef, PluginSpace, atest, echo, io_debug, plugin, poke, test_n


@atest
async def async_test() -> None:
    sec = randint(*PluginSpace.async_t)
    id = str(get_id())[-6:]
    resp = await send(f"异步测试开始。时长：{sec}s，识别标记：{id}", wait=True)
    resp = cast(ResponseEvent, resp)
    await aio.sleep(sec)
    await send(
        [
            reply_msg(resp.data["message_id"]),
            text_msg(f"√ 标记为 {id} 的异步测试完成"),
        ]
    )
    PluginSpace.test_cnt += 1


@test_n
async def test_stat() -> None:
    await send(f"已进行的测试次数：{PluginSpace.test_cnt}")


@echo
async def echo() -> None:
    output_cq = to_cq_str(msg_event().content)[6:]
    await send(output_cq, cq_str=True)


@io_debug
async def io_debug() -> None:
    status = msg_args().pop(0)
    PluginSpace.io_debug_flag = status


@plugin.on_action_presend
async def io_debug_hook(action: BotAction) -> None:
    if action.flag_check("TestUtils", "io-debug"):
        return
    if not PluginSpace.io_debug_flag:
        return
    if action.trigger is None or "message" not in action.params.keys():
        return

    e_str = json.dumps(action.trigger.raw, ensure_ascii=False, indent=2)
    a_str = action.flatten(indent=2)
    debug_action = action.copy()
    output = f"event:\n{e_str}\n\naction:\n{a_str}"
    if len(output) <= 10000:
        data = await thisbot.emit_signal(
            "BaseUtils", "txt2img", output, 50, 16, wait=True
        )
        data = base64_encode(data)
        debug_action.params["message"] = [image_msg(data)]
    else:
        debug_action.params["message"] = [text_msg("[调试输出过长，请使用调试器]")]
    debug_action.resp_id = None
    debug_action.mark("TestUtils", "io-debug")
    await take_custom_action(debug_action)


@poke
async def poke() -> None:
    event = notice_event()
    if event.notice_user_id != (await PluginRef.bot_id()):
        return
    poke_qid = event.notice_operator_id
    await send_custom_msg(
        poke_msg(poke_qid),
        not event.is_group(),
        event.notice_operator_id,
        event.notice_group_id if event.is_group() else None,
    )
