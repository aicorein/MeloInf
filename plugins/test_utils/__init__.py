import asyncio as aio
from random import randint

from melobot import ArgFormatter as Format
from melobot import AttrSessionRule as AttrRule
from melobot import (
    BotHupTimeout,
    Plugin,
    PluginStore,
    finish,
    get_id,
    reply_msg,
    send,
    send_hup,
    session,
    text_msg,
)

from ..env import PARSER_GEN, SU_CHECKER

atest = Plugin.on_msg(
    checker=SU_CHECKER,
    parser=PARSER_GEN.gen(target=["异步测试", "atest", "async-test"]),
)
test_n = Plugin.on_msg(
    checker=SU_CHECKER, parser=PARSER_GEN.gen(target=["测试统计", "testn", "test-stat"])
)
stest = Plugin.on_msg(
    checker=SU_CHECKER,
    session_rule=AttrRule("sender", "id"),
    direct_rouse=True,
    conflict_callback=send("其他的 session 测试进行中...稍后再试"),
    parser=PARSER_GEN.gen(target=["会话测试", "stest", "session-test"]),
)
debug = Plugin.on_msg(
    checker=SU_CHECKER,
    parser=PARSER_GEN.gen(
        target=["调试", "debug"],
        formatters=[
            Format(
                convert=lambda x: bool(int(x)),
                src_desc="开关值",
                src_expect="1 或 0",
            )
        ],
    ),
)
echo = Plugin.on_msg(
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


class TestUtils(Plugin):
    def __init__(self) -> None:
        super().__init__()
        self.async_t = (1, 6)
        self.session_t = 1.5
        self.session_overtime_t = 10
        self.test_cnt = 0

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
        await aio.sleep(self.session_t)
        cnt = 0
        overtime = False
        id = session.event.sender.id
        resp = await send(
            f"会话测试开始。识别标记：{id}，模拟间隔：{self.session_t}s。输入 stop 可停止本次会话测试",
            wait=True,
        )
        start_msg_id = resp.data["message_id"]
        await send_hup(
            f"是否启用时长为 {self.session_overtime_t}s 的会话超时功能？（y/n）"
        )
        if session.event.text == "y":
            overtime = True

        while True:
            if "stop" in session.event.text:
                break
            cnt += 1
            await aio.sleep(self.session_t)
            try:
                if overtime:
                    await send_hup(
                        f"第 {cnt} 次进入会话：\n事件列表：{session.events}\n",
                        overtime=self.session_overtime_t,
                    )
                else:
                    await send_hup(
                        f"第 {cnt} 次进入会话：\n事件列表：{session.events}\n"
                    )
            except BotHupTimeout:
                self.test_cnt += 1
                await finish(
                    [
                        reply_msg(start_msg_id),
                        text_msg(f"session 挂起等待超时，√ 标记为 {id} 会话测试结束"),
                    ]
                )
        self.test_cnt += 1
        await finish([reply_msg(start_msg_id), text_msg(f"√ 标记为 {id} 会话测试结束")])

    @test_n
    async def test_stat(self) -> None:
        await send(f"已进行的测试次数：{self.test_cnt}")

    @echo
    async def echo(self) -> None:
        content = session.args.pop(0)
        await send(content, enable_cq=True)

    @debug
    async def debug(self) -> None:
        status = session.args.pop(0)
        flag = PluginStore.get("BaseUtils", "debug_status")
        await flag.affect(status)
