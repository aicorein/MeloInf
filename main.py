from melobot import MeloBot
from plugins.test_utils import TestUtils
from plugins.base_utils import BaseUtils
from plugins.code_compile import CodeCompiler
from plugins.random_pic import RandomPicGen


bot = MeloBot()
bot.init("./config")
bot.load(BaseUtils)
bot.load(TestUtils)
bot.load(CodeCompiler)
bot.load(RandomPicGen)
bot.run()
