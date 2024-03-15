from melobot import ArgFormatter as Format
from melobot import CmdParser, MeloBot, Plugin, msg_args, send_reply

from ..env import BOT_INFO

bot = MeloBot.get(BOT_INFO.proj_name)

from ..env import COMMON_CHECKER

calc = Plugin.on_message(
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
        expression = msg_args().pop(0)
        output = await bot.emit_signal(
            "CodeCompiler", "do_calc", expression, 15, "py3", wait=True
        )
        await send_reply(output)
