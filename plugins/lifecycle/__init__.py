import datetime as dt
import time
from typing import List

from melobot import ArgFormatter as Format
from melobot import AttrSessionRule as AttrRule
from melobot import (
    MetaInfo,
    Plugin,
    PluginStore,
    PriorLevel,
    User,
    bot,
    msg_args,
    msg_event,
    send,
    send_custom_msg,
    send_reply,
)

from ..env import BOT_INFO, CHECKER_GEN, COMMON_CHECKER, PARSER_GEN, get_owner_checker
from .recovery import read_rec, save_rec

META_INFO = MetaInfo()
BOT_NICKNAME = BOT_INFO.bot_nickname
info = Plugin.on_message(
    parser=PARSER_GEN.gen(target=["info", "信息"]), checker=COMMON_CHECKER
)
auth = Plugin.on_message(
    parser=PARSER_GEN.gen(target=["auth", "权限"]), checker=COMMON_CHECKER
)
status = Plugin.on_message(
    parser=PARSER_GEN.gen(target=["status", "状态"]), checker=COMMON_CHECKER
)
life = Plugin.on_message(
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
                verify=lambda x: x in ["on", "off", "stop", "restart", "re"],
                src_desc="工作状态变更选项",
                src_expect="以下值之一：['on', 'off', 'stop', 'restart', 're']",
            )
        ],
    ),
)


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


class LifeCycleUtils(Plugin):
    def __init__(self) -> None:
        super().__init__()
        self.SHARES.extend(
            [
                "start_moment",
                "format_start_moment",
                "running_time",
                "format_running_time",
            ]
        )

        self.rec_name = "restart.rec"
        self.start_moment = time.time()
        self.format_start_moment = dt.datetime.now().strftime("%m-%d %H:%M:%S")
        self.cq_app_name = PluginStore.get("BaseUtils", "cq_app_name")
        self.cq_app_ver = PluginStore.get("BaseUtils", "cq_app_ver")
        self.cq_protocol_ver = PluginStore.get("BaseUtils", "cq_protocol_ver")
        self.cq_other_infos = PluginStore.get("BaseUtils", "cq_other_infos")

    @property
    def running_time(self) -> float:
        return time.time() - self.start_moment

    @property
    def format_running_time(self) -> str:
        def format_nums(*timeNum: int) -> list[str]:
            return [str(num) if num >= 10 else "0" + str(num) for num in timeNum]

        worked_time = int(time.time() - self.start_moment)
        days = worked_time // 3600 // 24
        hours = worked_time // 3600 % 24
        mins = worked_time // 60 % 60
        secs = worked_time % 60
        time_str_list = format_nums(days, hours, mins, secs)
        return ":".join(time_str_list)

    @bot.on_connected()
    async def restart_wake(self) -> None:
        res = read_rec(str(self.PATH), self.rec_name)
        if res is not None:
            sender_id, is_private, group_id = res
            await send_custom_msg(
                f"{BOT_NICKNAME} 重启完成~", is_private, sender_id, group_id
            )
            self.LOGGER.info("本次启动为指令触发的重启，已回复重启成功消息")

    @info
    async def info(self) -> None:
        output = bot_frontend_info.format(
            self.cq_app_name.val, self.cq_app_ver.val, self.cq_protocol_ver.val
        )
        if len(self.cq_other_infos.val):
            for k, v in self.cq_other_infos.val.items():
                output += f"\n{k}：{v}"
        await send(output)
        output = bot_backend_str.format(
            BOT_NICKNAME,
            META_INFO.PROJ_NAME,
            META_INFO.VER,
            BOT_INFO.proj_name,
            BOT_INFO.proj_ver,
            BOT_INFO.proj_src.lstrip("https://"),
            META_INFO.PY_VER.split("|")[0].strip(" "),
            META_INFO.PLATFORM,
        )
        await send(output)

    @auth
    async def auth(self) -> None:
        u_level = CHECKER_GEN.gen_base()._get_level(msg_event())
        alist = [
            BOT_NICKNAME,
            u_level >= User.OWNER,
            u_level >= User.SU,
            u_level >= User.WHITE,
            u_level >= User.USER,
        ]
        output = "当前对 {} 具有权限：\n ● owner：{}\n ● superuser：{}\n ● white_user：{}\n ● user：{}".format(
            *alist
        )
        await send_reply(output)

    @status
    async def status(self) -> None:
        all_plugins = bot.get_plugins()
        output = " ● 运行模式：{}\n ● 启动时间：{}\n ● 已运行：{}\n ● 全局冷却时间：{}s\n ● 已加载插件：{}".format(
            "模块运行模式" if bot.is_module_run() else "脚本运行模式",
            self.format_start_moment,
            self.format_running_time,
            bot.get_config().cooldown_time,
            ", ".join([p.id for p in all_plugins.values()])
            + f"（{len(all_plugins)} 个）",
        )
        await send(output)

    @life
    async def life(self) -> None:
        option = msg_args().pop(0)
        match option:
            case "on":
                if bot.is_activate:
                    await send(f"{BOT_NICKNAME} 已经在工作啦~")
                else:
                    bot.activate()
                    await send(f"{BOT_NICKNAME} 已恢复工作~")
            case "off":
                await send(f"{BOT_NICKNAME} 去休息了~")
                bot.slack()
            case "stop":
                await send(f"{BOT_NICKNAME} 下班啦~")
                self.LOGGER.info("指令触发停止操作，正在关闭 bot")
                await bot.close()
            case "restart" | "re":
                if bot.is_module_run():
                    await send(f"{BOT_NICKNAME} 正在准备重启...")
                    save_rec(str(self.PATH), self.rec_name)
                    await bot.restart()
                else:
                    await send(
                        f"{BOT_NICKNAME} 当前运行模式不支持重启哦，如需重启，请使用模块运行模式：\npython -m melobot main.py"
                    )
