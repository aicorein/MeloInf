import asyncio as aio
import importlib
import json
from random import randint

from melobot import ArgFormatter as Format
from melobot import AttrSessionRule
from melobot import AttrSessionRule as AttrRule
from melobot import (
    BotLife,
    Plugin,
    PluginBus,
    PluginStore,
    bot,
    finish,
    get_id,
    msg_event,
    msg_text,
    notice_event,
    send,
    send_hup,
    send_reply,
    session,
)
from melobot.models import BotAction, image_msg, reply_msg, text_msg, touch_msg
from melobot.types import SessionHupTimeout
from melobot.types.typing import AsyncFunc

from ..env import OWNER_CHECKER, PARSER_GEN, SU_CHECKER
from ..public_utils import base64_encode

atest = Plugin.on_message(
    checker=SU_CHECKER,
    parser=PARSER_GEN.gen(target=["异步测试", "atest", "async-test"]),
)
test_n = Plugin.on_message(
    checker=SU_CHECKER, parser=PARSER_GEN.gen(target=["测试统计", "testn", "test-stat"])
)
stest = Plugin.on_message(
    checker=SU_CHECKER,
    session_rule=AttrRule("sender", "id"),
    direct_rouse=True,
    conflict_cb=lambda: send("其他的 session 测试进行中...稍后再试"),
    parser=PARSER_GEN.gen(target=["会话测试", "stest", "session-test"]),
)
io_debug = Plugin.on_message(
    checker=SU_CHECKER,
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
core_debug = Plugin.on_message(
    checker=OWNER_CHECKER,
    parser=PARSER_GEN.gen(target=["核心调试", "core-debug"]),
    session_rule=AttrSessionRule("sender", "id"),
    direct_rouse=True,
    conflict_cb=lambda: send("已进入核心调试状态， 拒绝重复进入该状态"),
)
echo = Plugin.on_message(
    checker=SU_CHECKER,
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
        self.session_simulate_t = 1.5
        self.session_overtime_t = 10
        self.test_cnt = 0
        self.bot_id = PluginStore.get("BaseUtils", "bot_id")
        self.io_debug_flag = False

    @atest
    async def async_test(self) -> None:
        sec = randint(*self.async_t)
        id = str(get_id())[-6:]
        resp = await send(f"异步测试开始。时长：{sec}s，识别标记：{id}", wait=True)
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
        await aio.sleep(self.session_simulate_t)
        cnt = 0
        overtime = False
        qid = msg_event().sender.id
        resp = await send(
            f"会话测试开始。识别标记：{qid}，模拟间隔：{self.session_simulate_t}s。输入 stop 可停止本次会话测试",
            wait=True,
        )
        start_msg_id = resp.data["message_id"]
        await send_hup(
            f"是否启用时长为 {self.session_overtime_t}s 的会话超时功能？（y/n）"
        )
        if msg_text() == "y":
            overtime = True
        cnt += 1

        while True:
            if "stop" in msg_text():
                break
            cnt += 1
            await aio.sleep(self.session_simulate_t)
            try:
                eid_list_s = f"[{', '.join(['0x%x' %id(e) for e in session.events])}]"
                if overtime:
                    await send_hup(
                        f"第 {cnt} 次进入会话：\n事件 id 列表：{eid_list_s}\n",
                        overtime=self.session_overtime_t,
                    )
                else:
                    await send_hup(
                        f"第 {cnt} 次进入会话：\n事件 id 列表：{eid_list_s}\n"
                    )
            except SessionHupTimeout:
                self.test_cnt += 1
                await finish(
                    [
                        reply_msg(start_msg_id),
                        text_msg(f"session 挂起等待超时，√ 标记为 {qid} 会话测试结束"),
                    ]
                )
        self.test_cnt += 1
        await finish(
            [reply_msg(start_msg_id), text_msg(f"√ 标记为 {qid} 会话测试结束")]
        )

    @test_n
    async def test_stat(self) -> None:
        await send(f"已进行的测试次数：{self.test_cnt}")

    @echo
    async def echo(self) -> None:
        content = session.args.pop(0)
        await send(content, cq_str=True)

    @io_debug
    async def io_debug(self) -> None:
        status = session.args.pop(0)
        self.io_debug_flag = status

    @bot.on(BotLife.ACTION_PRESEND)
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
            data = await PluginBus.emit(
                "BaseUtils", "txt2img", output, 100, 16, wait=True
            )
            data = base64_encode(data)
            debug_action.params["message"] = [image_msg(data)]
        else:
            debug_action.params["message"] = [text_msg("[调试输出过长，请使用调试器]")]
        debug_action.resp_id = None
        debug_action.mark("TestUtils", "io-debug")
        await session.custom_action(debug_action)

    async def format_send(self, send_func: AsyncFunc[None], s: str) -> None:
        if len(s) <= 300:
            await send_func(s)
        elif len(s) > 10000:
            await send_func("<返回结果长度大于 10000，请使用调试器>")
        else:
            data = await PluginBus.emit("BaseUtils", "txt2img", s, 100, 16, wait=True)
            data = base64_encode(data)
            await send_func(image_msg(data))

    @core_debug
    async def core_debug(self) -> None:
        await send(
            "【你已进入核心调试状态】\n注意 ⚠️：对核心的错误修改可能导致崩溃，请谨慎操作！"
        )
        await send(
            "【输入求值表达式以查看值】\n例：bot.plugins['TestUtils']\n输入 $e$ 退出调试\n输入 $i$ 导入一个模块\n输入 $m$ 修改当前查看的值"
        )
        pointer = None
        imports = {}
        var_map = {"bot": bot.__origin__}
        while True:
            await session.hup()
            match msg_text():
                case "$e$":
                    await finish("已退出核心调试状态")
                case "$i$":
                    await send("【开始导入在调试时可用的模块】\n$e$ 退出导入操作")
                    await session.hup()
                    try:
                        text = msg_text()
                        if text == "$e$":
                            await send("已退出导入操作")
                            continue
                        module = importlib.import_module(text)
                        imports[text] = module
                        var_map.update(imports)
                        await send(f"{text} 导入完成 ✅")
                    except Exception as e:
                        await send(f"尝试导入模块时发生异常 ❌：{e.__str__()}")
                case "$m$":
                    if pointer is None:
                        await send("当前修改指向空对象，拒绝操作 ❌")
                        continue
                    else:
                        await send(
                            f"【输入修改后的值：】\n$e$ 退出修改操作\n当前指向对象：{pointer}"
                        )
                        await session.hup()
                        try:
                            text = msg_text()
                            if text == "$e$":
                                await send("已退出修改操作")
                                continue
                            exec(
                                f"{pointer}={msg_text()}",
                                var_map,
                            )
                            val = eval(f"{pointer}", var_map)
                            await self.format_send(
                                send, f"修改后的值为：{val}\n类型：{type(val)}"
                            )
                        except Exception as e:
                            await send(
                                f"尝试修改值并重新显示时发生异常 ❌：{e.__str__()}"
                            )
                case _:
                    try:
                        val = eval(f"{msg_text()}", var_map)
                        pointer = msg_text()
                        await self.format_send(send_reply, str(val))
                    except Exception as e:
                        await send(f"获取值时出现异常 ❌：{e.__str__()}")

    @poke
    async def poke(self) -> None:
        event = notice_event()
        if event.notice_user_id != self.bot_id.val:
            return
        poke_qid = event.notice_operator_id
        await session.custom_send(
            touch_msg(poke_qid),
            not event.is_group(),
            event.notice_operator_id,
            event.notice_group_id if event.is_group() else None,
            waitResp=True,
        )
