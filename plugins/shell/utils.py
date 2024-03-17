import asyncio as aio
import subprocess
import time

import psutil

from melobot import thisbot
from melobot.context.action import send_custom_msg
from melobot.models.cq import CQMsgDict, image_msg
from melobot.types.exceptions import BotException

from ..public_utils import base64_encode
from ._iface import PluginSpace as Space
from ._iface import plugin


@plugin.on_plugins_loaded
async def _open_shell() -> None:
    Space.shell = await aio.create_subprocess_exec(
        Space.executable,
        shell=False,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=Space.cwd,
    )
    if (
        Space.shell.stdout is None
        or Space.shell.stderr is None
        or Space.shell.stdin is None
    ):
        raise BotException("IShell 进程输入输出异常")
    Space.stdin = Space.shell.stdin
    Space.stdout = Space.shell.stdout
    Space.stderr = Space.shell.stderr
    Space.tasks = [
        aio.create_task(_output_watch(Space.stdout)),
        aio.create_task(_output_watch(Space.stderr)),
        aio.create_task(_buf_monitor()),
    ]
    thisbot.logger.info("IShell 服务已开启")


@plugin.on_before_stop
async def _close_shell() -> None:
    for t in Space.tasks:
        t.cancel()
    if Space.shell.returncode is None:
        Space.shell.terminate()
        await Space.shell.wait()
    thisbot.logger.info("Ishell 服务已关闭")


async def _output_watch(stream: aio.StreamReader) -> None:
    try:
        while True:
            try:
                stream_bytes = await stream.readline()
                output = stream_bytes.decode(Space.encoding).rstrip(Space.line_sep)
                if not output:
                    await aio.sleep(0.1)
                    continue
                else:
                    if Space.pointer:
                        Space._buf.append((time.time(), output))
            except Exception as e:
                thisbot.logger.warning(f"IShell 输出转发遇到问题，警告：{e}")
    except aio.CancelledError:
        pass
    except KeyboardInterrupt:
        pass


def intput_send(s: str) -> None:
    Space.stdin.write(f"{s}\n".encode(Space.encoding))


async def _buf_monitor() -> None:
    try:
        while True:
            if len(Space._buf) == 0:
                pass
            elif abs(Space._buf[-1][0] - time.time()) <= Space._cache_time:
                pass
            else:
                s = "\n".join([t[1] for t in Space._buf])
                Space._buf.clear()
                if s == "":
                    continue
                if Space.pointer:
                    p = Space.pointer
                    msg: str | CQMsgDict
                    if len(s) > 200:
                        data = await thisbot.emit_signal(
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
        thisbot.logger.error(f"IShell 缓存异常，错误：{e}")


def kill_childs() -> None:
    p = psutil.Process(Space.shell.pid)
    children = p.children()
    for child in children:
        child.terminate()
