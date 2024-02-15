import aiohttp
import base64
import re
from typing import Literal, AsyncGenerator
from contextlib import asynccontextmanager


ENG_PUNC = r"""!"#$%&',.:;?@\^"""
WITHOUT_DOLLAR_ENG_PUNC = r"""!"#%&',.:;?@\^"""
HANS_PUNC = '。，、；：？！…—·ˉ¨‘’“”々～‖∶＂＇｀〃．'  


def remove_punctuation(s: str) -> str:
    punc = ENG_PUNC + HANS_PUNC
    return re.sub(rf'[{re.escape(punc)}]', '', s)


def remove_ask_punctuation(s: str) -> str:
    punc = WITHOUT_DOLLAR_ENG_PUNC + HANS_PUNC
    return re.sub(rf'[{re.escape(punc)}]', '', s)


def base64_encode(data: bytes) -> str:
    """
    返回 base64 编码的数据，携带 `base64://` 标志
    """
    code = 'base64://'
    code += base64.b64encode(data).decode('utf-8')
    return code


@asynccontextmanager
async def async_http(url: str, method: Literal['get', 'post'], headers: dict=None, 
                    params: dict=None, data: dict=None) -> AsyncGenerator[aiohttp.ClientResponse, None]:
    async with aiohttp.ClientSession(headers=headers) as http_session:
        kwargs = {}
        if params: 
            kwargs['params'] = params
        if method == 'get':
            async with http_session.get(url, **kwargs) as resp:
                yield resp
        else:
            async with http_session.post(url, data=data, **kwargs) as resp:
                yield resp