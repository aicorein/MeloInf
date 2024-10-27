from melobot.plugin import SyncShare


class Store:
    onebot_name: str = "<尚未获取>"
    onebot_id: int = -1
    onebot_app_name: str = "<尚未获取>"
    onebot_app_ver: str = "<尚未获取>"
    onebot_protocol_ver: str = "<尚未获取>"
    onebot_other_infos: dict[str, str] = {}


def add_share(name: str) -> SyncShare:
    return SyncShare(name, lambda: getattr(Store, name), static=True)


onebot_name: SyncShare[str] = add_share("onebot_name")
onebot_id: SyncShare[int] = add_share("onebot_id")
onebot_app_name: SyncShare[str] = add_share("onebot_app_name")
onebot_app_ver: SyncShare[str] = add_share("onebot_app_ver")
onebot_protocol_ver: SyncShare[str] = add_share("onebot_protocol_ver")
onebot_other_infos: SyncShare[dict[str, str]] = add_share("onebot_other_infos")
