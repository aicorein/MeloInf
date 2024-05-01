import sys

sys.path.append("../src/")
from plugins.env import BOT_INFO

from melobot import *

if __name__ == "__main__":
    bot = MeloBot("MeloInf")
    conn = ReverseWsConn(
        "127.0.0.1", 9088, reconnect=True, access_token=BOT_INFO.access_token
    )
    bot.init(conn, log_to_dir="./logs", log_level="INFO")
    bot.load_plugins("plugins")
    bot.run()
