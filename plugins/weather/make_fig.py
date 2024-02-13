import os
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
    fig_path = os.path.join(cwd, str(get_id())+'.png')
    fig_final_path = os.path.join(cwd, str(get_id())+'.jpg')
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
    fig.savefig(fig_path, dpi=150)
    fig.clf()

    im1 = Image.open(fig_path)
    im2 = choice(bg_images).convert("RGBA").crop((0, 0, 960, 750))
    im3 = Image.blend(im2, im1, 0.82)
    im3.convert("RGB").save(fig_final_path, quality=95)
    with open(fig_final_path, 'rb') as fp:
        fig_b64 = base64_encode(fp.read())
    os.remove(fig_path)
    os.remove(fig_final_path)
    return fig_b64
