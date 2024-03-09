import asyncio as aio
import subprocess
import time
from typing import List, Optional, Tuple

import psutil

from melobot import ArgFormatter as Format
from melobot import AttrSessionRule as AttrRule
from melobot import (
    CmdParser,
    MetaInfo,
    Plugin,
    PluginBus,
    bot,
    finish,
    image_msg,
    msg_args,
    msg_event,
    msg_text,
    pause,
    send,
    send_custom_msg,
    send_reply,
)
from melobot.models import CQMsgDict
from melobot.types.exceptions import BotException

from ..env import get_owner_checker
from ..public_utils import base64_encode

META_INFO = MetaInfo()
shell = Plugin.on_message(
    checker=get_owner_checker(fail_cb=lambda: send_reply("你无权使用【命令行】功能")),
    session_rule=AttrRule("sender", "id"),
    direct_rouse=True,
    conflict_cb=lambda: send("已在运行交互式 shell"),
    parser=CmdParser(
        cmd_start="*",
        cmd_sep="$$",
        target="shell",
        formatters=[Format(src_desc="命令内容", src_expect="字符串", default=None)],
    ),
)


class ShellManager(Plugin):
    def __init__(self) -> None:
        super().__init__()
        self.shell: aio.subprocess.Process
        self.executable = "powershell" if META_INFO.PLATFORM == "win32" else "sh"
        self.encoding = "utf-8" if META_INFO.PLATFORM != "win32" else "gbk"
        self.line_sep = META_INFO.LINE_SEP
        self.pointer: Optional[Tuple[int, bool, Optional[int]]] = None
        self.tasks: List[aio.Task]
        self.stdin: aio.StreamWriter
        self.stdout: aio.StreamReader
        self.stderr: aio.StreamReader

        self._buf: list[tuple[float, str]] = []
        self._cache_time = 0.3

    @bot.on_all_loaded()
    async def open_shell(self) -> None:
        self.shell = await aio.create_subprocess_exec(
            self.executable,
            shell=False,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=str(self.PATH),
        )
        if (
            self.shell.stdout is None
            or self.shell.stderr is None
            or self.shell.stdin is None
        ):
            raise BotException("IShell 进程输入输出异常")
        self.stdin = self.shell.stdin
        self.stdout = self.shell.stdout
        self.stderr = self.shell.stderr
        self.tasks = [
            aio.create_task(self.output_watch(self.stdout)),
            aio.create_task(self.output_watch(self.stderr)),
            aio.create_task(self.buf_monitor()),
        ]
        self.LOGGER.info("IShell 服务已开启")

    @bot.on_before_stop()
    async def close_shell(self) -> None:
        for t in self.tasks:
            t.cancel()
        self.shell.terminate()
        await self.shell.wait()
        self.LOGGER.info("Ishell 服务已正常关闭")

    async def output_watch(self, stream: aio.StreamReader) -> None:
        try:
            while True:
                try:
                    stream_bytes = await stream.readline()
                    output = stream_bytes.decode(self.encoding).rstrip(self.line_sep)
                    if not output:
                        await aio.sleep(0.1)
                        continue
                    else:
                        if self.pointer:
                            self._buf.append((time.time(), output))
                except Exception as e:
                    self.LOGGER.warning(f"IShell 输出转发遇到问题，警告：{e}")
        except aio.CancelledError:
            pass

    def intput_send(self, s: str) -> None:
        self.stdin.write(f"{s}\n".encode(self.encoding))

    async def buf_monitor(self) -> None:
        try:
            while True:
                if len(self._buf) == 0:
                    pass
                elif abs(self._buf[-1][0] - time.time()) <= self._cache_time:
                    pass
                else:
                    s = "\n".join([t[1] for t in self._buf])
                    self._buf.clear()
                    if s == "":
                        continue
                    if self.pointer:
                        p = self.pointer
                        msg: str | CQMsgDict
                        if len(s) > 200:
                            data = await PluginBus.emit(
                                "BaseUtils", "txt2img", s, wait=True
                            )
                            b64_data = base64_encode(data)
                            msg = image_msg(b64_data)
                        else:
                            msg = s
                        await send_custom_msg(msg, p[1], p[0], p[2])
                await aio.sleep(0.2)
        except aio.CancelledError:
            pass
        except Exception as e:
            self.LOGGER.error(f"IShell 缓存异常，错误：{e}")

    def kill_childs(self) -> None:
        p = psutil.Process(self.shell.pid)
        children = p.children()
        for child in children:
            child.terminate()

    async def execute(self, text: str) -> None:
        match text:
            case "$cc$":
                self.kill_childs()
            case "$e$":
                self.pointer = None
                await finish("shell 交互模式已关闭")
            case "$\\n$":
                self.intput_send("\n")
            case _:
                self.intput_send(text)

    @shell
    async def run_in_shell(self) -> None:
        cmd = msg_args().pop(0)
        if cmd is None:
            event = msg_event()
            self.pointer = (
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
                await self.execute(msg_text())
        else:
            p = await aio.create_subprocess_shell(
                cmd,
                stderr=aio.subprocess.PIPE,
                stdout=aio.subprocess.PIPE,
                cwd=str(self.PATH),
            )
            out, err = await p.communicate()
            if err == b"":
                output = out.decode(encoding=self.encoding).strip(self.line_sep)
            else:
                output = err.decode(encoding=self.encoding).strip(self.line_sep)
            await send(output)
