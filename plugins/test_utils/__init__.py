import asyncio as aio
from random import randint
from melobot import AttrSessionRule as AttrRule, User
from melobot import Plugin, finish, get_id, send, send_hup, session
from melobot import reply_msg, text_msg
from melobot import BotHupTimeout
from ..env import ADMIN_CHECKER, PASER_GEN

atest = Plugin.on_message(
    parser=PASER_GEN.gen(["异步测试", "atest", "async-test"]),
    checker=ADMIN_CHECKER
)
stest = Plugin.on_message(
    parser=PASER_GEN.gen(["会话测试", "stest", "session-test"]),
    checker=ADMIN_CHECKER,
    session_rule=AttrRule("sender", "id"),
    direct_rouse=True,
    conflict_callback=send("其他的 session 测试进行中...稍后再试")
)
test_n = Plugin.on_message(
    parser=PASER_GEN.gen(["测试统计", "test_n"]),
    checker=ADMIN_CHECKER
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
        await send([
            reply_msg(resp.data['message_id']),
            text_msg(f"√ 标记为 {id} 的异步测试完成")
        ])
        self.test_cnt += 1

    @stest
    async def sessoin_test(self) -> None:
        await aio.sleep(self.session_t)
        cnt = 0
        overtime = False
        id = session.event.sender.id
        resp = await send(f"会话测试开始。识别标记：{id}，模拟间隔：{self.session_t}s。输入 stop 可停止本次会话测试", wait=True)
        start_msg_id = resp.data['message_id']
        await send_hup(f"是否启用时长为 {self.session_overtime_t}s 的超时测试功能？（y/n）")
        if session.event.text == 'y':
            overtime = True

        while True:
            if "stop" in session.event.text: 
                break
            cnt += 1
            await aio.sleep(self.session_t)
            try:
                if overtime:
                    await send_hup(f"第 {cnt} 次进入会话：\n事件列表：{session.events}\n", overtime=self.session_overtime_t)
                else:
                    await send_hup(f"第 {cnt} 次进入会话：\n事件列表：{session.events}\n")
            except BotHupTimeout:
                self.test_cnt += 1
                await finish([
                    reply_msg(start_msg_id),
                    text_msg(f"session 挂起等待超时，√ 标记为 {id} 会话测试结束")
                ])
        self.test_cnt += 1
        await finish([
            reply_msg(start_msg_id),
            text_msg(f"√ 标记为 {id} 会话测试结束")
        ])

    @test_n
    async def test_stat(self) -> None:
        await send(f"已进行的测试次数：{self.test_cnt}")
