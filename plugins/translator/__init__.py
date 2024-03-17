from melobot import ArgFormatter as Format
from melobot import BotPlugin, CmdParser, msg_args, send_reply, thisbot, timelimit
from melobot.types.exceptions import BotException

from ..env import COMMON_CHECKER
from .utils import get_translated_text

plugin = BotPlugin("Translator", version="1.0.0")

translate = plugin.on_message(
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
                src_expect="值为 [en, zh, jp] 其中之一",
                default="zh",
            ),
        ],
    ),
)


@translate
@timelimit(lambda: send_reply("翻译结果获取超时，请稍候再试..."), timeout=25)
async def translate() -> None:
    text, target = msg_args()
    try:
        _from, to, translated = await get_translated_text(text, target)
        output = "【模式 {} -> {}】\n{}".format(_from, to, translated)
        await send_reply(output)
    except BotException as e:
        thisbot.logger.error(e.__str__())
