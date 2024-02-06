from melobot import this_dir
from typing import Dict, List


with open(this_dir('./words.txt'), encoding='utf-8') as fp:
    alist = fp.readlines()
alist = map(lambda x: x.rstrip('\n').split('##'), alist)
adict: Dict[str, List[str]] = {}
for k, v in alist:
    dict_val = adict.get(k)
    if dict_val is None:
        adict[k] = [v]
    else:
        dict_val.append(v)

WORD_DICT = adict
BOT_FLAG = '$$bot$$'
SENDER_FLAG = '$$sender$$'
OWNER_FLAG = '$$owner$$'
