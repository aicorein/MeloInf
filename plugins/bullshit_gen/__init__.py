import math
import random
import string

from melobot import ArgFormatter as Format
from melobot import BotPlugin, msg_args, send

from ..env import COMMON_CHECKER, PARSER_GEN
from .gen import Generator

plugin = BotPlugin("BullshitGen", version="1.1.0")


class PluginSpace:
    gen_length = 200
    punc = string.punctuation + r"。，、；：？！…—·ˉ¨‘’“”々～‖∶＂＇｀〃．"


bullshit_gen = plugin.on_message(
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
error_codes = plugin.on_message(
    checker=COMMON_CHECKER, parser=PARSER_GEN.gen(target=["乱码生成", "ecode"])
)


@bullshit_gen
async def bullshit_gen() -> None:
    theme = msg_args().pop(0)
    output = Generator(theme, PluginSpace.gen_length).generate()
    await send(output)


@error_codes
async def error_codes() -> None:
    _len = random.randint(50, 300)
    chars = [chr(random.randint(0x0021, 0x9FFF)) for i in range(_len)]
    chars.extend([random.choice(PluginSpace.punc) for i in range(math.ceil(_len / 5))])
    random.shuffle(chars)
    output = "".join(chars)[:_len]
    await send(output)
