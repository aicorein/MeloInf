from melobot import ArgFormatter as Format
from melobot import CmdParser, Plugin, PluginBus, send_reply, session

from ..env import COMMON_CHECKER

calc = Plugin.on_msg(
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


class Calculator(Plugin):
    def __init__(self) -> None:
        super().__init__()

    @calc
    async def calc(self) -> None:
        expression = session.args.vals.pop(0)
        output = await PluginBus.emit(
            "CodeCompiler", "do_calc", expression, 15, "py3", wait=True, forward=True
        )
        await send_reply(output)
