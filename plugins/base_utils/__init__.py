from melobot import Plugin, bot, BotLife, session, User
from melobot import send, send_reply, get_metainfo
from melobot import ArgFormatter as Format, AttrSessionRule as AttrRule

from .recovery import save_restart_rec, read_restart_rec
from ..env import PASER_GEN, COMMON_CHECKER, BOT_INFO, CHECKER_GEN, OWNER_CHECKER



META_INFO = get_metainfo()
info = Plugin.on_message(parser=PASER_GEN.gen(["info", "信息"]), checker=COMMON_CHECKER)
auth = Plugin.on_message(parser=PASER_GEN.gen(["auth", "权限"]), checker=COMMON_CHECKER)
lifecycle = Plugin.on_message(checker=OWNER_CHECKER, 
                              session_rule=AttrRule('sender', 'id'),
                              conflict_callback=send("生命周期状态切换中...稍后再试~"),
                              parser=PASER_GEN.gen(["lifecycle", "lc", "生命周期"], 
                                                   formatters=[
                                                       Format(verify=lambda x: x in ['on', 'off', 'close', 'restart'],
                                                              src_desc="生命周期变更选项",
                                                              src_expect="以下值之一：['on', 'off', 'close', 'restart]")
                                                   ]))


class BaseUtils(Plugin):
    __share__ = ["bot_name", "bot_id"]

    def __init__(self) -> None:
        super().__init__()
        self.bot_name = None
        self.bot_id = None
        self.restart_rec_name = 'restart.rec'

    @bot.on(BotLife.CONNECTED)
    async def get_login_info(self) -> None:
        resp = await session.get_login_info()
        if resp.is_ok():
            self.bot_name = resp.data["nickname"]
            self.bot_id =resp.data["user_id"]
            BaseUtils.LOGGER.info("成功获得 bot 账号信息并存储")
        else:
            BaseUtils.LOGGER.warning("获取 bot 账号信息失败")

    @bot.on(BotLife.CONNECTED)
    async def restart_wake(self) -> None:
        res = read_restart_rec(self.ROOT, self.restart_rec_name)
        if res is not None:
            sender_id, is_private, group_id = res
            await session.custom_send("重启完成~", is_private, sender_id, group_id)
            BaseUtils.LOGGER.info("本次启动为指令触发的重启，已回复重启成功消息")

    @info
    async def info(self) -> None:
        output = "bot 昵称：{}\n内核项目：{}\n内核版本：{}\n内核项目地址：{}\nbot 项目：{}\nbot 版本：{}\nbot 项目地址：{}".format(
            BOT_INFO.bot_nickname,
            META_INFO.PROJ_NAME, f"v{META_INFO.VER}", META_INFO.PROJ_SRC,
            BOT_INFO.name, f"v{BOT_INFO.ver}", BOT_INFO.src
        )
        await send(output)

        output = "运行平台：{}\npy 版本：{}\n运行参数：{}".format(
            META_INFO.PLATFORM,
            META_INFO.PY_VER.split('|')[0],
            META_INFO.ARGV,
        )
        await send(output)

    @auth
    async def auth(self) -> None:
        u_level = CHECKER_GEN.gen_base()._get_level(session.event)
        alist = [
            u_level >= User.OWNER,
            u_level >= User.SU,
            u_level >= User.WHITE,
            u_level >= User.USER,
        ]
        output = "当前对 bot 具有权限：\nowner：{}\nsuperuser：{}\nwhite_user：{}\nuser：{}".format(*alist)
        await send_reply(output)

    @lifecycle
    async def lifecycle(self) -> None:
        option = session.args.vals.pop(0)
        match option:
            case 'on': 
                if bot.is_activate:
                    await send("bot 已经在工作啦~")
                else:
                    bot.activate()
                    await send("bot 已恢复工作~")
            case 'off':
                await send("bot 去休息了~")
                bot.slack()
            case 'close':
                await send("bot 下班啦~")
                BaseUtils.LOGGER.info("指令触发停止操作，正在关闭 bot")
                await bot.close()
            case 'restart':
                if bot.can_restart():
                    await send("bot 正在准备重启...")
                    save_restart_rec(self.ROOT, self.restart_rec_name)
                    await bot.restart()
                else:
                    await send("当前运行模式不支持重启哦，如需重启，请使用模块运行模式：\n python -m melobot main.py")
