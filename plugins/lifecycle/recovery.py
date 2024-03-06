import os
import pickle
from typing import Optional

from melobot import msg_event


def save_rec(plugin_root: str, rec_name: str) -> None:
    with open(os.path.join(plugin_root, rec_name), "wb") as fp:
        event = msg_event()
        pickle.dump(
            [
                event.sender.id,
                event.is_private(),
                event.group_id,
            ],
            fp,
        )


def read_rec(plugin_root: str, rec_name: str) -> Optional[tuple]:
    path = os.path.join(plugin_root, rec_name)
    if not os.path.exists(path):
        return None
    with open(path, "rb") as fp:
        obj = pickle.load(fp)
    os.remove(path)
    return obj
