from typing import Any, Callable, Coroutine, List, Tuple

import toml

from melobot import CmdParserGen, MsgCheckerGen, User, this_dir

settings_path = this_dir("./settings.toml")
with open(settings_path, encoding="utf-8") as fp:
    SETTINGS = toml.load(fp)

CONFIG = SETTINGS["bot_config"]


class BotInfo:
    def __init__(self) -> None:
        self.proj_name: str = CONFIG["bot_proj_name"]
        self.proj_ver: str = CONFIG["bot_proj_ver"]
        self.proj_src: str = CONFIG["bot_proj_src"]
        self.bot_name: str = CONFIG["bot_name"]
        self.bot_nickname: str = CONFIG["bot_nickname"]
        self.uni_cmd_start: str | list[str] = CONFIG["uni_cmd_start"]
        self.uni_cmd_sep: str | list[str] = CONFIG["uni_cmd_sep"]
        self.uni_default_flag: str = CONFIG["uni_default_flag"]
        self.owner: int = CONFIG["owner"]
        self.super_users: List[int] = CONFIG["super_users"]
        self.white_users: List[int] = CONFIG["white_users"]
        self.black_users: List[int] = CONFIG["black_users"]
        self.white_groups: List[int] = CONFIG["white_groups"]
        self.request_proxy: str = CONFIG["request_proxy"]
        self.figure_font: str = CONFIG["figure_font"]
        self.weather_key: str = CONFIG["weather_key"]
        self.dice_base_r: Tuple[int, int] = tuple(CONFIG["dice_base_r"])
        self.txt2img_font: str = CONFIG["txt2img_font"]
        self.baidu_translate_appid: str = CONFIG["baidu_translate_appid"]
        self.baidu_translate_key: str = CONFIG["baidu_translate_key"]
        self.hash_salt: str = CONFIG["hash_salt"]
        self.news_time: str = CONFIG["everyday_news_time"]
        self.news_gruop: List[int] = CONFIG["everyday_news_group"]


BOT_INFO = BotInfo()

CHECKER_GEN = MsgCheckerGen(
    owner=BOT_INFO.owner,
    super_users=BOT_INFO.super_users,
    white_users=BOT_INFO.white_users,
    black_users=BOT_INFO.black_users,
    white_groups=BOT_INFO.white_groups,
)
PARSER_GEN = CmdParserGen(BOT_INFO.uni_cmd_start, BOT_INFO.uni_cmd_sep)


def _auto_fill(checker, ok_cb, fail_cb):
    if ok_cb is not None:
        checker._fill_ok_cb(ok_cb)
    if fail_cb is not None:
        checker._fill_fail_cb(fail_cb)


def get_owner_checker(
    ok_cb: Callable[[], Coroutine[Any, Any, None]] = None,
    fail_cb: Callable[[], Coroutine[Any, Any, None]] = None,
):
    """
    获得一个 owner 级别的权限检查器
    """
    checker = CHECKER_GEN.gen_group(User.OWNER) | CHECKER_GEN.gen_private(User.OWNER)
    _auto_fill(checker, ok_cb, fail_cb)
    return checker


def get_su_checker(
    ok_cb: Callable[[], Coroutine[Any, Any, None]] = None,
    fail_cb: Callable[[], Coroutine[Any, Any, None]] = None,
):
    """
    获得一个 superuser 级别的权限检查器
    """
    checker = CHECKER_GEN.gen_group(User.SU) | CHECKER_GEN.gen_private(User.SU)
    _auto_fill(checker, ok_cb, fail_cb)
    return checker


def get_white_checker(
    ok_cb: Callable[[], Coroutine[Any, Any, None]] = None,
    fail_cb: Callable[[], Coroutine[Any, Any, None]] = None,
):
    """
    获得一个 white_user 级别的权限检查器
    """
    checker = CHECKER_GEN.gen_group(User.WHITE) | CHECKER_GEN.gen_private(User.WHITE)
    _auto_fill(checker, ok_cb, fail_cb)
    return checker


COMMON_CHECKER = CHECKER_GEN.gen_group() | CHECKER_GEN.gen_private()
