from melobot import AttrSessionRule as AttrRule
from melobot import BotPlugin
from melobot import CmdArgFormatter as Format
from melobot import NoticeChecker, send, send_reply, thisbot

from ..env import COMMON_CHECKER, PARSER_FACTORY, get_owner_checker, get_su_checker

plugin = BotPlugin("TestUtils", version="2.0.0")


class PluginSpace:
    async_t = (1, 6)
    session_simulate_t = 1
    session_overtime_t = 10
    test_cnt = 0

    io_debug_flag = False


class PluginRef:
    async def bot_id() -> int:
        return await thisbot.get_share("BaseUtils", "bot_id").val


atest = plugin.on_message(
    checker=get_su_checker(fail_cb=lambda: send_reply("你无权使用【异步测试】功能")),
    parser=PARSER_FACTORY.get(targets=["异步测试", "atest", "async-test"]),
)

test_n = plugin.on_message(
    checker=get_su_checker(fail_cb=lambda: send_reply("你无权使用【测试统计】功能")),
    parser=PARSER_FACTORY.get(targets=["测试统计", "testn", "test-stat"]),
)

stest = plugin.on_message(
    checker=get_su_checker(fail_cb=lambda: send_reply("你无权使用【会话测试】功能")),
    session_rule=AttrRule("sender", "id"),
    direct_rouse=True,
    conflict_wait=False,
    conflict_cb=lambda: send("其他的会话测试进行中...稍后再试"),
    parser=PARSER_FACTORY.get(targets=["会话测试", "stest", "session-test"]),
)

io_debug = plugin.on_message(
    checker=get_su_checker(fail_cb=lambda: send_reply("你无权使用【io 调试】功能")),
    parser=PARSER_FACTORY.get(
        targets=["io调试", "io-debug"],
        formatters=[
            Format(
                convert=lambda x: bool(int(x)),
                src_desc="开关值",
                src_expect="1 或 0",
            )
        ],
    ),
)

core_debug = plugin.on_message(
    checker=get_owner_checker(fail_cb=lambda: send_reply("你无权使用【核心调试】功能")),
    parser=PARSER_FACTORY.get(targets=["核心调试", "core-debug"]),
    session_rule=AttrRule("sender", "id"),
    direct_rouse=True,
    conflict_wait=False,
    conflict_cb=lambda: send("已进入核心调试状态， 拒绝重复进入该状态"),
)

echo = plugin.on_message(
    checker=get_su_checker(fail_cb=lambda: send_reply("你无权使用【复读】功能")),
    parser=PARSER_FACTORY.get(
        targets=["复读", "echo"],
        formatters=[
            Format(
                verify=lambda x: len(x) <= 100,
                src_desc="复读的内容",
                src_expect="字符数 <= 100",
                default="Hello World!",
            )
        ],
    ),
)

get_img_url = plugin.on_message(
    checker=COMMON_CHECKER,
    parser=PARSER_FACTORY.get(
        targets=["get-img", "获取图片"],
    ),
)

poke = plugin.on_notice(checker=COMMON_CHECKER & NoticeChecker(lambda e: e.is_poke()))
