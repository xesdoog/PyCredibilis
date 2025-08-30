from vgamepad import VX360Gamepad, XUSB_BUTTON
from time import sleep


gamepad = VX360Gamepad()

DIRECTIONS = {
    "Top": (0.0, 1.0),
    "Left": (-1.0, 0.0),
    "Right": (1.0, 0.0)
}


def block_direction(direction: str):
    if direction not in DIRECTIONS:
        return

    gamepad.right_joystick_float(*DIRECTIONS[direction])
    gamepad.update()
    sleep(0.05)
    gamepad.right_joystick_float(0.0, 0.0)
    gamepad.update()


def parry(_):
    gamepad.right_trigger_float(1.0)
    gamepad.update()
    sleep(0.05)
    gamepad.right_trigger_float(0.0)
    gamepad.update()


def deflect(direction: str):
    if direction not in DIRECTIONS:
        return

    gamepad.left_joystick_float(*DIRECTIONS[direction])
    sleep(0.01)
    gamepad.press_button(XUSB_BUTTON.XUSB_GAMEPAD_A)
    gamepad.update()
    sleep(0.05)
    gamepad.release_button(XUSB_BUTTON.XUSB_GAMEPAD_A)
    gamepad.left_joystick_float(0.0, 0.0)
    gamepad.update()


def allguard(_):
    gamepad.right_joystick_float(0.0, -1.0)
    gamepad.update()
    sleep(0.5)
    gamepad.right_joystick_float(0.0, 0.0)
    gamepad.update()


def flip(_):
    gamepad.right_joystick_float(0.0, -1.0)
    gamepad.press_button(XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER)
    gamepad.update()
    sleep(0.2)
    gamepad.release_button(XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER)
    gamepad.right_joystick_float(0.0, 0.0)
    gamepad.update()


def force_reset_gamepad():
    gamepad.right_joystick_float(0.0, 0.0)
    gamepad.left_joystick_float(0.0, 0.0)
    gamepad.right_trigger_float(0.0)
    gamepad.release_button(XUSB_BUTTON.XUSB_GAMEPAD_A)
    gamepad.release_button(XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER)
    gamepad.update()
