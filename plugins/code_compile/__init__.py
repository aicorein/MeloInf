from typing import Dict

from melobot import ArgFormatter as Format
from melobot import CmdParser, Plugin, PluginBus, send_reply, session

from ..env import BOT_INFO, COMMON_CHECKER
from ..public_utils import async_http, get_headers

code_c = Plugin.on_message(
    checker=COMMON_CHECKER,
    timeout=25,
    overtime_cb=lambda: send_reply("代码编译结果获取超时，请稍候再试..."),
    parser=CmdParser(
        cmd_start="*",
        cmd_sep="$",
        target=["code", "代码"],
        formatters=[
            Format(
                convert=lambda x: x.lower(),
                verify=lambda x: x in ["cpp", "cs", "py"],
                src_desc="编程语言类型",
                src_expect='是以下值之一（兼容大小写）：["cpp", "cs", "py"]',
                default="py",
                default_replace_flag=BOT_INFO.uni_default_flag,
            ),
            Format(
                verify=lambda x: len(x) <= 1000,
                src_desc="代码",
                src_expect="代码总字符数 <= 1000",
            ),
        ],
    ),
)


class CodeCompiler(Plugin):
    def __init__(self) -> None:
        super().__init__()
        self.url = "https://www.runoob.com/try/compile2.php"

    @PluginBus.on("CodeCompiler", "do_calc")
    async def do_calc(self, expression: str, lang_id: int, ext: str) -> str:
        code = f"print(eval('{expression}'))"
        output = await self.compile(code, lang_id, ext)
        return output

    def gen_headers(self) -> Dict:
        headers = get_headers()
        headers["Content-Type"] = "application/x-www-form-urlencoded; charset=UTF-8"
        return headers

    async def compile(self, code: str, lang_id: int, ext: str) -> str:
        data = {
            "code": code,
            "token": "066417defb80d038228de76ec581a50a",
            "language": lang_id,
            "fileext": ext,
        }
        async with async_http(
            self.url, "post", headers=self.gen_headers(), data=data
        ) as resp:
            if resp.status != 200:
                await send_reply("远端编译请求失败...请稍后再试，或联系 bot 管理员解决")
                CodeCompiler.LOGGER.error(f"请求失败：{resp.status}")
                return
            try:
                ret = await resp.json()
                if ret["errors"] != "\n\n":
                    output = ret["errors"].strip("\n")
                else:
                    output = ret["output"].strip("\n")
                return output
            except Exception as e:
                await send_reply("远端编译请求失败...请稍后再试，或联系 bot 管理员解决")
                CodeCompiler.LOGGER.error(f"{e.__class__.__name__} {e}")

    @code_c
    async def codec(self) -> None:
        lang, code = session.args
        match lang:
            case "cpp":
                lang_id, ext = 7, "cpp"
            case "cs":
                lang_id, ext = 10, "cs"
            case "py":
                lang_id, ext = 15, "py3"
        output = await self.compile(code, lang_id, ext)
        await send_reply(output)
