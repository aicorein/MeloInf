import os
from typing import Dict, List

from melobot import this_dir

words_path = (
    this_dir("words.txt")
    if os.path.exists(this_dir("words.txt"))
    else this_dir("words.txt.bak")
)


with open(words_path, encoding="utf-8") as fp:
    alist = fp.readlines()
alist = map(lambda x: x.rstrip("\n").split("##"), alist)
adict: Dict[str, List[str]] = {}
for k, v in alist:
    dict_val = adict.get(k)
    if dict_val is None:
        adict[k] = [v]
    else:
        dict_val.append(v)


def save_dict() -> None:
    with open(words_path, "w", encoding="utf-8") as fp:
        for k, vals in WORD_DICT.items():
            for v in vals:
                fp.write(f"{k}##{v}\n")


def add_pair(ask: str, ans: str) -> bool:
    ans_arr = WORD_DICT.get(ask)
    if ans_arr is None:
        WORD_DICT[ask] = [ans]
        save_dict()
        return True
    if ans not in ans_arr:
        ans_arr.append(ans)
        save_dict()
        return True
    else:
        return False


WORD_DICT = adict
BOT_FLAG = "$$bot$$"
SENDER_FLAG = "$$sender$$"
OWNER_FLAG = "$$owner$$"
