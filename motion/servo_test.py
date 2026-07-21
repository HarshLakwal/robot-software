import argparse
import time

from adafruit_servokit import ServoKit


def main():
    parser = argparse.ArgumentParser(description="Sweep a single servo on the PCA9685 to confirm it's wired and working")
    parser.add_argument("--channel", type=int, required=True, help="PCA9685 channel number (0-15)")
    parser.add_argument("--pause", type=float, default=1.0, help="Seconds to hold at each angle")
    args = parser.parse_args()

    kit = ServoKit(channels=16)
    servo = kit.servo[args.channel]

    print(f"Testing servo on channel {args.channel}. Ctrl+C to stop.")
    try:
        for angle in (90, 0, 180, 90):
            print(f"  -> {angle} degrees")
            servo.angle = angle
            time.sleep(args.pause)
        print("Done. If the servo moved smoothly through all positions, it's working.")
    except KeyboardInterrupt:
        print("\nStopped early.")


if __name__ == "__main__":
    main()
