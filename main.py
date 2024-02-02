from melobot import MeloBot
from plugins.test_utils import TestUtils
from plugins.base_utils import BaseUtils
from plugins.basic_info import BasicInfo
from plugins.code_compile import CodeCompiler


bot = MeloBot()
bot.init("./config")
bot.load(BaseUtils)
bot.load(TestUtils)
bot.load(BasicInfo)
bot.load(CodeCompiler)
bot.run()
