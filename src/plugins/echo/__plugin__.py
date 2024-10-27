from typing import cast

from melobot import MetaInfo, get_bot
from melobot.adapter import AdapterLifeSpan, open_chain
from melobot.adapter.generic import send_text
from melobot.io import AbstractIOSource, SourceLifeSpan
from melobot.log import GenericLogger
from melobot.plugin import Plugin
from melobot.protocols.onebot.v11.adapter import Adapter, EchoRequireCtx
from melobot.protocols.onebot.v11.adapter.action import Action
from melobot.protocols.onebot.v11.adapter.event import MessageEvent, NoticeEvent
from melobot.protocols.onebot.v11.const import PROTOCOL_IDENTIFIER
from melobot.protocols.onebot.v11.handle import Args, on_command, on_notice
from melobot.protocols.onebot.v11.utils import ParseArgs

bot = get_bot()
ob11_adapter: Adapter | None = cast(Adapter, bot.get_adapter(PROTOCOL_IDENTIFIER))
assert ob11_adapter is not None


@ob11_adapter.on(AdapterLifeSpan.BEFORE_ACTION)
def aprint(action: Action, logger: GenericLogger) -> None:
    logger.generic_obj("即将发送的 onebot-v11 行为", action.flatten())


iset = ob11_adapter.get_isrcs(lambda _: True)
for input in iset:

    async def _close_log(logger: GenericLogger, src: AbstractIOSource = input) -> None:
        logger.info(f"输出源 {src} 已关闭")

    input.on(SourceLifeSpan.STOPPED)(_close_log)


@on_command(
    cmd_start=".",
    cmd_sep=" ",
    targets=["echo", "repeat", "print"],
    checker=lambda e: e.user_id == 1574260633,
)
async def echo(adapter: Adapter, event: MessageEvent, args: ParseArgs = Args()) -> None:
    with open_chain() as chain:
        (
            await chain.in_ctx(EchoRequireCtx(), True)
            .add(send_text(f"[{event.id}]\nArgs: {args.vals}"))
            .add(adapter.send("echoed"))
            .sleep(1)
            .add(
                adapter.send_image(
                    "test.jpg", url="https://glowmem.com/static/avatar.jpg"
                )
            )
            .sleep(1)
            .add(send_text("chain finished"))
            .run()
        )


@on_command(cmd_start=".", cmd_sep=" ", targets=["info"])
async def info(event: MessageEvent) -> None:
    assert ob11_adapter is not None

    await send_text(
        f"id: {event.self_id}\n"
        f"core: {MetaInfo.name} {MetaInfo.ver}\n"
        f"protocol stack: {list(a.protocol for a in bot.adapters.values())}\n"
        f"inputs: {len(ob11_adapter.get_isrcs(lambda _: True))}\n"
        f"outputs: {len(ob11_adapter.get_osrcs(lambda _: True))}\n"
        f"plugins: {len(bot.get_plugins())}\n"
    )


@on_notice()
async def get_notice(event: NoticeEvent, logger: GenericLogger) -> None:
    logger.generic_obj("收到通知事件", event.__dict__)


class EchoPlugin(Plugin):
    version = "1.0.0"
    flows = [echo, get_notice, info]
