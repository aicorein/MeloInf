import sys

sys.path.append("E:\\projects\\Python\\git-proj\\melobot_renew")
from melobot import MeloBot

bot = MeloBot()
bot.init("./config")
bot.load_plugins("./plugins")
bot.run()
