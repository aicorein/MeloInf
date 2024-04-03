from melobot import BotPlugin
from melobot import CmdArgFormatter as Format
from melobot import CmdParser, msg_args, send_reply, thisbot

from ..env import COMMON_CHECKER

plugin = BotPlugin("Calculator", version="1.0.0")

calc = plugin.on_message(
    checker=COMMON_CHECKER,
    parser=CmdParser(
        cmd_start=["~", "～"],
        cmd_sep=" ",
        target=["计算", "calc"],
        formatters=[
            Format(
                verify=lambda x: len(x) <= 50,
                src_desc="用于计算的表达式",
                src_expect="表达式字符数 <= 50",
            )
        ],
    ),
)


@calc
async def calc() -> None:
    expression = msg_args().pop(0)
    output = await thisbot.emit_signal(
        "CodeCompiler", "do_calc", expression, 15, "py3", wait=True
    )
    await send_reply(output)
