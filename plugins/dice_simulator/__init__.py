from melobot import Plugin, session
from melobot import ArgFormatter as Format
from melobot import send, send_reply, finish

from ..env import COMMON_CHECKER, PARSER_GEN
from .utils import DeckStore, r_gen


dice_r = Plugin.on_msg(checker=COMMON_CHECKER, parser=PARSER_GEN.gen(
    target="r",
    formatters=[
        Format(verify=lambda x: len(x) <= 15,
               src_desc="r 值表达式",
               src_expect="字符数 <= 15")
    ]
))
dice_draw = Plugin.on_msg(checker=COMMON_CHECKER, parser=PARSER_GEN.gen(
    target="draw",
    formatters=[
        Format(src_desc="牌堆名",
               src_expect="若缺乏牌堆名参数，则显示当前所有可用牌堆",
               default=None)
    ]
))


class DiceSimulator(Plugin):
    def __init__(self) -> None:
        super().__init__()
        self.cmd_desks_map = {cmd: group for group in DeckStore.get_all().values() for cmd in group.cmds}
    
    @dice_r
    async def dice_r(self) -> None:
        s = session.args.vals.pop(0)
        try:
            output = r_gen(s)
            await send_reply(output)
        except Exception as e:
            await send_reply("掷骰表达式解析错误...已记录错误日志")
            raise e
    
    @dice_draw
    async def dice_draw(self) -> None:
        deck_name = session.args.vals.pop(0)
        if deck_name is None:
            output = '当前可用牌堆：\n ● ' + '\n ● '.join(self.cmd_desks_map.keys())
            output += "\n本功能牌堆来源于：\n ● dice 论坛\n ● Github: @Vescrity"
            await finish(output)
        if deck_name not in self.cmd_desks_map.keys():
            await finish(f"牌堆【{deck_name}】不存在")
        deck_group = self.cmd_desks_map[deck_name]
        output = deck_group.decks[deck_name].draw()[0].strip('\n')
        await send_reply(output)
