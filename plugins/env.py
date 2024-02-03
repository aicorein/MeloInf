import toml
from copy import deepcopy

from melobot import MsgCheckerGen, CmdParserGen
from melobot import this_dir
from melobot import User

with open(this_dir("./auth.toml"), encoding='utf-8') as fp:
    CONFIG = toml.load(fp)
with open(this_dir("./settings.toml"), encoding="utf-8") as fp:
    SETTINGS = toml.load(fp)

class BotInfo:
    def __init__(self) -> None:
        self.name = SETTINGS['bot_proj_name']
        self.ver = SETTINGS['bot_proj_ver']
        self.src =SETTINGS['bot_proj_src']
        self.bot_nickname = SETTINGS['bot_nickname']
        self.uni_cmd_start = SETTINGS['uni_cmd_start']
        self.uni_cmd_sep = SETTINGS['uni_cmd_sep']
BOT_INFO = BotInfo()

CHECKER_GEN = MsgCheckerGen(owner=CONFIG['owner'],
                            super_users=CONFIG['super_users'],
                            white_users=CONFIG['white_users'],
                            black_users=CONFIG['black_users'],
                            white_groups=CONFIG['white_groups'])
PASER_GEN = CmdParserGen(BOT_INFO.uni_cmd_start, BOT_INFO.uni_cmd_sep)

OWNER_CHECKER = CHECKER_GEN.gen_group(User.OWNER) | CHECKER_GEN.gen_private(User.OWNER)
ADMIN_CHECKER = CHECKER_GEN.gen_group(User.SU) | CHECKER_GEN.gen_private(User.OWNER)
COMMON_CHECKER = CHECKER_GEN.gen_group() | CHECKER_GEN.gen_private()

def get_headers():
    return deepcopy(SETTINGS['request_headers'])
