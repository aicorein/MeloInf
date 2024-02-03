from melobot import Plugin, send_reply, session
from melobot import ArgFormatter as Format
from melobot import CmdParser

from ..env import COMMON_CHECKER, get_headers
from ..utils import async_http


code_c = Plugin.on_message(checker=COMMON_CHECKER, parser=CmdParser(
    cmd_start='*',
    cmd_sep='---',
    target=["code", "代码"],
    formatters=[
        Format(convert=lambda x: x.lower(),
               verify=lambda x: x in ["cpp", "cs", "py"],
               src_desc="编程语言类型",
               src_expect='是以下值之一（兼容大小写）：["cpp", "cs", "py"]'),
        Format(verify=lambda x: len(x) <= 1000,
               src_desc="代码",
               src_expect="代码总字符数 <= 1000")
    ]
))

class CodeCompiler(Plugin):
    def __init__(self) -> None:
        super().__init__()
    
    @code_c
    async def codec(self) -> None:
        lang, code = session.args.vals
        match lang:
            case "cpp": lang_id, ext = 7, "cpp"
            case "cs": lang_id, ext = 10, "cs"
            case "py": lang_id, ext = 15, "py3"
        url = 'https://www.runoob.com/try/compile2.php'
        headers = get_headers()
        headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
        data = {
            'code': code,
            'token': '066417defb80d038228de76ec581a50a',
            'language': lang_id,
            'fileext': ext,
        }
        async with async_http(url, 'post', headers=headers, data=data) as resp:
            if resp.status != 200:
                await send_reply("远端编译请求失败...请稍后再试，或联系 bot 管理员解决")
                CodeCompiler.LOGGER.error(f"请求失败：{resp.status}")
                return
            try:
                ret = await resp.json()
                if ret['errors'] != '\n\n':
                    output = ret['errors'].strip('\n')
                else:
                    output = ret['output'].strip('\n')
                await send_reply(output)
            except Exception as e:
                await send_reply("远端编译请求失败...请稍后再试，或联系 bot 管理员解决")
                CodeCompiler.LOGGER.error(f"{e.__class__.__name__} {e}")
