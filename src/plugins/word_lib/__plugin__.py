import re
from random import choice, random

from melobot import Plugin, get_bot, send_text
from melobot.protocols.onebot.v11 import Adapter, on_message
from melobot.protocols.onebot.v11.adapter.event import MessageEvent
from melobot.protocols.onebot.v11.handle import GetParseArgs
from melobot.protocols.onebot.v11.utils import CmdArgFormatter as Fmtter
from melobot.protocols.onebot.v11.utils import CmdParser, ParseArgs
from melobot.utils import lock

from ...env import ENVS
from ...platform.onebot import (
    COMMON_CHECKER,
    PARSER_FACTORY,
    FormatCb,
    get_white_checker,
)
from ...utils import ENG_PUNC, HANS_PUNC, remove_punctuation
from .. import base_utils as BASE_INFO
from .wdict import BOT_FLAG, OWNER_FLAG, SENDER_FLAG, WORD_DICT, add_pair

_fmt_err_cbs = {
    "convert_fail": FormatCb.convert_fail,
    "validate_fail": FormatCb.validate_fail,
    "arg_lack": FormatCb.arg_lack,
}
bot = get_bot()
OB_ADAPTER = bot.get_adapter(Adapter)
assert isinstance(OB_ADAPTER, Adapter)

SPECIAL_PROB = 0.001
BOT_NAME = ENVS.bot.bot_name
NICKNAMES = ENVS.bot.bot_nicknames
NICKNAME = NICKNAMES[-1]
OB_OWNER_NAME = ENVS.onebot.owner_names[0]
OB_OWNER_ID = ENVS.onebot.owner_id


class WordLib(Plugin):
    def __init__(self) -> None:
        super().__init__()
        self.version = "1.4.0"
        self.flows = (make_reply, get_wlib_info, wlib_teach)


@on_message(checker=COMMON_CHECKER)
async def make_reply(event: MessageEvent) -> None:
    keys = await get_keys(event)
    output = get_random_reply(event, keys)
    if len(output):
        await send_text(output)


@on_message(checker=COMMON_CHECKER, parser=PARSER_FACTORY.get(["wlib-info", "词库信息"]))
async def get_wlib_info() -> None:
    await send_text(f"● 当前加载词库文件：words.txt\n● 词条数：{len(WORD_DICT)}")


_wlib_teach_check = get_white_checker(
    fail_cb=lambda: OB_ADAPTER.send_reply("你无权使用【词条扩充】功能")
)


@on_message(
    checker=COMMON_CHECKER,
    parser=CmdParser(
        cmd_start="*",
        cmd_sep="##",
        targets=["wlib-teach", "词条扩充"],
        fmtters=[
            Fmtter(
                validate=lambda x: len(x) <= 20 and "##" not in x,
                src_desc="触发语句",
                src_expect="字符数 <= 20 且不包含 ## 符号",
                **_fmt_err_cbs,
            ),
            Fmtter(
                validate=lambda x: len(x) <= 200 and "##" not in x,
                src_desc="回复语句",
                src_expect="字符数 <= 200 且不包含 ## 符号",
                **_fmt_err_cbs,
            ),
        ],
    ),
)
async def wlib_teach(
    adapter: Adapter, event: MessageEvent, args: ParseArgs = GetParseArgs()
) -> None:
    if not (await _wlib_teach_check.check(event)):
        return
    await _teach_pair(adapter, args)


@lock(
    lambda: OB_ADAPTER.send_reply(f"{NICKNAME} 学不过来啦，等 {NICKNAME} 先学完上一句嘛~")
)
async def _teach_pair(adapter: Adapter, args: ParseArgs) -> None:
    ask, ans = args.vals
    punc = ENG_PUNC.replace("$", "") + HANS_PUNC
    ask = re.sub(rf"[{re.escape(punc)}]", "", ask)
    res = add_pair(ask, ans)

    if res:
        await adapter.send_reply(f"{NICKNAME} 学会啦！")
    else:
        await adapter.send_reply(f"这个 {NICKNAME} 已经会了哦~")


async def get_keys(event: MessageEvent) -> list[str]:
    text = event.text.replace("\n", "").strip(" ")
    text = remove_punctuation(text)
    text = re.sub(rf"({'|'.join(NICKNAMES)})", BOT_FLAG, text)

    for qid in event.get_datas("at", "qq"):
        if qid == (BASE_INFO.onebot_id):
            keys = []
            keys.append(f"{BOT_FLAG}{text}")
            keys.append(f"{text}{BOT_FLAG}")
            return keys
    return [text]


def get_random_reply(event: MessageEvent, keys: list[str]) -> str:
    res: list[str] = []
    for k in keys:
        v = WORD_DICT.get(k)
        if v:
            res.extend(v)
    output = choice(res) if len(res) > 0 else ""

    if BOT_FLAG in output:
        output = output.replace(BOT_FLAG, NICKNAME)

    if SENDER_FLAG in output:
        if event.is_private():
            sender_name = event.sender.nickname
        else:
            sender_name = (
                event.sender.card
                if event.sender.card not in ("", None)
                else event.sender.nickname
            )
        output = output.replace(SENDER_FLAG, sender_name)

    if OWNER_FLAG in output:
        output = output.replace(OWNER_FLAG, OB_OWNER_NAME)

    if output != "":
        if random() < SPECIAL_PROB:
            output = "[恭喜你触发了千分之一概率的隐藏回复]"
    return output
