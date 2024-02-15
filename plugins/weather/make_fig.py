import os
import io
import matplotlib.pyplot as plt
from random import choice
from PIL import Image
from math import floor, ceil
from typing import List, Tuple
from melobot import get_id, this_dir

from ..env import BOT_INFO
from ..public_utils import base64_encode

plt.rcParams['font.family'] = BOT_INFO.figure_font
plt.rcParams['axes.unicode_minus'] = False
cwd = this_dir()
bg_images: List[Image.Image] = []
bg_dir = os.path.join(cwd, 'bgs')
for filename in os.listdir(bg_dir):
    bg_images.append(Image.open(os.path.join(bg_dir, filename)))


def get_ylim(base_v: int, steps: int, min_t: int, max_t: int) -> Tuple[int, int]:
    fv = abs(min_t-base_v)/steps
    v = floor(fv)
    y_low = base_v+v*steps
    if fv == v:
        y_low -= steps
    fv = abs(max_t-base_v)/steps
    v = ceil(fv)
    y_up = base_v+v*steps
    if fv == v:
        y_up += steps
    return y_low, y_up


def gen_weather_fig(min_temps: List[int], max_temps: List[int]) -> str:
    data_len = len(min_temps)
    fig_id = get_id()
    min_t, max_t = min(min_temps), max(max_temps)
    lower_v, upper_v, steps = -100, 100, 4
    day_s, day_e = 1, data_len
    fig = plt.figure(num=fig_id, figsize=(6.4, 5))
    figio = io.BytesIO()
    imgio = io.BytesIO()
    ax = fig.gca()

    ax.set_xticks(range(day_s, day_e+1))
    ax.set_yticks(range(lower_v, upper_v+1, 4))
    ax.set_ylim(get_ylim(lower_v, steps, min_t, max_t))
    ax.set_xlim(day_s-0.5, day_e+0.5)
    ax.set_xlabel("第 n 天（包含今天）")
    ax.set_ylabel("温度（°C）")
    ax.plot(range(1, data_len+1), min_temps, marker='*', color="deepskyblue")
    ax.plot(range(1, data_len+1), max_temps, marker='*', color="deeppink")
    ax.grid(True, axis='y', linestyle='--')
    fig.savefig(figio, dpi=150)
    fig.clf()

    im1 = Image.open(figio)
    im2 = choice(bg_images).convert("RGBA").crop((0, 0, 960, 750))
    im3 = Image.blend(im2, im1, 0.82)
    im3.convert("RGB").save(imgio, format='JPEG', quality=95)
    fig_b64 = base64_encode(imgio.getvalue())
    return fig_b64
