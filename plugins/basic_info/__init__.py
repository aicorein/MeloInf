from melobot import Plugin, PluginStore, META_INFO, session
from melobot import User, send, send_reply
from ..env import CHECKER_GEN, PASER_GEN, BOT_INFO, COMMON_CHECKER


info = Plugin.on_message(parser=PASER_GEN.gen(["info", "信息"]), checker=COMMON_CHECKER)
auth = Plugin.on_message(parser=PASER_GEN.gen(["auth", "权限"]), checker=COMMON_CHECKER)


class BasicInfo(Plugin):
    def __init__(self) -> None:
        super().__init__()
        self.bot_name = PluginStore.get("BaseUtils", "bot_name")
        self.bot_id = PluginStore.get("BaseUtils", "bot_id")

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