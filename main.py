import sys

sys.path.append(r"E:\projects\Python\git-proj\melobot")
from melobot import MeloBot

bot = MeloBot()
bot.init("./config")
bot.load_plugins("./plugins")
bot.run()
