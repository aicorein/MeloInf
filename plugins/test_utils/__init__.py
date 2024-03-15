import asyncio as aio
import json
from random import randint
from typing import cast

from melobot import ArgFormatter as Format
from melobot import AttrSessionRule
from melobot import AttrSessionRule as AttrRule
from melobot import (
    BotAction,
    MeloBot,
    Plugin,
    ResponseEvent,
    msg_args,
    msg_event,
    notice_event,
    send,
    send_reply,
)
from melobot.context.action import send_custom_msg, take_custom_action
from melobot.models.cq import image_msg, reply_msg, text_msg, to_cq_str, touch_msg
from melobot.types.tools import get_id

from ..env import BOT_INFO, PARSER_GEN, get_owner_checker, get_su_checker
from ..public_utils import base64_encode
from .core_debug import core_debug_process
from .session_test import session_test_process

bot = MeloBot.get(BOT_INFO.proj_name)

atest = Plugin.on_message(
    checker=get_su_checker(fail_cb=lambda: send_reply("你无权使用【异步测试】功能")),
    parser=PARSER_GEN.gen(target=["异步测试", "atest", "async-test"]),
)
test_n = Plugin.on_message(
    checker=get_su_checker(fail_cb=lambda: send_reply("你无权使用【测试统计】功能")),
    parser=PARSER_GEN.gen(target=["测试统计", "testn", "test-stat"]),
)
stest = Plugin.on_message(
    checker=get_su_checker(fail_cb=lambda: send_reply("你无权使用【会话测试】功能")),
    session_rule=AttrRule("sender", "id"),
    direct_rouse=True,
    conflict_cb=lambda: send("其他的 session 测试进行中...稍后再试"),
    parser=PARSER_GEN.gen(target=["会话测试", "stest", "session-test"]),
)
io_debug = Plugin.on_message(
    checker=get_su_checker(fail_cb=lambda: send_reply("你无权使用【io 调试】功能")),
    parser=PARSER_GEN.gen(
        target=["io调试", "io-debug"],
        formatters=[
            Format(
                convert=lambda x: bool(int(x)),
                src_desc="开关值",
                src_expect="1 或 0",
            )
        ],
    ),
)
core_debug_handle = Plugin.on_message(
    checker=get_owner_checker(fail_cb=lambda: send_reply("你无权使用【核心调试】功能")),
    parser=PARSER_GEN.gen(target=["核心调试", "core-debug"]),
    session_rule=AttrSessionRule("sender", "id"),
    direct_rouse=True,
    conflict_cb=lambda: send("已进入核心调试状态， 拒绝重复进入该状态"),
)
echo = Plugin.on_message(
    checker=get_su_checker(fail_cb=lambda: send_reply("你无权使用【复读】功能")),
    parser=PARSER_GEN.gen(
        target=["复读", "echo"],
        formatters=[
            Format(
                verify=lambda x: len(x) <= 100,
                src_desc="复读的内容",
                src_expect="字符数 <= 100",
                default="Hello World!",
            )
        ],
    ),
)
poke = Plugin.on_notice(type="poke")


class TestUtils(Plugin):
    def __init__(self) -> None:
        super().__init__()
        self.async_t = (1, 6)
        self.session_simulate_t = 1
        self.session_overtime_t = 10
        self.test_cnt = 0
        self.bot_id = bot.get_share("BaseUtils", "bot_id")
        self.io_debug_flag = False

    @atest
    async def async_test(self) -> None:
        sec = randint(*self.async_t)
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
        self.test_cnt += 1

    @stest
    async def sessoin_test(self) -> None:
        await session_test_process(self.session_simulate_t, self.session_overtime_t)
        self.test_cnt += 1

    @test_n
    async def test_stat(self) -> None:
        await send(f"已进行的测试次数：{self.test_cnt}")

    @echo
    async def echo(self) -> None:
        output_cq = to_cq_str(msg_event().content)[6:]
        await send(output_cq, cq_str=True)

    @io_debug
    async def io_debug(self) -> None:
        status = msg_args().pop(0)
        self.io_debug_flag = status

    @bot.on_action_presend()
    async def _io_debug(self, action: BotAction) -> None:
        if action.flag_check("TestUtils", "io-debug"):
            return
        if not self.io_debug_flag:
            return
        if action.trigger is None or "message" not in action.params.keys():
            return

        e_str = json.dumps(action.trigger.raw, ensure_ascii=False, indent=2)
        a_str = action.flatten(indent=2)
        debug_action = action.copy()
        output = f"event:\n{e_str}\n\naction:\n{a_str}"
        if len(output) <= 10000:
            data = await bot.emit_signal(
                "BaseUtils", "txt2img", output, 50, 16, wait=True
            )
            data = base64_encode(data)
            debug_action.params["message"] = [image_msg(data)]
        else:
            debug_action.params["message"] = [text_msg("[调试输出过长，请使用调试器]")]
        debug_action.resp_id = None
        debug_action.mark("TestUtils", "io-debug")
        await take_custom_action(debug_action)

    @core_debug_handle
    async def _core_debug(self) -> None:
        await core_debug_process()

    @poke
    async def poke(self) -> None:
        event = notice_event()
        if event.notice_user_id != self.bot_id.val:
            return
        poke_qid = event.notice_operator_id
        await send_custom_msg(
            touch_msg(poke_qid),
            not event.is_group(),
            event.notice_operator_id,
            event.notice_group_id if event.is_group() else None,
        )
