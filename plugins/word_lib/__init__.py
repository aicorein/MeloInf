from random import choice, random
from typing import List

from melobot import BotPlugin
from melobot import CmdArgFormatter as Format
from melobot import (
    CmdParser,
    lock,
    msg_args,
    msg_event,
    msg_text,
    send,
    send_reply,
    thisbot,
)

from ..env import BOT_INFO, COMMON_CHECKER, PARSER_GEN, get_white_checker
from ..public_utils import remove_ask_punctuation, remove_punctuation
from .dict import BOT_FLAG, OWNER_FLAG, SENDER_FLAG, WORD_DICT, add_pair

plugin = BotPlugin("WordlibLoader", version="1.4.0")


class PluginSpace:
    special_prob = 0.001


class PluginRef:
    async def bot_id() -> int:
        return await thisbot.get_share("BaseUtils", "bot_id").val


make_reply = plugin.on_message(checker=COMMON_CHECKER)

words_info = plugin.on_message(
    checker=COMMON_CHECKER, parser=PARSER_GEN.gen(["w-info", "词库信息"])
)

teach = plugin.on_message(
    checker=get_white_checker(fail_cb=lambda: send_reply("你无权使用【词条扩充】功能")),
    parser=CmdParser(
        cmd_start="*",
        cmd_sep="##",
        target=["w-teach", "词条扩充"],
        formatters=[
            Format(
                verify=lambda x: len(x) <= 20 and "##" not in x,
                src_desc="触发语句",
                src_expect="字符数 <= 20 且不包含 ## 符号",
            ),
            Format(
                verify=lambda x: len(x) <= 200 and "##" not in x,
                src_desc="触发语句",
                src_expect="字符数 <= 200 且不包含 ## 符号",
            ),
        ],
    ),
)


async def get_keys() -> List[str]:
    text = msg_text().replace("\n", "").strip(" ")
    text = remove_punctuation(text)
    text = text.replace(BOT_INFO.bot_name, BOT_FLAG).replace(
        BOT_INFO.bot_nickname, BOT_FLAG
    )
    for qid in msg_event().get_datas("at", "qq"):
        if qid == (await PluginRef.bot_id()):
            keys = []
            keys.append(f"{BOT_FLAG}{text}")
            keys.append(f"{text}{BOT_FLAG}")
            return keys
    return [text]


def get_random_reply(keys: List[str]) -> str:
    res: List[str] = []
    for k in keys:
        v = WORD_DICT.get(k)
        if v:
            res.extend(v)
    output = choice(res) if len(res) > 0 else ""
    if BOT_FLAG in output:
        output = output.replace(BOT_FLAG, BOT_INFO.bot_nickname)
    if SENDER_FLAG in output:
        output = output.replace(SENDER_FLAG, f"[CQ:at,qq={msg_event().sender.id}] ")
    if OWNER_FLAG in output:
        output = output.replace(OWNER_FLAG, f"[CQ:at,qq={BOT_INFO.owner}] ")
    if output != "":
        if random() < PluginSpace.special_prob:
            output = "[恭喜你触发了这条千分之一概率的隐藏回复]"
    return output


@make_reply
async def make_reply() -> None:
    keys = await get_keys()
    output = get_random_reply(keys)
    if len(output):
        await send(output, cq_str=True)


@words_info
async def words_info() -> None:
    output = f"● 当前加载词库文件：words.txt\n● 词条数：{len(WORD_DICT)}"
    await send(output)


@teach
@lock(
    lambda: send(
        f"{BOT_INFO.bot_nickname} 学不过来啦，等 {BOT_INFO.bot_nickname} 先学完上一句嘛~"
    )
)
async def teach_pair() -> None:
    ask, ans = msg_args()
    ask = remove_ask_punctuation(ask)
    res = add_pair(ask, ans)
    if res:
        await send_reply(f"{BOT_INFO.bot_nickname} 学会啦！")
    else:
        await send_reply(f"这个 {BOT_INFO.bot_nickname} 已经会了哦~")
