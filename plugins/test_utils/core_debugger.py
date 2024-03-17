import importlib
from typing import Callable

from melobot import finish, msg_text, pause, send, send_reply, thisbot
from melobot.models import image_msg

from ..public_utils import base64_encode
from ._iface import core_debug


async def format_send(send_func: Callable, s: str) -> None:
    if len(s) <= 300:
        await send_func(s)
    elif len(s) > 10000:
        await send_func("<返回结果长度大于 10000，请使用调试器>")
    else:
        data = await thisbot.emit_signal("BaseUtils", "txt2img", s, 70, 16, wait=True)
        data = base64_encode(data)
        await send_func(image_msg(data))


@core_debug
async def core_debug_process() -> None:
    await send(
        "【你已进入核心调试状态】\n注意 ⚠️：对核心的错误修改可能导致崩溃，请谨慎操作！"
    )
    await send(
        "【输入求值表达式以查看值】\n例：bot.plugins['TestUtils']\n输入 $e$ 退出调试\n输入 $i$ 导入一个模块\n输入 $m$ 修改当前查看的值"
    )
    pointer = None
    imports = {}
    var_map = {"bot": thisbot}
    while True:
        await pause()
        match msg_text():
            case "$e$":
                await finish("已退出核心调试状态")
            case "$i$":
                await send("【开始导入在调试时可用的模块】\n$e$ 退出导入操作")
                await pause()
                try:
                    text = msg_text()
                    if text == "$e$":
                        await send("已退出导入操作")
                        continue
                    module = importlib.import_module(text)
                    imports[text] = module
                    var_map.update(imports)
                    await send(f"{text} 导入完成 ✅")
                except Exception as e:
                    await send(f"尝试导入模块时发生异常 ❌：{e.__str__()}")
            case "$m$":
                if pointer is None:
                    await send("当前修改指向空对象，拒绝操作 ❌")
                    continue
                else:
                    await send(
                        f"【输入修改后的值：】\n$e$ 退出修改操作\n当前指向对象：{pointer}"
                    )
                    await pause()
                    try:
                        text = msg_text()
                        if text == "$e$":
                            await send("已退出修改操作")
                            continue
                        exec(
                            f"{pointer}={msg_text()}",
                            var_map,
                        )
                        val = eval(f"{pointer}", var_map)
                        await format_send(
                            send, f"修改后的值为：{val}\n类型：{type(val)}"
                        )
                    except Exception as e:
                        await send(f"尝试修改值并重新显示时发生异常 ❌：{e.__str__()}")
            case _:
                try:
                    val = eval(f"{msg_text()}", var_map)
                    pointer = msg_text()
                    await format_send(send_reply, str(val))
                except Exception as e:
                    await send(f"获取值时出现异常 ❌：{e.__str__()}")
