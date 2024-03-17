from melobot import finish, msg_args, send, send_reply, thisbot
from melobot.models.cq import image_msg

from ..public_utils import base64_encode
from ._iface import PluginSpace, dice_draw, dice_info, dice_r
from .utils import DeckStore, r_gen


@dice_info
async def dice_info() -> None:
    output = "【dice 模拟器信息】\n ● 牌堆文件数：{}\n ● 牌堆总词条数：{}".format(
        len(DeckStore.get_all()), DeckStore.get_count()
    )
    await send(output)


@dice_r
async def dice_r() -> None:
    s = msg_args().pop(0)
    output = r_gen(s)
    await send_reply(output)


@dice_draw
async def dice_draw() -> None:
    deck_name, freq = msg_args()
    if deck_name is None:
        output = "当前可用牌堆：\n ● " + "\n ● ".join(PluginSpace.cmd_desks_map.keys())
        output += "\n本功能牌堆来源于：\n ● dice 论坛\n ● Github: @Vescrity"
        await finish(output)
    if deck_name not in PluginSpace.cmd_desks_map.keys():
        await finish(f"牌堆【{deck_name}】不存在")
    deck_group = PluginSpace.cmd_desks_map[deck_name]
    samples = deck_group.decks[deck_name].draw(sample_num=freq, replace=True)
    output = "\n\n".join(map(lambda x: x.replace("\n\n", "\n").strip("\n"), samples))
    if len(output) > 200:
        data = await thisbot.emit_signal("BaseUtils", "txt2img", output, wait=True)
        await finish(image_msg(base64_encode(data)))
    await send_reply(output)
