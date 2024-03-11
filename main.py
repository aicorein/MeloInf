import sys

sys.path.append("..")

from melobot import MeloBot

bot = MeloBot()
bot.init("./config")
bot.load_plugins("./plugins")
bot.run()
