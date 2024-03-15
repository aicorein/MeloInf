from melobot import BotLogger, ForwardWsConn, MeloBot

bot = MeloBot("MeloInf")
conn = ForwardWsConn("127.0.0.1", 8080)
bot_logger = BotLogger("MeloInf", "DEBUG", to_dir="./logs")
bot.init(conn, bot_logger)
bot.load_plugins("plugins")
MeloBot.start(bot)
