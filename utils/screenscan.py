import cv2
import numpy as np
import mss
from enum import Enum
from time import time
from threading import Lock

# debug
from keyboard import is_pressed


class eIndicatorState(Enum):
    IDLE     = 0x0,
    TRACKING = 0x1,
    FLASHING = 0x2


CROP_WIDTH  = 144
CROP_HEIGHT = 72
TIMEOUT_MS  = 1200
LOCK        = Lock()

lower_red   = np.array([0, 174, 215])
upper_red   = np.array([5, 254, 255])
lower_flash = np.array([0, 0, 220])
upper_flash = np.array([10, 50, 255])
MSSBase     = None

flash_state = {
    "Top":   eIndicatorState.IDLE,
    "Left":  eIndicatorState.IDLE,
    "Right": eIndicatorState.IDLE,
}

tracking_since = {
    "Top":   0,
    "Left":  0,
    "Right": 0,
}


def make_monitor(center_x, center_y, dx, dy):
    return {
        "top": center_y + dy - CROP_HEIGHT // 2,
        "left": center_x + dx - CROP_WIDTH // 2,
        "width": CROP_WIDTH,
        "height": CROP_HEIGHT,
        "mon": 1
    }


def screen_scan():
    global flash_state, tracking_since, MSSBase

    if MSSBase is None:
        MSSBase = mss.mss()

    monitor = MSSBase.monitors[1]
    width   = monitor["width"]
    height  = monitor["height"]
    centerx = width // 2
    centery = height // 2

    top   = make_monitor(centerx, centery - 35, 0, -CROP_HEIGHT)
    left  = make_monitor(centerx, centery + 35, -80, 0)
    right = make_monitor(centerx, centery + 35, 80, 0)
    rois  = [("Top", top), ("Left", left), ("Right", right)]

    try:
        start  = time()
        now_ms = int(time() * 1000)

        for dir, mon in rois:
            img = np.array(MSSBase.grab(mon))
            hsv = cv2.cvtColor(cv2.cvtColor(img, cv2.COLOR_BGRA2BGR), cv2.COLOR_BGR2HSV)

            mask_red = cv2.inRange(hsv, lower_red, upper_red)
            mask_flash = cv2.inRange(hsv, lower_flash, upper_flash)
            indicator_count = cv2.countNonZero(mask_red)
            flash_count = cv2.countNonZero(mask_flash)

            with LOCK:
                state = flash_state[dir]
                if state == eIndicatorState.IDLE:
                    if indicator_count > 30:
                        flash_state[dir] = eIndicatorState.TRACKING
                        tracking_since[dir] = now_ms
                elif state == eIndicatorState.TRACKING:
                    if indicator_count < 10:
                        flash_state[dir] = eIndicatorState.IDLE
                    elif flash_count > 200:
                        flash_state[dir] = eIndicatorState.FLASHING
                    elif now_ms - tracking_since[dir] > TIMEOUT_MS:
                        flash_state[dir] = eIndicatorState.IDLE
                elif state == eIndicatorState.FLASHING:
                    if indicator_count < 10:
                        flash_state[dir] = eIndicatorState.IDLE

        frames = 1.0 / (time() - start)
        print(f"\rFPS: {frames:.1f}", flush=True, end="")

        if is_pressed("!"):
            show_debug_window()
    except Exception as e:
        print(f"Screen Scan error: {e}")
        exit(1)


def show_debug_window():
    if MSSBase is None:
        print("MSSBase was not initialized")
        return

    monitor = MSSBase.monitors[1]
    img     = np.array(MSSBase.grab(monitor))
    frame   = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    width   = monitor["width"]
    height  = monitor["height"]
    centerx = width // 2
    centery = height // 2

    rois = [
        ("Top",   make_monitor(centerx, centery - 35, 0, -CROP_HEIGHT)),
        ("Left",  make_monitor(centerx, centery + 35, -80, 0)),
        ("Right", make_monitor(centerx, centery + 35, 80, 0)),
    ]

    for name, mon in rois:
        x1, y1 = mon["left"], mon["top"]
        x2, y2 = x1 + mon["width"], y1 + mon["height"]
        color  = (0, 255, 0) if flash_state[name] != eIndicatorState.IDLE else (0, 0, 255)

        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(
            frame,
            name,
            (x1, y1 - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            color,
            2
        )

    cv2.imshow("Debug ROIs", frame)
    cv2.waitKey(1)
