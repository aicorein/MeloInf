import datetime as dt
import time
from typing import Any

from melobot import AttrSessionRule as AttrRule
from melobot import BotPlugin
from melobot import CmdArgFormatter as Format
from melobot import MetaInfo, PriorLevel, send, send_reply, thisbot

from ..env import BOT_INFO, COMMON_CHECKER, PARSER_GEN, get_owner_checker

plugin = BotPlugin("LifeCycleUtils", "2.0.0")


class PluginSpace:
    meta_info = MetaInfo()
    bot_nickname = BOT_INFO.bot_nickname
    bot_backend_str = """【bot backend】
name：{}
core：{}-{}
proj：{}-{}
src：{}
python env：{}-{}"""
    bot_frontend_info = """【bot frontend】
core：{}
version：{}
protocol：{}"""
    start_moment = time.time()
    format_start_moment = dt.datetime.now().strftime("%m-%d %H:%M:%S")

    def get_running_time() -> float:
        return time.time() - PluginSpace.start_moment

    def get_format_running_time() -> str:
        def format_nums(*timeNum: int) -> list[str]:
            return [str(num) if num >= 10 else "0" + str(num) for num in timeNum]

        worked_time = int(time.time() - PluginSpace.start_moment)
        days = worked_time // 3600 // 24
        hours = worked_time // 3600 % 24
        mins = worked_time // 60 % 60
        secs = worked_time % 60
        time_str_list = format_nums(days, hours, mins, secs)
        return ":".join(time_str_list)


class PluginRef:
    async def cq_app_name() -> str:
        return await thisbot.get_share("BaseUtils", "cq_app_name").val

    async def cq_app_ver() -> str:
        return await thisbot.get_share("BaseUtils", "cq_app_ver").val

    async def cq_protocol_ver() -> str:
        return await thisbot.get_share("BaseUtils", "cq_protocol_ver").val

    async def cq_other_infos() -> dict[str, Any]:
        return await thisbot.get_share("BaseUtils", "cq_other_infos").val


plugin.on_share(
    plugin.__id__, "start_moment", lambda: getattr(PluginSpace, "start_moment")
)
plugin.on_share(
    plugin.__id__,
    "format_start_moment",
    lambda: getattr(PluginSpace, "format_start_moment"),
)
plugin.on_share(plugin.__id__, "running_time", PluginSpace.get_running_time)
plugin.on_share(
    plugin.__id__, "format_running_time", PluginSpace.get_format_running_time
)


info = plugin.on_message(
    parser=PARSER_GEN.gen(target=["info", "信息"]), checker=COMMON_CHECKER
)

auth = plugin.on_message(
    parser=PARSER_GEN.gen(target=["auth", "权限"]), checker=COMMON_CHECKER
)

status = plugin.on_message(
    parser=PARSER_GEN.gen(target=["status", "状态"]), checker=COMMON_CHECKER
)

life = plugin.on_message(
    checker=get_owner_checker(
        fail_cb=lambda: send_reply("你无权使用【生命状态设置】功能")
    ),
    session_rule=AttrRule("sender", "id"),
    conflict_cb=lambda: send("工作状态切换中...稍后再试~"),
    priority=PriorLevel.MIN,
    parser=PARSER_GEN.gen(
        target=["life", "状态设置"],
        formatters=[
            Format(
                verify=lambda x: x in ["on", "off", "stop"],
                src_desc="工作状态变更选项",
                src_expect="以下值之一：[on, off, stop]",
            )
        ],
    ),
)
