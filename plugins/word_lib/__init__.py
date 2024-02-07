import asyncio as aio
from melobot import Plugin, session, CmdParser
from melobot import PluginStore as Store, ArgFormatter as Format
from melobot import send, send_reply
from random import random, choice
from typing import List, Union

from ..env import COMMON_CHECKER, BOT_INFO, PASER_GEN, WHITE_CHECKER
from ..public_utils import remove_punctuation, remove_ask_punctuation
from .dict import WORD_DICT, BOT_FLAG, SENDER_FLAG, OWNER_FLAG, add_pair


make_reply = Plugin.on_any_message(checker=COMMON_CHECKER)
words_info = Plugin.on_message(checker=COMMON_CHECKER,
                               parser=PASER_GEN.gen(["w-info", "词库信息"]))
teach = Plugin.on_message(checker=WHITE_CHECKER,
                          parser=CmdParser(cmd_start='*', 
                                           cmd_sep='##', 
                                           target=["w-teach", "词条扩充"],
                                           formatters=[
                                               Format(verify=lambda x: len(x) <= 20 and '##' not in x,
                                                      src_desc="触发语句",
                                                      src_expect="字符数 <= 20 且不包含 ## 符号"),
                                               Format(verify=lambda x: len(x) <= 200 and '##' not in x,
                                                      src_desc="触发语句",
                                                      src_expect="字符数 <= 200 且不包含 ## 符号")
                                           ]))


class WordlibLoader(Plugin):
    def __init__(self) -> None:
        super().__init__()
        self.bot_id = Store.get('BaseUtils', 'bot_id')
        self.special_prob = 0.001
        self.teach_lock = aio.Lock()

    def get_keys(self) -> List[str]:
        text = session.event.text.replace('\n', '').strip(' ')
        text = remove_punctuation(text)
        text = text.replace(BOT_INFO.bot_name, BOT_FLAG).replace(BOT_INFO.bot_nickname, BOT_FLAG)
        for item in session.event.content:
            if item['type'] == 'at' and int(item['data']['qq']) == self.bot_id.val:
                keys = []
                keys.append(f"{BOT_FLAG}{text}")
                keys.append(f"{text}{BOT_FLAG}")
                return keys
        return [text]
    
    def get_random_reply(self, keys: List[str]) -> Union[str, None]:
        res: List[str] = []
        for k in keys:
            v = WORD_DICT.get(k)
            if v:
                res.extend(v)
        output = choice(res) if len(res) > 0 else ''
        if BOT_FLAG in output:
            output = output.replace(BOT_FLAG, BOT_INFO.bot_nickname)
        if SENDER_FLAG in output:
            output = output.replace(SENDER_FLAG, f'[CQ:at,qq={session.event.sender.id}] ')
        if OWNER_FLAG in output:
            output = output.replace(OWNER_FLAG, f'[CQ:at,qq={BOT_INFO.owner}] ')
        output = output if len(output) > 0 else None
        if output is not None:
            if random() < self.special_prob:
                output = "[恭喜你触发了这条 1% 概率的隐藏回复]"
        return output

    @make_reply
    async def make_reply(self) -> None:
        keys = self.get_keys()
        output = self.get_random_reply(keys)
        if output:
            await send(output, enable_cq_str=True)

    @words_info
    async def words_info(self) -> None:
        output = f'● 当前加载词库文件：words.txt\n● 词条数：{len(WORD_DICT)}'
        await send(output)

    @teach
    async def teach_pair(self) -> None:
        async with self.teach_lock:
            ask, ans = session.args.vals
            ask = remove_ask_punctuation(ask)
            res = add_pair(ask, ans)
            if res:
                await send_reply(f"{BOT_INFO.bot_nickname} 学会啦！")
            else:
                await send_reply(f"这个 {BOT_INFO.bot_nickname} 已经会了哦~")
