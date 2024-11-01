from melobot import Plugin, send_text
from melobot.handle import stop
from melobot.protocols.onebot.v11 import Adapter, on_message
from melobot.protocols.onebot.v11.adapter.event import GroupMessageEvent
from melobot.protocols.onebot.v11.handle import GetParseArgs
from melobot.protocols.onebot.v11.utils import CmdParser, ParseArgs
from melobot.utils import RWContext

from ...platform.onebot import COMMON_CHECKER, get_owner_checker


class GroupTitle(Plugin):
    flag = False
    flag_rw = RWContext()

    def __init__(self) -> None:
        super().__init__()
        self.version = "1.0.0"
        self.flows = (title_manager,)


OWNER_CHECKER = get_owner_checker()


@on_message(checker=COMMON_CHECKER, parser=CmdParser("!", "$", ["title", "头衔"]))
async def title_manager(
    adapter: Adapter, event: GroupMessageEvent, args: ParseArgs = GetParseArgs()
) -> None:
    if len(args.vals) <= 0:
        return await send_text("不支持的群头衔功能指令")

    match args.vals[0]:
        case "set" | "设置":
            async with GroupTitle.flag_rw.read():
                if not GroupTitle.flag:
                    return await send_text("群头衔相关功能未被启用")

                gtitle = " ".join(args.vals[1:])
                if gtitle == "":
                    return await send_text("群头衔值不能为空")
                return await adapter.set_group_special_title(
                    event.group_id, event.user_id, title=gtitle
                )

        case "enable" | "启用" | "开启":
            await owner_check(adapter, event)
            async with GroupTitle.flag_rw.write():
                GroupTitle.flag = True
                return await send_text("群头衔相关功能已启用 ✅")

        case "disable" | "禁用" | "关闭" | "禁用":
            await owner_check(adapter, event)
            async with GroupTitle.flag_rw.write():
                GroupTitle.flag = False
                return await send_text("群头衔相关功能已禁用 ✅")

        case _:
            return await send_text("不支持的群头衔功能指令")


async def owner_check(adapter: Adapter, event: GroupMessageEvent) -> None:
    if not await OWNER_CHECKER.check(event):
        await adapter.send_reply("无权执行此操作")
        await stop()
