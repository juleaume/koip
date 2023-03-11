from enum import Enum


class ControlKeys(Enum):
    ctrl = "\x11"
    gui = "\x12"
    alt = "\x13"
    alt_gr = "\x14"
    tab = "\x09"
    enter = "\x0a"
    default = ""


CONTROL_KEYS = {
    "C": ControlKeys.ctrl,
    "G": ControlKeys.gui,
    "A": ControlKeys.alt,
    "R": ControlKeys.alt_gr,
    "E": ControlKeys.enter,
    "T": ControlKeys.tab,
}


def make_mouse_trame(up_down: int, left_right: int, wheel: int) -> bytes:
    trame = "\x01M"
    if up_down:
        trame += f"\x02V{up_down}\x03"
    if left_right:
        trame += f"\x02H{left_right}\x03"
    if wheel:
        trame += f"\x02W{wheel}\x03"
    trame += "\x02S!\x03\x04"
    return trame.encode()


def make_keyboard_trame(
    pressed: set[ControlKeys], message: str, released: set[ControlKeys]
) -> bytes:
    trame = "\x01K\x02^"
    for ctrl in pressed:
        trame += ctrl.value
    trame += "\x03\x02%"
    special = False
    for c in message:
        if c == "$":
            special = True
        elif special:
            trame += CONTROL_KEYS.get(c, ControlKeys.default).value
            special = False
        else:
            trame += c
    trame += "\x03\x02$"
    for ctrl in released:
        trame += ctrl.value
    trame += "\x03\x04"
    return trame.encode()
