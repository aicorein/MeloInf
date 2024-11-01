import importlib
from typing import Callable

from melobot import Plugin, get_bot, send_text
from melobot.di import Depends
from melobot.handle import get_event, stop
from melobot.protocols.onebot.v11 import Adapter, on_message
from melobot.protocols.onebot.v11.adapter.event import MessageEvent
from melobot.protocols.onebot.v11.adapter.segment import ImageSegment
from melobot.protocols.onebot.v11.utils import Checker, CmdParser
from melobot.session import Rule, enter_session, suspend

from ...platform.onebot import COMMON_CHECKER, PARSER_FACTORY, get_owner_checker
from ...utils import base64_encode
from .. import base_utils


class CoreDebugger(Plugin):
    def __init__(self) -> None:
        super().__init__()
        self.version = "1.0.0"
        self.flows = (core_dbg,)


async def format_send(send_func: Callable, s: str) -> None:
    if len(s) <= 300:
        await send_func(s)
    elif len(s) > 10000:
        await send_func("<返回结果长度大于 10000，请使用调试器>")
    else:
        data = await base_utils.txt2img(s, wrap_len=70, font_size=16)
        data = base64_encode(data)
        await send_func(ImageSegment(file=data))


def get_text() -> str:
    assert isinstance(event := get_event(), MessageEvent)
    return event.text


@on_message(checker=COMMON_CHECKER)
async def core_dbg(
    adapter: Adapter,
    event: MessageEvent,
    rule: Rule = Depends(
        lambda: Rule[MessageEvent].new(lambda e1, e2: e1.scope == e2.scope),
        cache=True,
        recursive=False,
    ),
    checker: Checker = Depends(
        lambda: get_owner_checker(
            fail_cb=lambda: get_bot()
            .get_adapter(Adapter)
            .send_reply("你无权使用【核心调试】功能")
        ),
        cache=True,
        recursive=False,
    ),
    parser: CmdParser = Depends(
        lambda: PARSER_FACTORY.get(["核心调试", "core-dbg"]), cache=True, recursive=False
    ),
) -> None:
    async with enter_session(rule):
        res = await parser.parse(event.text)
        if res is None:
            return

        if not await checker.check(event):
            return

        await send_text(
            "【你已进入核心调试状态】\n" + "注意 ⚠️：错误操作可能导致崩溃，请谨慎操作！"
        )
        await send_text(
            "【输入求值表达式以查看值】\n"
            "例：bot.name\n"
            "输入 $e$ 退出调试\n"
            "输入 $i$ 导入一个模块\n"
            "输入 $m$ 修改当前查看的值"
        )

        pointer = None
        imports = {}
        var_map = {"bot": get_bot()}

        while True:
            await suspend()

            match (get_text()):
                case "$e$":
                    await send_text("已退出核心调试状态")
                    await stop()

                case "$i$":
                    await send_text(
                        "【开始导入在调试时可用的模块】\n" + "$e$ 退出导入操作"
                    )
                    await suspend()

                    try:
                        text = get_text()
                        if text == "$e$":
                            await send_text("已退出导入操作")
                            continue

                        mod = importlib.import_module(text)
                        imports[text] = mod
                        var_map.update(imports)
                        await send_text(f"{text} 导入完成 ✅")

                    except Exception as e:
                        await send_text(f"尝试导入模块时发生异常 ❌：{str(e)}")

                case "$m$":
                    if pointer is None:
                        await send_text("修改指针为空，拒绝操作 ❌")
                        continue

                    await send_text(
                        "【输入修改后的值：】\n"
                        "$e$ 退出修改操作\n"
                        f"当前指向对象：{pointer}"
                    )
                    await suspend()

                    try:
                        text = get_text()
                        if text == "$e$":
                            await send_text("已退出修改操作")
                            continue

                        exec(f"{pointer}={text}", var_map)  # pylint: disable=exec-used
                        val = eval(f"{pointer}", var_map)  # pylint: disable=eval-used
                        await format_send(
                            send_text, f"修改后的值为：{val}\n" f"类型：{type(val)}"
                        )

                    except Exception as e:
                        await send_text(f"尝试修改值并重新显示时发生异常 ❌：{str(e)}")

                case _:
                    try:
                        text = get_text()
                        val = eval(f"{text}", var_map)  # pylint: disable=eval-used
                        pointer = text
                        await format_send(adapter.send_reply, str(val))

                    except Exception as e:
                        await send_text(f"获取值时出现异常 ❌：{str(e)}")
