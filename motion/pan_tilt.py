import argparse
import time

from adafruit_servokit import ServoKit

PAN_CHANNEL = 0
TILT_CHANNEL = 1

PAN_CENTER = 90
TILT_CENTER = 90


def clamp(value, low=0, high=180):
    return max(low, min(high, value))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pan", type=float, default=PAN_CENTER, help="Pan angle 0-180")
    parser.add_argument("--tilt", type=float, default=TILT_CENTER, help="Tilt angle 0-180")
    parser.add_argument(
        "--sweep",
        action="store_true",
        help="Run a pan/tilt range-of-motion test instead of setting a fixed angle",
    )
    args = parser.parse_args()

    kit = ServoKit(channels=16)

    if args.sweep:
        print("Sweeping pan: 0 -> 180 -> center, then tilt: 0 -> 180 -> center. Ctrl+C to stop early.")
        for angle in (0, 180, PAN_CENTER):
            kit.servo[PAN_CHANNEL].angle = clamp(angle)
            time.sleep(1)
        for angle in (0, 180, TILT_CENTER):
            kit.servo[TILT_CHANNEL].angle = clamp(angle)
            time.sleep(1)
        return

    kit.servo[PAN_CHANNEL].angle = clamp(args.pan)
    kit.servo[TILT_CHANNEL].angle = clamp(args.tilt)
    print(f"Pan set to {clamp(args.pan)}, tilt set to {clamp(args.tilt)}")


if __name__ == "__main__":
    main()
