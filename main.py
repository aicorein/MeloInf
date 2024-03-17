import sys

sys.path.append("../src")

from melobot import ForwardWsConn, MeloBot

if __name__ == "__main__":
    bot = MeloBot("MeloInf")
    conn = ForwardWsConn("127.0.0.1", 8080)
    bot.init(conn)
    bot.load_plugins("plugins")
    bot.run()
