import asyncio
import sys

if sys.platform != "win32":
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

sys.path.insert(0, "/home/melodyecho/projects/Python/git-proj/melobot/src")

from melobot import Bot
from melobot.log import Logger, LogLevel
from melobot.protocols.onebot.v11.adapter import Adapter
from melobot.protocols.onebot.v11.io import ForwardWebSocketIO

from env import ENVS

bot = Bot("meloinf", logger=Logger("meloinf", level=LogLevel.DEBUG))
bot.add_io(
    ForwardWebSocketIO(ENVS.onebot.forward_ws, access_token=ENVS.onebot.access_token)
)
bot.add_adapter(Adapter())
bot.load_plugins_dir("plugins", load_depth=3)
bot.run(debug=True)
