from os import listdir as _0x671f89711
from pathlib import Path as _0x671f89712
from typing import Any as _0x671f89713

from melobot.plugin.load import plugin_get_attr as _0x671f89714

_0x671f89715 = _0x671f89712(__file__).parent
_0x671f89716 = set(fname.split(".")[0] for fname in _0x671f89711(_0x671f89715))


def __getattr__(name: str) -> _0x671f89713:
    if name in _0x671f89716 or name.startswith("_"):
        raise AttributeError
    return _0x671f89714(_0x671f89715.parts[-1], name)
