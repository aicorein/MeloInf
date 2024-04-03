from melobot import ForwardWsConn, HttpConn, MeloBot, ReverseWsConn

if __name__ == "__main__":
    bot = MeloBot("MeloInf")
    # conn = ForwardWsConn("127.0.0.1", 8080, allow_reconnect=True)
    conn = ReverseWsConn("127.0.0.1", "9090", allow_reconnect=True)
    # conn = HttpConn(
    #     "127.0.0.1", 10101, "127.0.0.1", 10100, allow_reconnect=True, max_interval=6
    # )
    bot.init(conn, log_level="DEBUG")
    bot.load_plugins("plugins")
    bot.run()
