from melobot import PluginPlanner, send_text
from melobot.protocols.onebot.v11 import on_message
from melobot.protocols.onebot.v11.handle import GetParseArgs
from melobot.protocols.onebot.v11.utils import ParseArgs

from ...platform.onebot import COMMON_CHECKER, PARSER_FACTORY

Echo = PluginPlanner("1.0.0")


@Echo.use
@on_message(
    parser=PARSER_FACTORY.get(["echo", "print", "repost", "复读"]),
    checker=COMMON_CHECKER,
)
async def onebot_echo(args: ParseArgs = GetParseArgs()) -> None:
    if len(args.vals):
        await send_text(args.vals[0])
