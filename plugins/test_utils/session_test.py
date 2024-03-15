import asyncio as aio
from typing import cast

from melobot import (
    MessageEvent,
    ResponseEvent,
    finish,
    msg_event,
    msg_text,
    send,
    send_wait,
    session,
)
from melobot.models.cq import reply_msg, text_msg
from melobot.types.exceptions import SessionHupTimeout


def set_event_records() -> None:
    session.store_add("EVENTS", [])


def get_event_records() -> list[MessageEvent]:
    return session.store_get("EVENTS")


def append_event_records() -> None:
    get_event_records().append(msg_event())


async def session_test_process(simulate_t: float, overtime_t: float):
    cnt = 0
    overtime = False
    qid = msg_event().sender.id
    resp = await send(
        f"会话测试开始。识别标记：{qid}，模拟间隔：{simulate_t}s。输入 stop 可停止本次会话测试",
        wait=True,
    )
    resp = cast(ResponseEvent, resp)
    start_msg_id = resp.data["message_id"]

    set_event_records()
    append_event_records()
    await send_wait(f"是否启用时长为 {overtime_t}s 的会话超时功能？（y/n）")
    append_event_records()
    if msg_text() == "y":
        overtime = True
    cnt += 1

    while True:
        if "stop" in msg_text():
            break
        cnt += 1
        await aio.sleep(simulate_t)
        try:
            eid_list_s = f"[{', '.join(['0x%x' %id(e) for e in get_event_records()])}]"
            if overtime:
                await send_wait(
                    f"第 {cnt} 次进入会话：\n事件 id 列表：{eid_list_s}",
                    overtime=overtime_t,
                )
            else:
                await send_wait(f"第 {cnt} 次进入会话：\n事件 id 列表：{eid_list_s}")
            append_event_records()
        except SessionHupTimeout:
            await send([reply_msg(start_msg_id), text_msg(f"session 挂起等待超时")])
            break
    await send([reply_msg(start_msg_id), text_msg(f"√ 标记为 {qid} 会话测试结束")])
