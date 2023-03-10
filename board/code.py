import os
import time
import wifi
import board
import usb_hid
import digitalio
import socketpool
from adafruit_hid.mouse import Mouse
from adafruit_hid.keycode import Keycode
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS

SPECIAL_KEYS = {
    0x11: Keycode.LEFT_CONTROL,
    0x12: Keycode.LEFT_GUI,
    0x13: Keycode.LEFT_ALT,
    0x14: Keycode.RIGHT_ALT,
}

KEYBOARD_KEYS = {
    0x09: Keycode.TAB,
    0x0A: Keycode.RETURN,
}


TRAME = {
    0x01: "HEADER",
    0x02: "MESSAGE",
    0x03: "FOOTER",
    0x04: "EOT",
}

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT
led.value = True


def blink():
    led.value = not led.value


mouse = Mouse(usb_hid.devices)
blink()
keyboard = Keyboard(usb_hid.devices)
blink()
k_layout = KeyboardLayoutUS(keyboard)
blink()
# wifi.radio.start_ap(os.getenv("WIFI_SSID"), os.getenv("WIFI_PASSWORD"))
try:
    wifi.radio.start_ap("pico", "theotheo")
except NotImplementedError:
    print("Network is already up")
print(wifi.radio.ipv4_address_ap)
blink()
pool = socketpool.SocketPool(wifi.radio)
blink()
sock = pool.socket(pool.AF_INET, pool.SOCK_DGRAM)
blink()
sock.bind(("", 5000))
buffer = bytearray(1024)
current_portion = "EOT"
led.value = True
while True:
    r = sock.recv_into(buffer)
    # message format is
    # \x01CTRL?GUI?ALT?ALTGR?\x02MESSAGE\x03CTRL?GUI?ALT?ALTGR?\x04
    # [ H E A D E R]          [MESSAGE]     [ F O O T E R ]
    # The header presses the control keys
    # the message writes keyboards
    # the footer releases the control keys
    message = buffer[: (r + 1)]
    for char in message:
        led.value = not led.value
        if char in TRAME.keys():
            current_portion = TRAME[char]
            continue
        elif current_portion == "HEADER":
            _key = SPECIAL_KEYS.get(char, 0)
            print(f"pressing {_key}")
            keyboard.press(_key)
        elif current_portion == "MESSAGE":
            print("MESSAGE TIME")
            if char >= 0x20:
                print(f"writing {chr(char)}")
                k_layout.write(chr(char))
            else:
                if char in SPECIAL_KEYS.keys():
                    _key = SPECIAL_KEYS[char]
                elif char in KEYBOARD_KEYS.keys():
                    _key = KEYBOARD_KEYS[char]
                else:
                    print(f"Unknown char: {char}")
                    continue
                print(f"sending {_key} (0x{char:02X})")
                keyboard.send(_key)

        elif current_portion == "FOOTER":
            _key = SPECIAL_KEYS.get(char, 0)
            print(f"releasing {_key}")
            keyboard.release(_key)
        elif current_portion == "EOT":
            print("BYE-BYE")
            break
        else:
            print("EH??? TIME")
            continue
