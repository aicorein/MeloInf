from random import choice, random
from typing import List

from melobot import ArgFormatter as Format
from melobot import CmdParser, Plugin
from melobot import PluginStore as Store
from melobot import lock, msg_args, msg_event, msg_text, send, send_reply

from ..env import BOT_INFO, COMMON_CHECKER, PARSER_GEN, WHITE_CHECKER
from ..public_utils import remove_ask_punctuation, remove_punctuation
from .dict import BOT_FLAG, OWNER_FLAG, SENDER_FLAG, WORD_DICT, add_pair

make_reply = Plugin.on_every_message(checker=COMMON_CHECKER)
words_info = Plugin.on_message(
    checker=COMMON_CHECKER, parser=PARSER_GEN.gen(["w-info", "词库信息"])
)
teach = Plugin.on_message(
    checker=WHITE_CHECKER,
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


class WordlibLoader(Plugin):
    def __init__(self) -> None:
        super().__init__()
        self.bot_id = Store.get("BaseUtils", "bot_id")
        self.special_prob = 0.001

    def get_keys(self) -> List[str]:
        text = msg_text().replace("\n", "").strip(" ")
        text = remove_punctuation(text)
        text = text.replace(BOT_INFO.bot_name, BOT_FLAG).replace(
            BOT_INFO.bot_nickname, BOT_FLAG
        )
        for qid in msg_event().get_cq_params("at", "qq"):
            if qid == self.bot_id.val:
                keys = []
                keys.append(f"{BOT_FLAG}{text}")
                keys.append(f"{text}{BOT_FLAG}")
                return keys
        return [text]

    def get_random_reply(self, keys: List[str]) -> str:
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
            if random() < self.special_prob:
                output = "[恭喜你触发了这条千分之一概率的隐藏回复]"
        return output

    @make_reply
    async def make_reply(self) -> None:
        keys = self.get_keys()
        output = self.get_random_reply(keys)
        if len(output):
            await send(output, cq_str=True)

    @words_info
    async def words_info(self) -> None:
        output = f"● 当前加载词库文件：words.txt\n● 词条数：{len(WORD_DICT)}"
        await send(output)

    @teach
    @lock(
        lambda: send(
            f"{BOT_INFO.bot_nickname} 学不过来啦，等 {BOT_INFO.bot_nickname} 先学完上一句嘛~"
        )
    )
    async def teach_pair(self) -> None:
        ask, ans = msg_args()
        ask = remove_ask_punctuation(ask)
        res = add_pair(ask, ans)
        if res:
            await send_reply(f"{BOT_INFO.bot_nickname} 学会啦！")
        else:
            await send_reply(f"这个 {BOT_INFO.bot_nickname} 已经会了哦~")
