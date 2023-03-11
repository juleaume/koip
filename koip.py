import socket
import time
from enum import Enum, auto

from rich.console import Console

from src.utils import (
    make_keyboard_trame,
    ControlKeys,
    make_mouse_trame,
    CONTROL_KEYS,
)

console = Console()

DEFAULT_IP = "192.168.4.1"
DEFAULT_PORT = 5000


class Commands(Enum):
    slack = auto()
    chrome = auto()
    term = auto()


COMMANDS = {_c.name: _c for _c in Commands}


def connect(
    ip: str = DEFAULT_IP, port: int = DEFAULT_PORT
) -> socket.socket | None:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect((ip, port))
        console.print("Connected", style="green")
        return sock
    except OSError:
        console.print("Network is unreachable", style="red")
        return None


MENU = (
    "[bold][blue]M[/bold]: Message[/blue]\n"
    "[bold][cyan]C[/bold]: Command[/cyan]\n"
    "[bold][magenta]S[/bold]: Mouse[/magenta]\n"
    "[bold][red]Q[/bold]: Quit[/red]\n> "
)


def main():
    console.rule("Keyboard Over Internet Protocol")
    console.print("Connect to distant keyboard")
    _ip = console.input(f"IP ({DEFAULT_IP}):\n> ")
    _ip = _ip if _ip else DEFAULT_IP
    _port = console.input(f"Port ({DEFAULT_PORT}):\n> ")
    _port = int(_port) if _port else DEFAULT_PORT
    if (sock := connect(_ip, _port)) is None:
        return None
    while (opt := console.input(MENU)) != "Q":
        match opt:
            case "M":
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
                sock.send(make_keyboard_trame(header, message, footer))
            case "C":
                cmd = console.input("Command:\n> ")
                if cmd in COMMANDS.keys():
                    keyboard_command(COMMANDS[cmd], sock)
                else:
                    console.print(f"Unknown command: {cmd}")
            case "S":
                ud = console.input("VERTICAL:\n> ")
                lr = console.input("HORIZONTAL:\n> ")
                wh = console.input("WHEEL:\n> ")
                sock.send(make_mouse_trame(int(ud), int(lr), int(wh)))
            case _:
                console.print(f"Unknown option: {opt}")


def keyboard_command(cmd: Commands, sock: socket.socket | None) -> None:
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
                ((set(), "t", {ControlKeys.ctrl, ControlKeys.alt}), 1),
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
        trame = make_keyboard_trame(*_command)
        console.print(f"sending {trame}")
        sock.send(trame)
        time.sleep(_timeout)


if __name__ == "__main__":
    main()
