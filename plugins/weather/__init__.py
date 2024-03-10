from melobot import ArgFormatter as Format
from melobot import Plugin, finish, lock, msg_args, send, send_reply, timelimit
from melobot.models import image_msg

from ..env import BOT_INFO, COMMON_CHECKER, PARSER_GEN
from ..public_utils import async_http, get_headers
from .make_fig import gen_weather_fig

weather = Plugin.on_message(
    checker=COMMON_CHECKER,
    parser=PARSER_GEN.gen(
        target=["天气", "weather"],
        formatters=[
            Format(
                verify=lambda x: len(x) <= 10,
                src_desc="城市名",
                src_expect="字符数 <= 10",
            ),
            Format(
                convert=int,
                verify=lambda x: 1 <= x <= 7,
                src_desc="需要预报的天数",
                src_expect="1<=天数<=7",
                default=3,
            ),
        ],
    ),
)


class WeatherUtils(Plugin):
    def __init__(self) -> None:
        super().__init__()
        self.api_key = BOT_INFO.weather_key
        self.city_lookup_url = "https://geoapi.qweather.com/v2/city/lookup"
        self.weather_now_url = "https://devapi.qweather.com/v7/weather/now"
        self.weather_7d_url = "https://devapi.qweather.com/v7/weather/7d"

    @weather
    @lock(lambda: send("请等待前一个天气获取任务完成，稍后再试~"))
    @timelimit(lambda: send_reply("天气信息获取超时，请稍候再试..."), timeout=25)
    async def weather(self) -> None:
        city, days = msg_args()
        text_box = []
        min_temps, max_temps = [], []

        async with async_http(
            self.city_lookup_url,
            "get",
            headers=get_headers(),
            params={"location": city, "key": self.api_key},
        ) as resp:
            if resp.status != 200:
                await send_reply("城市 id 查询失败...请稍后再试，或联系 bot 管理员解决")
                self.LOGGER.error(f"请求失败：{resp.status}")
                return
            else:
                res = await resp.json()

        if res["code"] == "404" or "location" not in res.keys():
            await finish(f"检索不到城市 {city}，请检查输入哦~")
        link = res["location"][0]["fxLink"]
        city_id = res["location"][0]["id"]

        async with async_http(
            self.weather_now_url,
            "get",
            headers=get_headers(),
            params={"location": city_id, "key": self.api_key},
        ) as resp:
            if resp.status != 200:
                await send_reply(
                    "城市当前天气获取失败...请稍后再试，或联系 bot 管理员解决"
                )
                self.LOGGER.error(f"请求失败：{resp.status}")
                return
            else:
                res = await resp.json()

        text_box.append(res["now"]["text"] + " " + res["now"]["temp"] + " 度")

        async with async_http(
            self.weather_7d_url,
            method="get",
            headers=get_headers(),
            params={"location": city_id, "key": self.api_key},
        ) as resp:
            if resp.status != 200:
                await send_reply(
                    "城市多天天气获取失败...请稍后再试，或联系 bot 管理员解决"
                )
                self.LOGGER.error(f"请求失败：{resp.status}")
                return
            else:
                res = await resp.json()

        for data in res["daily"]:
            text_box.append(
                " ● "
                + data["textDay"]
                + " "
                + data["tempMin"]
                + " ~ "
                + data["tempMax"]
                + " 度"
            )
            min_temps.append(int(data["tempMin"]))
            max_temps.append(int(data["tempMax"]))
        output = f"城市 {city}：\n【今日天气】{text_box[0]}\n【近 {days} 天天气（包括今天）】\n"
        output += "\n".join(text_box[1 : days + 1])
        output += f"\n【详细参见】{link}"
        await send(output)
        fig_b64 = gen_weather_fig(min_temps[:days], max_temps[:days])
        await send(image_msg(fig_b64), wait=True)
