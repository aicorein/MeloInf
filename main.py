import sys

sys.path.append("../src")

from plugins.env import BOT_INFO

from melobot import *

if __name__ == "__main__":
    bot = MeloBot("MeloInf")
    conn = ReverseWsConn(
        "127.0.0.1", 9090, allow_reconnect=True, access_token=BOT_INFO.access_token
    )
    # conn = ForwardWsConn("127.0.0.1", 8080, allow_reconnect=True)
    # conn = HttpConn("127.0.0.1", 10101, "127.0.0.1", 10100, allow_reconnect=True)
    bot.init(conn, log_to_dir="./logs", log_level="DEBUG")
    bot.load_plugins("plugins")
    bot.run()


# p = BotPlugin("test", "1.0.0")
# @p.on_message(parser=CmdParser("/", " ", ["ask", "ASK", "Ask"]))
# async def test() -> None:
#     args = msg_args()
#     await send_reply(args)


# bot = MeloBot(__name__)
# bot.init(ForwardWsConn("127.0.0.1", 8080, allow_reconnect=True), log_level="DEBUG")
# bot.load_plugin(p)
# bot.run()
