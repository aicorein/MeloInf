import asyncio
import sys

import uvloop

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

sys.path.insert(0, "/home/melodyecho/projects/Python/git-proj/melobot/src")

from melobot import Bot
from melobot.log import Logger, LogLevel
from melobot.protocols.onebot.v11.adapter import Adapter
from melobot.protocols.onebot.v11.io import ForwardWebSocketIO

bot = Bot("meloinf", logger=Logger("meloinf", level=LogLevel.DEBUG, two_stream=True))
bot.add_io(ForwardWebSocketIO("ws://127.0.0.1:8080"))
bot.add_adapter(Adapter())
bot.load_plugins_dirs(["plugins"])
bot.run(debug=True)
