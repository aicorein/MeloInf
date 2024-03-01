from typing import List, Tuple, Union

import toml

from melobot import CmdParserGen, MsgCheckerGen, User, this_dir

settings_path = this_dir("./settings.toml")
with open(settings_path, encoding="utf-8") as fp:
    SETTINGS = toml.load(fp)

CONFIG = SETTINGS["bot_config"]


class BotInfo:
    def __init__(self) -> None:
        self.name: str = CONFIG["bot_proj_name"]
        self.ver: str = CONFIG["bot_proj_ver"]
        self.src: str = CONFIG["bot_proj_src"]
        self.bot_name: str = CONFIG["bot_name"]
        self.bot_nickname: str = CONFIG["bot_nickname"]
        self.uni_cmd_start: Union[str, List[str]] = CONFIG["uni_cmd_start"]
        self.uni_cmd_sep: Union[str, List[str]] = CONFIG["uni_cmd_sep"]
        self.uni_default_flag: str = CONFIG["uni_default_flag"]
        self.owner: int = CONFIG["owner"]
        self.super_users: List[int] = CONFIG["super_users"]
        self.white_users: List[int] = CONFIG["white_users"]
        self.black_users: List[int] = CONFIG["black_users"]
        self.white_groups: List[int] = CONFIG["white_groups"]
        self.figure_font: str = CONFIG["figure_font"]
        self.weather_key: str = CONFIG["weather_key"]
        self.dice_base_r: Tuple[int, int] = tuple(CONFIG["dice_base_r"])
        self.txt2img_font: str = CONFIG["txt2img_font"]
        self.baidu_translate_appid = CONFIG["baidu_translate_appid"]
        self.baidu_translate_key = CONFIG["baidu_translate_key"]
        self.hash_salt = CONFIG["hash_salt"]


BOT_INFO = BotInfo()

CHECKER_GEN = MsgCheckerGen(
    owner=BOT_INFO.owner,
    super_users=BOT_INFO.super_users,
    white_users=BOT_INFO.white_users,
    black_users=BOT_INFO.black_users,
    white_groups=BOT_INFO.white_groups,
)
PARSER_GEN = CmdParserGen(BOT_INFO.uni_cmd_start, BOT_INFO.uni_cmd_sep)

OWNER_CHECKER = CHECKER_GEN.gen_group(User.OWNER) | CHECKER_GEN.gen_private(User.OWNER)
SU_CHECKER = CHECKER_GEN.gen_group(User.SU) | CHECKER_GEN.gen_private(User.SU)
WHITE_CHECKER = CHECKER_GEN.gen_group(User.WHITE) | CHECKER_GEN.gen_private(User.WHITE)
COMMON_CHECKER = CHECKER_GEN.gen_group() | CHECKER_GEN.gen_private()
