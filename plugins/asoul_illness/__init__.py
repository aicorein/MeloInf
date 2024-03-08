import json
from random import choice
from typing import Dict, List

from melobot import ArgFormatter as Format
from melobot import Plugin, msg_args, send, this_dir

from ..env import COMMON_CHECKER, PARSER_GEN

be_ill = Plugin.on_message(
    checker=COMMON_CHECKER,
    parser=PARSER_GEN.gen(
        target=["发病", "ill"],
        formatters=[
            Format(
                verify=lambda x: len(x) <= 20,
                src_desc="发病对象",
                src_expect="字符数 <= 20",
            )
        ],
    ),
)


data_path = this_dir("data.json")


class AsoulIllness(Plugin):
    def __init__(self) -> None:
        super().__init__()
        with open(data_path, encoding="utf-8") as fp:
            self.data: List[Dict[str, str]] = json.load(fp)

    @be_ill
    async def be_ill(self) -> None:
        target = msg_args().pop(0)
        text_pair = choice(self.data)
        text, person = text_pair["text"], text_pair["person"]
        text = text.replace(person, target)
        await send(text, cq_str=True)
