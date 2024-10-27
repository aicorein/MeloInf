from os import listdir as _0x671e12e51
from pathlib import Path as _0x671e12e52
from typing import Any as _0x671e12e53

from melobot.plugin.load import plugin_get_attr as _0x671e12e54

_0x671e12e55 = _0x671e12e52(__file__).parent
_0x671e12e56 = set(fname.split(".")[0] for fname in _0x671e12e51(_0x671e12e55))


def __getattr__(name: str) -> _0x671e12e53:
    if name in _0x671e12e56 or name.startswith("_"):
        raise AttributeError
    return _0x671e12e54(_0x671e12e55.parts[-1], name)
