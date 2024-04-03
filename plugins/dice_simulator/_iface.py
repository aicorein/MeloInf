from melobot import BotPlugin
from melobot import CmdArgFormatter as Format

from ..env import COMMON_CHECKER, PARSER_GEN
from .utils import DeckStore

plugin = BotPlugin("DiceSimulator", version="1.2.0")


class PluginSpace:
    cmd_desks_map = {
        cmd: group for group in DeckStore.get_all().values() for cmd in group.cmds
    }


dice_r = plugin.on_message(
    checker=COMMON_CHECKER,
    parser=PARSER_GEN.gen(
        target=["r", "随机"],
        formatters=[
            Format(
                verify=lambda x: len(x) <= 15,
                src_desc="掷骰表达式",
                src_expect="字符数 <= 15",
            )
        ],
    ),
)

dice_draw = plugin.on_message(
    checker=COMMON_CHECKER,
    parser=PARSER_GEN.gen(
        target=["draw", "抽牌"],
        formatters=[
            Format(
                src_desc="牌堆名",
                src_expect="若缺乏牌堆名参数，则显示当前所有可用牌堆",
                default=None,
            ),
            Format(
                convert=int,
                verify=lambda x: 1 <= x <= 10,
                src_desc="抽牌次数",
                src_expect="1 <= 次数 <= 10",
                default=1,
            ),
        ],
    ),
)

dice_info = plugin.on_message(
    checker=COMMON_CHECKER,
    parser=PARSER_GEN.gen(target=["dice-info", "dice模拟器信息"]),
)
