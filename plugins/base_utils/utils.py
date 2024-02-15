from PIL import Image, ImageFont, ImageDraw
from typing import Tuple, List

from ..env import BOT_INFO


def txt2img(text: str, font_size: int=18, bg_color: str="white", color: str="black",
            margin: Tuple[int, int]=[10, 10], align: str="left") -> Image.Image:
    font = ImageFont.truetype(BOT_INFO.txt2img_font, size=font_size)
    img = Image.new("RGB", (1000, 1000))
    draw = ImageDraw.Draw(img)
    left, top, right, bottom = draw.multiline_textbbox((0, 0), text, font)
    width, height = right - left, bottom - top
    if margin:
        width += 2*margin[0]
        height += 2*margin[1]
    img = Image.new("RGB", (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)
    draw_point = (0+margin[0], 0+margin[1]) if margin else (0, 0)
    draw.multiline_text(draw_point, text, font=font, fill=color, align=align)
    return img


def wrap_s(s: str, wrap_len: int) -> List[str]:
    return [s[i:i+wrap_len] for i in range(0, len(s), wrap_len)]
