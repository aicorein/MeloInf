import os
import pickle
from typing import Union

from melobot import session


def save_restart_rec(plugin_root: str, rec_name: str) -> None:
    with open(os.path.join(plugin_root, rec_name), 'wb') as fp:
        pickle.dump([
            session.event.sender.id,
            session.event.is_private(),
            session.event.group_id
        ], fp)


def read_restart_rec(plugin_root: str, rec_name: str) -> Union[None, tuple]:
    path = os.path.join(plugin_root, rec_name)
    if not os.path.exists(path):
        return None
    with open(path, 'rb') as fp:
        obj = pickle.load(fp)
    os.remove(path)
    return obj
