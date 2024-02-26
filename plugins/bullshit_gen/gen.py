#!/usr/bin/python
# -*- coding: UTF-8 -*-
import random

from melobot import this_dir

from .readJSON import 读JSON文件

path = this_dir("data.json")


class Generator:
    DATA = 读JSON文件(path)

    def __init__(self, theme: str, words_len: int) -> None:
        self.名人名言 = Generator.DATA["famous"].copy()  # a 代表前面垫话，b代表后面垫话
        self.前面垫话 = Generator.DATA["before"].copy()  # 在名人名言前面弄点废话
        self.后面垫话 = Generator.DATA["after"].copy()  # 在名人名言后面弄点废话
        self.废话 = Generator.DATA["bosh"].copy()  # 代表文章主要废话来源
        self.xx = theme
        self.theme = theme
        self.重复度 = 2
        self.下一句废话 = self.洗牌遍历(self.废话)
        self.下一句名人名言 = self.洗牌遍历(self.名人名言)
        self.words_len = words_len

    def 洗牌遍历(self, 列表):
        池 = list(列表) * self.重复度
        while True:
            random.shuffle(池)
            for 元素 in 池:
                yield 元素

    def 来点名人名言(self):
        self.xx = next(self.下一句名人名言)
        self.xx = self.xx.replace("a", random.choice(self.前面垫话))
        self.xx = self.xx.replace("b", random.choice(self.后面垫话))
        return self.xx

    def 另起一段(self):
        self.xx = ". "
        self.xx += "\n"
        return self.xx

    def generate(self) -> str:
        tmp = str()
        while len(tmp) < self.words_len:
            分支 = random.randint(0, 100)
            if 分支 < 5:
                tmp += self.另起一段()
            elif 分支 < 20:
                tmp += self.来点名人名言()
            else:
                tmp += next(self.下一句废话)
        tmp = tmp.replace("x", self.theme)
        return tmp
