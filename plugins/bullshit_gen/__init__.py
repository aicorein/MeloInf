import math
import random
import string

from melobot import ArgFormatter as Format
from melobot import Plugin, send, session

from ..env import COMMON_CHECKER, PARSER_GEN
from .gen import Generator

bullshit_gen = Plugin.on_message(
    checker=COMMON_CHECKER,
    parser=PARSER_GEN.gen(
        target=["狗屁不通生成", "bullshit"],
        formatters=[
            Format(
                verify=lambda x: len(x) <= 15,
                src_desc="文章主题",
                src_expect="字符数 <= 15",
            )
        ],
    ),
)
error_codes = Plugin.on_message(
    checker=COMMON_CHECKER, parser=PARSER_GEN.gen(target=["乱码生成", "ecode"])
)


class BullshitGen(Plugin):
    def __init__(self) -> None:
        super().__init__()
        self.length = 200
        self.punc = string.punctuation + r"。，、；：？！…—·ˉ¨‘’“”々～‖∶＂＇｀〃．"

    @bullshit_gen
    async def bullshit_gen(self) -> None:
        theme = session.args.pop(0)
        output = Generator(theme, self.length).generate()
        await send(output)

    @error_codes
    async def error_codes(self) -> None:
        _len = random.randint(50, 300)
        chars = [chr(random.randint(0x0021, 0x9FFF)) for i in range(_len)]
        chars.extend([random.choice(self.punc) for i in range(math.ceil(_len / 5))])
        random.shuffle(chars)
        output = "".join(chars)[:_len]
        await send(output)
