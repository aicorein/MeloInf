import asyncio as aio
from typing import List, Optional, Tuple

from melobot import AttrSessionRule as AttrRule
from melobot import BotPlugin
from melobot import CmdArgFormatter as Format
from melobot import CmdParser, MetaInfo, send, send_reply, this_dir

from ..env import get_owner_checker

plugin = BotPlugin("ShellManager", version="1.3.0")


class PluginSpace:
    cwd = this_dir()
    meta_info = MetaInfo
    shell: aio.subprocess.Process
    executable = "powershell" if meta_info.PLATFORM == "win32" else "sh"
    encoding = "utf-8" if meta_info.PLATFORM != "win32" else "gbk"
    line_sep = meta_info.LINE_SEP
    pointer: Optional[Tuple[int, bool, Optional[int]]] = None
    tasks: List[aio.Task]
    stdin: aio.StreamWriter
    stdout: aio.StreamReader
    stderr: aio.StreamReader

    _buf: list[tuple[float, str]] = []
    _cache_time = 0.3


shell = plugin.on_message(
    checker=get_owner_checker(fail_cb=lambda: send_reply("你无权使用【命令行】功能")),
    session_rule=AttrRule("sender", "id"),
    direct_rouse=True,
    conflict_cb=lambda: send("已在运行交互式 shell"),
    parser=CmdParser(
        cmd_start="*",
        cmd_sep="$$",
        targets="shell",
        formatters=[Format(src_desc="命令内容", src_expect="字符串", default=None)],
    ),
)
