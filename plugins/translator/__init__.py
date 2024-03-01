from melobot import ArgFormatter as Format
from melobot import CmdParser, Plugin, send_reply, session

from ..env import COMMON_CHECKER
from .utils import get_translated_text

translate = Plugin.on_msg(
    checker=COMMON_CHECKER,
    parser=CmdParser(
        cmd_start="*",
        cmd_sep="#",
        target=["translate", "翻译"],
        formatters=[
            Format(
                verify=lambda x: len(x) <= 300,
                src_desc="要翻译的文本",
                src_expect="字符数 <= 300",
            ),
            Format(
                verify=lambda x: x in ["en", "zh", "jp"],
                src_desc="翻译目标语种",
                src_expect="值为 ['en', 'zh', 'jp'] 其中之一",
                default="zh",
            ),
        ],
    ),
)


class Translator(Plugin):
    def __init__(self) -> None:
        super().__init__()

    @translate
    async def translate(self) -> None:
        text, target = session.args
        _from, to, translated = await get_translated_text(text, target)
        output = "【模式 {} -> {}】\n{}".format(_from, to, translated)
        await send_reply(output)
