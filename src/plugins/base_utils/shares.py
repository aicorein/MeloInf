from melobot.plugin import SyncShare


class Store:
    bot_info: str = (
        "[Core]\n"
        "name：{}\n"
        "core：{} {}\n"
        "proj：{} {}\n"
        "src：{}\n"
        "python：{} | {}\n"
        "adapters：{}\n"
        "plugins：{}"
    )
    onebot_name: str = "<unkown>"
    onebot_id: int = -1
    onebot_app_name: str = "<unkown>"
    onebot_app_ver: str = "<unkown>"
    onebot_protocol_ver: str = "<unkown>"
    onebot_other_infos: dict[str, str] = {}
    onebot_info_str: str = (
        "[OneBot]\n"
        "app：{}\n"
        "ver：{}\n"
        "protocol_ver：{}\n"
        "other_info：{}"
    )


def add_share(name: str) -> SyncShare:
    return SyncShare(name, lambda: getattr(Store, name), static=True)


onebot_name: SyncShare[str] = add_share("onebot_name")
onebot_id: SyncShare[int] = add_share("onebot_id")
onebot_app_name: SyncShare[str] = add_share("onebot_app_name")
onebot_app_ver: SyncShare[str] = add_share("onebot_app_ver")
onebot_protocol_ver: SyncShare[str] = add_share("onebot_protocol_ver")
onebot_other_infos: SyncShare[dict[str, str]] = add_share("onebot_other_infos")
