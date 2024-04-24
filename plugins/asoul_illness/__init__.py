import json
from random import choice
from typing import Dict, List

from melobot import BotPlugin
from melobot import CmdArgFormatter as Format
from melobot import msg_args, send, this_dir

from ..env import COMMON_CHECKER, PARSER_FACTORY

plugin = BotPlugin("AsoulIllness", version="1.0.0")

be_ill = plugin.on_message(
    checker=COMMON_CHECKER,
    parser=PARSER_FACTORY.get(
        targets=["发病", "ill"],
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
with open(data_path, encoding="utf-8") as fp:
    data: List[Dict[str, str]] = json.load(fp)


@be_ill
async def be_ill() -> None:
    target = msg_args()[0]
    text_pair = choice(data)
    text, person = text_pair["text"], text_pair["person"]
    text = text.replace(person, target)
    await send(text, cq_str=True)
