import socket
import time
from enum import Enum, auto

from rich.console import Console

console = Console()

DEFAULT_IP = "192.168.4.1"
DEFAULT_PORT = 5000


class Commands(Enum):
    slack = auto()
    chrome = auto()
    term = auto()


COMMANDS = {_c.name: _c for _c in Commands}


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


def make_trame(
    cmds_in: set[ControlKeys], message: str, cmds_out: set[ControlKeys]
) -> bytes:
    trame = "\x01"
    for ctrl in cmds_in:
        trame += ctrl.value
    trame += "\x02"
    special = False
    for c in message:
        if c == "$":
            special = True
        elif special:
            trame += CONTROL_KEYS.get(c, ControlKeys.default).value
            special = False
        else:
            trame += c
    trame += "\x03"
    for ctrl in cmds_out:
        trame += ctrl.value
    trame += "\x04"
    return trame.encode()


def connect(ip: str = DEFAULT_IP, port: int = DEFAULT_PORT) -> socket.socket:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect((ip, port))
    console.print("Connected", style="green")
    return sock


MENU = (
    "[bold][blue]M[/bold]: Message[/blue]\n"
    "[bold][cyan]C[/bold]: Command[/cyan]\n"
    "[bold][red]Q[/bold]: Quit[/red]\n> "
)


def main():
    console.rule("Keyboard Over Internet Protocol")
    console.print("Connect to distant keyboard")
    _ip = console.input(f"IP ({DEFAULT_IP}):\n> ")
    _ip = _ip if _ip else DEFAULT_IP
    _port = console.input(f"Port ({DEFAULT_PORT}):\n> ")
    _port = int(_port) if _port else DEFAULT_PORT
    sock = connect(_ip, _port)
    while (opt := console.input(MENU)) != "Q":
        if opt == "M":
            header = set()
            footer = set()
            msg = console.input("Header to send:\n> ")
            for c in msg:
                if c in CONTROL_KEYS.keys():
                    header.add(CONTROL_KEYS[c])
            message = console.input("Message to send:\n> ")
            msg = console.input("Footer to send:\n> ")
            for c in msg:
                if c in CONTROL_KEYS.keys():
                    footer.add(CONTROL_KEYS[c])
            sock.send(make_trame(header, message, footer))
        elif opt == "C":
            cmd = console.input("Command:\n> ")
            if cmd in COMMANDS.keys():
                command(COMMANDS[cmd], sock)
            else:
                console.print(f"Unknown command: {cmd}")
        else:
            console.print(f"Unknown option: {opt}")


def command(cmd: Commands, sock: socket.socket | None) -> None:
    if sock is None:
        sock = connect()
    match cmd:
        case Commands.chrome:
            cmds = [
                (("", "$G", ""), 1),
                (("", "chr$E", ""), 0.1),
            ]
        case Commands.term:
            cmds = [
                (({ControlKeys.ctrl, ControlKeys.alt}, "", set()), 0.5),
                ((set(), "t", {ControlKeys.ctrl, ControlKeys.alt}), 0.1),
            ]
        case Commands.slack:
            cmds = [
                ((set(), "$G", set()), 0.5),
                ((set(), "slack$E", set()), 1),
                ((set(), "$Ck", set()), 0.5),
                ((set(), "general$E", set()), 0.5),
                ((set(), "Je ramene le prochain petit dej$E", set()), 0.5),
            ]
        case _:
            cmds = []
    for _command, _timeout in cmds:
        trame = make_trame(*_command)
        console.print(f"sending {trame}")
        sock.send(trame)
        time.sleep(_timeout)


if __name__ == "__main__":
    main()
