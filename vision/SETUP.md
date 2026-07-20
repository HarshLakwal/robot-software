# Object recognition — setup on the Pi

Run all of this on the Raspberry Pi itself (SSH in), not on your Mac.

## 1. System packages
```
sudo apt update
sudo apt install -y python3-picamera2 espeak-ng libatlas-base-dev unzip
```
`espeak-ng` is the voice engine — the script calls its command-line binary directly (`espeak-ng "text"`) rather than going through `pyttsx3`, since `pyttsx3`'s ctypes-based library lookup is unreliable on current Raspberry Pi OS/Python versions. `python3-picamera2` must come from apt, not pip — it depends on system libcamera bindings that don't build cleanly through pip.

## 2. Python environment
`picamera2` only exists in system site-packages, so the venv needs `--system-site-packages` to see it:
```
python3 -m venv --system-site-packages ~/venvs/robot
source ~/venvs/robot/bin/activate
pip install -r requirements.txt
```
This uses full `tensorflow` for the TFLite interpreter — Google stopped publishing `tflite-runtime` wheels for current Python/Raspberry Pi OS versions, so that lighter package isn't installable anymore. `tensorflow` is a much bigger download, but piwheels has prebuilt ARM wheels for it so it won't compile from source — expect the install to take a while on first run, not to fail.

## 3. Get the detection model
Standard COCO-trained SSD MobileNet V1 quantized model (fast enough for real-time-ish inference on a Pi 4 without an accelerator):
```
cd ~/robot-software/vision/models
wget https://storage.googleapis.com/download.tensorflow.org/models/tflite/coco_ssd_mobilenet_v1_1.0_quant_2018_06_29.zip
unzip coco_ssd_mobilenet_v1_1.0_quant_2018_06_29.zip
```
This gives you `detect.tflite` and `labelmap.txt` in `models/` — exactly the filenames the script expects by default. If that link 404s (Google occasionally moves these), search "tflite coco ssd mobilenet v1 quant download" — it's TensorFlow's standard quickstart model, referenced in their own docs.

## 4. Confirm the camera works on its own first
```
rpicam-hello -t 5000
```
If that doesn't show a live preview / doesn't error out, fix the camera connection before running the detection script — don't debug both at once.

## 5. Run it
```
cd ~/robot-software/vision
python3 object_recognition.py
```
It prints every detection above 0.5 confidence to the console, speaks each distinct object name once per 5-second cooldown (so it doesn't repeat "I can see a bottle" every frame), and opens a live preview window with bounding boxes drawn around whatever it detects. Tune with `--threshold` and `--say-cooldown`. Press `q` in the preview window (or Ctrl+C in the terminal) to stop.

If you're running this over a plain SSH session with no desktop attached (no monitor, no Pi Connect/VNC), the preview window has nowhere to draw — pass `--headless` to skip it and stay console/speech-only.

## Known limits of this v1
- No Coral accelerator yet, so expect a handful of FPS, not real-time video — fine for "walk into frame, get recognized," not for tracking fast motion.
- The preview window is a temporary debugging aid — nothing is drawn to the robot's actual 3.5" display yet. That's a follow-up once the display's GPIO pass-through question (from the wiring plan) is resolved and the screen is actually wired up.
- Runs in the foreground in a terminal; turning this into a background service/systemd unit is a later step once you're integrating it with the rest of the robot.
