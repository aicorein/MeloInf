import sys

sys.path.append("../src/")
from melobot import *

if __name__ == "__main__":
    bot = MeloBot("MeloInf")
    conn = ReverseWsConn("127.0.0.1", 9090, reconnect=True)
    bot.init(conn, log_to_dir="./logs", log_level="DEBUG")
    bot.load_plugins("plugins")
    bot.run()
