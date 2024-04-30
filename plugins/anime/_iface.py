from melobot import AttrSessionRule, BotPlugin, send

from ..env import COMMON_CHECKER, PARSER_FACTORY

plugin = BotPlugin("AnimeSearcher", version="1.2.0")


class PluginSpace:
    bot_id: int = -1
    anime_search_url = "https://api.trace.moe/search?anilistInfo&cutBorders&url="


anime_recognize = plugin.on_message(
    checker=COMMON_CHECKER,
    parser=PARSER_FACTORY.get(["番剧识别", "anime"]),
    session_rule=AttrSessionRule("sender", "id"),
    direct_rouse=True,
    conflict_wait=False,
    conflict_cb=lambda: send("你已触发一个识番任务，拒绝再次触发"),
)
