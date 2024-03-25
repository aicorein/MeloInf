from melobot import ArgFormatter as Format
from melobot import BotPlugin, CmdParser, msg_args, send_reply, timelimit
from melobot.base.exceptions import BotException

from ..env import BOT_INFO, COMMON_CHECKER
from ..public_utils import async_http, get_headers

plugin = BotPlugin("CodeCompiler", version="1.3.0")

url = "https://www.runoob.com/try/compile2.php"

code_c = plugin.on_message(
    checker=COMMON_CHECKER,
    parser=CmdParser(
        cmd_start=["~", "～"],
        cmd_sep="$",
        target=["code", "代码"],
        formatters=[
            Format(
                convert=lambda x: x.lower(),
                verify=lambda x: x in ["cpp", "cs", "py"],
                src_desc="编程语言类型",
                src_expect="是以下值之一（兼容大小写）：[cpp, cs, py]",
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


@code_c
@timelimit(lambda: send_reply("代码编译结果获取超时，请稍候再试..."), timeout=25)
async def codec() -> None:
    lang, code = msg_args()
    match lang:
        case "cpp":
            lang_id, ext = 7, "cpp"
        case "cs":
            lang_id, ext = 10, "cs"
        case "py":
            lang_id, ext = 15, "py3"
    output = await compile(code, lang_id, ext)
    await send_reply(output)


@plugin.on_signal("CodeCompiler", "do_calc")
async def do_calc(expression: str, lang_id: int, ext: str) -> str:
    code = f"print(eval('{expression}'))"
    output = await compile(code, lang_id, ext)
    return output


def gen_headers() -> dict:
    headers = get_headers()
    headers["Content-Type"] = "application/x-www-form-urlencoded; charset=UTF-8"
    return headers


async def compile(code: str, lang_id: int, ext: str) -> str:
    data = {
        "code": code,
        "token": "066417defb80d038228de76ec581a50a",
        "language": lang_id,
        "fileext": ext,
    }
    async with async_http(url, "post", headers=gen_headers(), data=data) as resp:
        if resp.status != 200:
            await send_reply("远端编译请求失败...请稍后再试，或联系 bot 管理员解决")
            raise BotException(f"远端编译请求失败：{resp.status}")
        try:
            ret = await resp.json()
            if ret["errors"] != "\n\n":
                output = ret["errors"].strip("\n")
            else:
                output = ret["output"].strip("\n")
            return output
        except Exception as e:
            await send_reply("远端编译请求失败...请稍后再试，或联系 bot 管理员解决")
            raise BotException(f"远端编译请求异常：{e.__class__.__name__} {e}")
