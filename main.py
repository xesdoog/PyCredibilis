from keyboard import is_pressed, add_hotkey
from time import sleep
from threading import Thread
from winsound import PlaySound
from utils.input import (
    block_direction,
    parry,
    deflect,
    allguard,
    flip,
    force_reset_gamepad
)
from utils.screenscan import (
    screen_scan,
    flash_state,
    eIndicatorState,
    LOCK,
)


should_pause = False

_prev_state = {
    "Top":   eIndicatorState.IDLE,
    "Left":  eIndicatorState.IDLE,
    "Right": eIndicatorState.IDLE,
}

auto_counters = {
    "auto_parry":    "e",
    "auto_deflect":  "a",
    "auto_flip":     "x",
    "auto_allguard": "w",
}

auto_counter_callbacks = {
    "auto_parry":    parry,
    "auto_deflect":  deflect,
    "auto_flip":     flip,
    "auto_allguard": allguard
}


def play_sound(path: str):
    PlaySound(path, 0x20000 | 0x1)

    
def toggle():
    global should_pause

    should_pause = not should_pause
    play_sound("./sounds/toggle.wav")

    for direction, _ in _prev_state.items():
        _prev_state[direction] = eIndicatorState.IDLE

    with LOCK:
        for direction, _ in flash_state.items():
            flash_state[direction] = eIndicatorState.IDLE
    force_reset_gamepad()


def scan_loop():
    global should_pause

    while True:
        if should_pause:
            sleep(1)
            continue
        screen_scan()


def start_scanner():
    Thread(target=scan_loop, daemon=True).start()


def main():
    global _prev_state

    with LOCK:
        for direction, state in flash_state.items():
            recent_input = False
            if should_pause:
                flash_state[direction] = eIndicatorState.IDLE
                break

            if state != eIndicatorState.IDLE and _prev_state[direction] == eIndicatorState.IDLE:
                block_direction(direction)

            if state == eIndicatorState.FLASHING and _prev_state[direction] != eIndicatorState.FLASHING:
                for option, button in auto_counters.items():
                    if is_pressed(button) and not recent_input:
                        recent_input = True
                        auto_counter_callbacks[option](direction)
                        break

            _prev_state[direction] = state
            recent_input = False


if __name__ == "__main__":
    add_hotkey("p", toggle)
    start_scanner()

    while True:
        try:
            sleep(0.01)
            if should_pause:
                sleep(1)
                continue
            main()

        except Exception as e:
            print(e)
            exit(1)
