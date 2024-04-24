from melobot import User, msg_args, msg_event, send, send_reply, thisbot
from melobot.models import image_msg

from ..env import BOT_INFO, CHECKER_FACTORY
from ..public_utils import base64_encode
from ._iface import PluginRef, PluginSpace, auth, info, life, status

BOT_NICKNAME = PluginSpace.bot_nickname
META_INFO = PluginSpace.meta_info


@info
async def info() -> None:
    output = PluginSpace.bot_frontend_info.format(
        await PluginRef.cq_app_name(),
        await PluginRef.cq_app_ver(),
        await PluginRef.cq_protocol_ver(),
    )
    others = await PluginRef.cq_other_infos()
    if len(others):
        for k, v in others.items():
            output += f"\n{k}：{v}"
    await send(output)
    output = PluginSpace.bot_backend_str.format(
        BOT_NICKNAME,
        META_INFO.PROJ_NAME,
        META_INFO.VER,
        BOT_INFO.proj_name,
        BOT_INFO.proj_ver,
        BOT_INFO.proj_src.lstrip("https://"),
        f"{META_INFO.PY_INFO.major}.{META_INFO.PY_INFO.minor}.{META_INFO.PY_INFO.micro}",
        META_INFO.PLATFORM,
    )
    await send(output)


@auth
async def auth() -> None:
    u_level = CHECKER_FACTORY.get_base()._get_level(msg_event())
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
async def status() -> None:
    all_plugins = thisbot.get_plugins()
    output = " ● 启动时间：{}\n ● 已运行：{}\n ● 行为操作冷却：{}s\n ● 已加载插件：\n{}".format(
        PluginSpace.format_start_moment,
        PluginSpace.get_format_running_time(),
        thisbot.connector.cd_time,
        "\n".join(f"  - {p.id}: v{p.version}" for p in all_plugins.values()),
    )
    data = await thisbot.emit_signal("BaseUtils", "txt2img", output, 40, wait=True)
    await send(image_msg(base64_encode(data)))


@life
async def life() -> None:
    option = msg_args()[0]
    match option:
        case "on":
            if thisbot.is_activate():
                await send(f"{BOT_NICKNAME} 已经在工作啦~")
            else:
                thisbot.activate()
                await send(f"{BOT_NICKNAME} 已恢复工作~")
        case "off":
            await send(f"{BOT_NICKNAME} 去休息了~")
            thisbot.slack()
        case "stop":
            await send(f"{BOT_NICKNAME} 下班啦~", wait=True)
            thisbot.logger.info("指令触发停止操作，正在关闭 bot")
            await thisbot.close()
