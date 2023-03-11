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
    ord("\t"): Keycode.TAB,
    ord("\n"): Keycode.RETURN,
}

TRAME = {
    0x01: "HEADER",
    0x02: "MESSAGE",
    0x03: "ETX",
    0x04: "EOT",
}

COMMAND_TYPE = {ord("K"): "KEYBOARD", ord("M"): "MOUSE", ord("C"): "CONFIGURE"}

SEND_TYPE = {
    ord("^"): "PRESS",
    ord("%"): "SEND",
    ord("$"): "RELEASE",
}

MOUSE_DIRECTION = {
    ord("V"): "VERTICAL",
    ord("H"): "HORIZONTAL",
    ord("W"): "WHEEL",
    ord("S"): "SEND"
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
    message = buffer[: (r + 1)]
    command_type = ""
    send_type = ""
    direction = ""
    up_down = ""
    left_right = ""
    wheel = ""
    for char in message:
        led.value = not led.value
        if char in TRAME.keys():
            current_portion = TRAME[char]
            if current_portion == "ETX":
                send_type = ""
        elif current_portion == "HEADER":
            command_type = COMMAND_TYPE.get(char, "")
        elif current_portion == "MESSAGE":
            if command_type == "KEYBOARD":
                # message format is
                # \x01K\x02press\x03\x02send\x03\x02release\x03\x04
                # press is keys to press down
                # send is keys to send
                # release is keys to release up
                if send_type == "PRESS":
                    # PRESS MODE
                    _key = SPECIAL_KEYS.get(char, 0)
                    keyboard.press(_key)
                elif send_type == "RELEASE":
                    # RELEASE MODE
                    _key = SPECIAL_KEYS.get(char, 0)
                    keyboard.release(_key)
                elif send_type == "SEND":
                    # SENDING MODE
                    if char >= 0x20:
                        k_layout.write(chr(char))
                    else:
                        if char in SPECIAL_KEYS.keys():
                            _key = SPECIAL_KEYS[char]
                        elif char in KEYBOARD_KEYS.keys():
                            _key = KEYBOARD_KEYS[char]
                        else:
                            continue
                        keyboard.send(_key)
                elif char in SEND_TYPE.keys():
                    send_type = SEND_TYPE[char]
                else:
                    continue
            elif command_type == "MOUSE":
                if char in MOUSE_DIRECTION.keys():
                    direction = MOUSE_DIRECTION[char]
                elif direction == "VERTICAL":
                    up_down += chr(char)
                elif direction == "HORIZONTAL":
                    left_right += chr(char)
                elif direction == "WHEEL":
                    wheel += chr(char)
                elif direction == "SEND":
                    if not left_right:
                        left_right = 0
                    if not up_down:
                        up_down = 0
                    if not wheel:
                        wheel = 0
                    mouse.move(int(left_right), int(up_down), )
        elif current_portion == "ETX":
            continue
        elif current_portion == "EOT":
            break
        else:
            continue
