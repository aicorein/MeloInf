import asyncio as aio
import json
from random import randint

from melobot import msg_args, msg_event, reply_finish, send, send_reply, thisbot
from melobot.base import BotAction
from melobot.base.tools import get_id
from melobot.base.typing import MsgSegment
from melobot.context import (
    custom_action,
    get_msg,
    notice_event,
    send_custom,
    send_forward,
)
from melobot.models import (
    NoticeEvent,
    custom_msg_node,
    custom_type_msg,
    image_msg,
    reply_msg,
    text_msg,
    to_cq_str,
)

from ..env import BOT_INFO
from ..public_utils import base64_encode
from ._iface import (
    PluginRef,
    PluginSpace,
    atest,
    echo,
    get_img_url,
    io_debug,
    plugin,
    poke,
    test_n,
)


@atest
async def async_test() -> None:
    sec = randint(*PluginSpace.async_t)
    id = str(get_id())[-6:]
    handle = send(f"异步测试开始。时长：{sec}s，识别标记：{id}", wait=True)
    await aio.sleep(sec)
    await send(
        [
            reply_msg((await handle.resp).data["message_id"]),
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
    status = msg_args()[0]
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
    await custom_action(debug_action.type, debug_action.params)


def poke_msg(event: NoticeEvent) -> MsgSegment:
    if not event.is_group():
        msg = custom_type_msg("friend_poke", {"user_id": str(event.operator_id)})
    else:
        msg = custom_type_msg(
            "group_poke",
            {"group_id": str(event.group_id), "user_id": str(event.operator_id)},
        )
    return msg


@poke
async def poke() -> None:
    event = notice_event()
    if event.user_id != (await PluginRef.bot_id()):
        return
    await send_custom(
        poke_msg(event),
        not event.is_group(),
        event.operator_id,
        event.group_id if event.is_group() else None,
    )


@get_img_url
async def get_img_url() -> None:
    event = msg_event()
    ids = event.get_datas("reply", "id")
    if len(ids) == 0:
        await reply_finish("未引用要获取的消息，无法获取")
    handle = get_msg(ids[-1], wait=True)
    urls = [
        seg["data"]["file"]
        for seg in (await handle.resp).data["message"]
        if seg["type"] == "image"
    ]
    if len(urls) == 0:
        await reply_finish("引用的消息中不存在图片/表情包，或表情包不是纯图片")

    if len(urls) == 1:
        output = "图片链接：\n" + "\n".join(urls)
        await send_reply(output)
    else:
        outputs = urls
        bot_id = await PluginRef.bot_id()
        outputs.insert(0, "【以下为所有图片的链接】")
        nodes = list(
            map(
                lambda x: custom_msg_node(x, sendName=BOT_INFO.bot_name, sendId=bot_id),
                outputs,
            )
        )
        await send_forward(nodes)
