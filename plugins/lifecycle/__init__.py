import time
import datetime as dt
from typing import List
from melobot import Plugin, send, send_reply, get_metainfo
from melobot import ArgFormatter as Format, AttrSessionRule as AttrRule
from melobot import User, BotLife, bot, session, PriorityLevel

from ..env import PASER_GEN, COMMON_CHECKER, BOT_INFO, CHECKER_GEN, OWNER_CHECKER
from .recovery import read_rec, save_rec


META_INFO = get_metainfo()
BOT_NICKNAME = BOT_INFO.bot_nickname
info = Plugin.on_message(parser=PASER_GEN.gen(["info", "信息"]), checker=COMMON_CHECKER)
auth = Plugin.on_message(parser=PASER_GEN.gen(["auth", "权限"]), checker=COMMON_CHECKER)
status = Plugin.on_message(parser=PASER_GEN.gen(["status", "状态"]), checker=COMMON_CHECKER)
life = Plugin.on_message(checker=OWNER_CHECKER, 
                         session_rule=AttrRule('sender', 'id'),
                         conflict_callback=send("工作状态切换中...稍后再试~"),
                         priority=PriorityLevel.MIN,
                         parser=PASER_GEN.gen(["life", "状态设置"], 
                                              formatters=[
                                                  Format(verify=lambda x: x in ['on', 'off', 'close', 'restart'],
                                                         src_desc="工作状态变更选项",
                                                         src_expect="以下值之一：['on', 'off', 'close', 'restart']")
                                              ]))


class LifeCycleUtils(Plugin):
    __share__ = ['start_moment', 'format_start_moment', 'running_time', 'format_running_time']

    def __init__(self) -> None:
        super().__init__()
        self.rec_name = 'restart.rec'
        self.start_moment = time.time()
        self.format_start_moment = dt.datetime.now().strftime('%m-%d %H:%M:%S')

    @property
    def running_time(self) -> float:
        return time.time() - self.start_moment

    @property
    def format_running_time(self) -> str:
        def format_nums(*timeNum: List[int]) -> str:
            return [str(num) if num >= 10 else '0' + str(num) for num in timeNum]
        worked_time = int(time.time() - self.start_moment)
        days = worked_time // 3600 // 24
        hours = worked_time // 3600 % 24
        mins = worked_time // 60 % 60
        secs = worked_time % 60
        time_str_list = format_nums(days, hours, mins, secs)
        return ":".join(time_str_list)

    @bot.on(BotLife.CONNECTED)
    async def restart_wake(self) -> None:
        res = read_rec(self.ROOT, self.rec_name)
        if res is not None:
            sender_id, is_private, group_id = res
            await session.custom_send(f"{BOT_NICKNAME} 重启完成~", is_private, sender_id, group_id)
            LifeCycleUtils.LOGGER.info("本次启动为指令触发的重启，已回复重启成功消息")

    @info
    async def info(self) -> None:
        output = " ● bot 昵称：{}\n ● 内核：{}\n ● 内核版本：{}\n ● 内核项目地址：{}\n ● bot 项目：{}\n ● bot 版本：{}\n ● bot 项目地址：{}".format(
            BOT_NICKNAME,
            META_INFO.PROJ_NAME, f"v{META_INFO.VER}", META_INFO.PROJ_SRC,
            BOT_INFO.name, f"v{BOT_INFO.ver}", BOT_INFO.src
        )
        await send(output)

        output = " ● 运行平台：{}\n ● py 版本：{}".format(
            META_INFO.PLATFORM,
            META_INFO.PY_VER.split('|')[0]
        )
        await send(output)

    @auth
    async def auth(self) -> None:
        u_level = CHECKER_GEN.gen_base()._get_level(session.event)
        alist = [
            BOT_NICKNAME,
            u_level >= User.OWNER,
            u_level >= User.SU,
            u_level >= User.WHITE,
            u_level >= User.USER,
        ]
        output = "当前对 {} 具有权限：\n ● owner：{}\n ● superuser：{}\n ● white_user：{}\n ● user：{}".format(*alist)
        await send_reply(output)

    @status
    async def status(self) -> None:
        output = " ● 运行模式：{}\n ● 启动时间：{}\n ● 已运行：{}\n ● 全局冷却时间：{}s\n ● 已加载插件：{}".format(
            "模块运行模式" if bot.is_module_run() else "脚本运行模式",
            self.format_start_moment,
            self.format_running_time,
            bot.config.cooldown_time,
            ', '.join([p.id for p in bot.plugins.values()]) + f"（{len(bot.plugins)} 个）"
        )
        await send(output)

    @life
    async def life(self) -> None:
        option = session.args.vals.pop(0)
        match option:
            case 'on': 
                if bot.is_activate:
                    await send(f"{BOT_NICKNAME} 已经在工作啦~")
                else:
                    bot.activate()
                    await send(f"{BOT_NICKNAME} 已恢复工作~")
            case 'off':
                await send(f"{BOT_NICKNAME} 去休息了~")
                bot.slack()
            case 'close':
                await send(f"{BOT_NICKNAME} 下班啦~")
                LifeCycleUtils.LOGGER.info("指令触发停止操作，正在关闭 bot")
                await bot.close()
            case 'restart':
                if bot.is_module_run():
                    await send(f"{BOT_NICKNAME} 正在准备重启...")
                    save_rec(self.ROOT, self.rec_name)
                    await bot.restart()
                else:
                    await send(f"{BOT_NICKNAME} 当前运行模式不支持重启哦，如需重启，请使用模块运行模式：\npython -m melobot main.py")
