import asyncio as aio

from melobot import finish, msg_args, msg_event, msg_text, pause, send

from ._iface import PluginSpace as Space
from ._iface import shell
from .utils import intput_send, kill_childs


async def execute(text: str) -> None:
    match text:
        case "$cc$":
            kill_childs()
        case "$e$":
            Space.pointer = None
            await finish("shell 交互模式已关闭")
        case "$\\n$":
            intput_send("\n")
        case _:
            intput_send(text)


@shell
async def run_in_shell() -> None:
    cmd = msg_args().pop(0)
    if cmd is None:
        event = msg_event()
        Space.pointer = (
            event.sender.id,
            event.is_private(),
            event.group_id,
        )
        tip = (
            "已进入交互 shell。\n"
            + "使用 $\\n$ 发送一个回车\n"
            + "使用 $cc$ 结束其内部程序执行\n"
            + "使用 $e$ 退出交互状态"
        )
        await send(tip)
        while True:
            await pause()
            await execute(msg_text())
    else:
        p = await aio.create_subprocess_shell(
            cmd,
            stderr=aio.subprocess.PIPE,
            stdout=aio.subprocess.PIPE,
            cwd=Space.cwd,
        )
        out, err = await p.communicate()
        if err == b"":
            output = out.decode(encoding=Space.encoding).strip(Space.line_sep)
        else:
            output = err.decode(encoding=Space.encoding).strip(Space.line_sep)
        await send(output)
