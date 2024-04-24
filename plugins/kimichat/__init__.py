from melobot import BotPlugin
from melobot import CmdArgFormatter as Format
from melobot import CmdParser, msg_args, reply_finish, send_reply, thisbot
from melobot.base.tools import semaphore, speedlimit, timelimit

from ..env import BOT_INFO, COMMON_CHECKER
from ..public_utils import async_http

plugin = BotPlugin("KimiChat", version="1.0.0")


class PluginSpace:
    url = "https://api.moonshot.cn/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {BOT_INFO.moonshot_key}",
        "Content-Type": "application/json",
    }
    chars_num = 384
    data = {
        "model": "moonshot-v1-8k",
        "messages": [
            {
                "role": "system",
                "content": f"你叫{BOT_INFO.bot_name}（也可以叫{BOT_INFO.bot_nickname}），是qq这款聊天软件某个群的群成员，你的主人名叫{BOT_INFO.owner_name}。现在你将模仿一只猫娘，与群里的群友聊天。请牢记：你会为提供安全，有帮助，准确的回答。同时，你会拒绝一切涉及恐怖主义，种族歧视，黄色暴力主题的问题或话题讨论。另外，回答请控制在{chars_num}字以内（包含代码块）。",
            },
            {
                "role": "user",
                "content": "",
            },
        ],
        "temperature": 0.3,
        "max_tokens": int(chars_num * 0.6),
    }


chat = plugin.on_message(
    checker=COMMON_CHECKER,
    parser=CmdParser(
        cmd_start="*",
        cmd_sep="#",
        targets=["chat", "聊天"],
        formatters=[
            Format(
                verify=lambda x: 0 < len(x) <= 100,
                src_desc="问答的字数",
                src_expect="0 < 字数 <= 100",
            )
        ],
    ),
)


@chat
@semaphore(
    callback=lambda: send_reply(f"{BOT_INFO.bot_nickname}在回复其他几个问题，等等哦"),
    value=10,
)
@speedlimit(
    callback=lambda: send_reply("一分钟内只能回复 30 次啦，稍后再来吧~"),
    limit=30,
)
@timelimit(
    callback=lambda: send_reply(f"{BOT_INFO.bot_nickname}连接服务器超时 QAQ"),
    timeout=30,
)
async def chat() -> None:
    data = PluginSpace.data.copy()
    prompt = msg_args()[0]
    data["messages"][-1]["content"] = prompt
    async with async_http(
        PluginSpace.url, "post", headers=PluginSpace.headers, json=data
    ) as resp:
        try:
            if resp.status != 200:
                thisbot.logger.error(f"获取 chat 回复失败，状态码：{resp.status}")
                await reply_finish("获取 chat 回复失败，稍后再试")
            else:
                res = await resp.json()
                output = res["choices"][0]["message"]["content"]
                await send_reply(output)
        except Exception:
            await send_reply("获取 chat 回复出现异常，稍后再试")
            raise
