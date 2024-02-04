import time
import subprocess
import signal
import psutil
import asyncio as aio
from typing import Tuple, Union, List

from melobot import Plugin, bot, BotLife, session
from melobot import ArgFormatter as Format, AttrSessionRule as AttrRule, CmdParser
from melobot import send, finish, get_metainfo

from ..env import OWNER_CHECKER


shell = Plugin.on_message(checker=OWNER_CHECKER,
                          session_rule=AttrRule('sender', 'id'),
                          direct_rouse=True,
                          conflict_callback=send("已在运行交互式 shell"),
                          parser=CmdParser(cmd_start='*',
                                           cmd_sep='$$',
                                           target=["shell"], 
                                           formatters=[
                                               Format(src_desc="命令内容",
                                                      src_expect="字符串",
                                                      default=None)
                                           ]))


class ShellManager(Plugin):
    def __init__(self) -> None:
        super().__init__()
        self.shell: aio.subprocess.Process = None
        self.executable = "powershell" if get_metainfo().PLATFORM == 'win32' else "sh"
        self.encoding = 'utf-8' if get_metainfo().PLATFORM != 'win32' else 'gbk'
        self.int_signal = signal.SIGINT if get_metainfo().PLATFORM != 'win32' else signal.CTRL_C_EVENT
        self.line_sep = get_metainfo().LINE_SEP
        self.pointer: Tuple[int, bool, Union[int, None]] = None
        self.tasks: List[aio.Task] = None

        self._buf = []
        self._cache_time = 0.3

    @bot.on(BotLife.LOADED)
    async def open_shell(self) -> None:
        self.shell = await aio.create_subprocess_exec(self.executable, shell=False, stdin=subprocess.PIPE, 
                                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=str(self.ROOT))
        self.tasks = [
            aio.create_task(self.output_watch(self.shell.stdout)),
            aio.create_task(self.output_watch(self.shell.stderr)),
            aio.create_task(self.buf_monitor())
        ]
        ShellManager.LOGGER.info("IShell 服务已开启")

    @bot.on(BotLife.BEFORE_STOP)
    async def close_shell(self) -> None:
        for t in self.tasks:
            t.cancel()
        self.shell.terminate()
        await self.shell.wait()
        ShellManager.LOGGER.info("Ishell 服务已正常关闭")
    
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
                    ShellManager.LOGGER.warning(f"IShell 输出转发遇到问题，警告：{e}")
        except aio.CancelledError:
            pass
    
    def intput_send(self, s: str) -> None:
        self.shell.stdin.write(f'{s}\n'.encode(self.encoding))

    async def buf_monitor(self) -> None:
        try:
            while True:
                if len(self._buf) == 0:
                    pass
                elif abs(self._buf[-1][0] - time.time()) <= self._cache_time:
                    pass
                else:
                    s = '\n'.join([t[1] for t in self._buf])
                    self._buf.clear()
                    if s == '':
                        continue
                    if self.pointer:
                        p = self.pointer
                        await session.custom_send(s, p[1], p[0], p[2])
                await aio.sleep(0.2)
        except aio.CancelledError:
            pass
        except Exception as e:
            ShellManager.LOGGER.error(f"IShell 缓存异常，错误：{e}")

    def kill_childs(self) -> None:
        p = psutil.Process(self.shell.pid)
        children = p.children()
        for child in children:
            child.terminate()

    async def execute(self, text: str) -> None:
        match text:
            case "$ctrlc$":
                self.kill_childs()
            case "$exit$":
                self.pointer = None
                await finish("shell 交互模式已关闭")
            case "$\\n$":
                self.intput_send('\n')
            case _:
                self.intput_send(text)

    @shell
    async def run_in_shell(self) -> None:
        cmd = session.args.vals.pop(0)
        if cmd is None:
            self.pointer = (session.event.sender.id,
                            session.event.is_private(),
                            session.event.group_id)
            await send("已进入交互 shell。\n使用 $\\n$ 发送一个回车\n使用 $ctrlc$ 结束其内部程序执行\n使用 $exit$ 退出交互状态")
            while True:
                await session.suspend()
                await self.execute(session.event.text)
        else:
            p = await aio.create_subprocess_shell(cmd, stderr=aio.subprocess.PIPE, stdout=aio.subprocess.PIPE, cwd=str(self.ROOT))
            out, err = await p.communicate()
            if err == b'':
                output = out.decode(encoding=self.encoding).strip(self.line_sep)
            else:
                output = err.decode(encoding=self.encoding).strip(self.line_sep)
            await send(output)
