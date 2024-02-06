from melobot import Plugin, session
from melobot import PluginStore as Store
from melobot import send
from random import random, choice
from typing import List, Union

from ..env import COMMON_CHECKER, BOT_INFO, PASER_GEN
from ..public_utils import remove_punctuation
from .dict_build import WORD_DICT, BOT_FLAG, SENDER_FLAG, OWNER_FLAG


make_reply = Plugin.on_any_message(checker=COMMON_CHECKER)
words_info = Plugin.on_message(checker=COMMON_CHECKER,
                               parser=PASER_GEN.gen(["w-info", "词库信息"]))


class WordLibLoader(Plugin):
    def __init__(self) -> None:
        super().__init__()
        self.bot_id = Store.get('BaseUtils', 'bot_id')
        self.reply_prob = 0.9

    def get_keys(self) -> List[str]:
        text = session.event.text.replace('\n', '').strip(' ')
        text = remove_punctuation(text)
        for item in session.event.content:
            if item['type'] == 'at' and int(item['data']['qq']) == self.bot_id.val:
                keys = []
                keys.append(f"{BOT_FLAG}{text}")
                keys.append(f"{text}{BOT_FLAG}")
                return keys
        return [text]
    
    def get_random_reply(self, keys: List[str]) -> Union[str, None]:
        if random() <= self.reply_prob:
            res: List[str] = []
            for k in keys:
                v = WORD_DICT.get(k)
                if v:
                    res.extend(v)
            output = choice(res) if len(res) > 0 else ''
            if SENDER_FLAG in output:
                output = output.replace(SENDER_FLAG, f'[CQ:at,qq={session.event.sender.id}]')
            if OWNER_FLAG in output:
                output = output.replace(OWNER_FLAG, f'[CQ:at,qq={BOT_INFO.owner}]')
            return output if len(output) > 0 else None
        return None

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
