# Object recognition — setup on the Pi

Run all of this on the Raspberry Pi itself (SSH in), not on your Mac.

## 1. System packages
```
sudo apt update
sudo apt install -y python3-picamera2 espeak libatlas-base-dev unzip
```
`espeak` is the voice engine `pyttsx3` drives on Linux. `python3-picamera2` must come from apt, not pip — it depends on system libcamera bindings that don't build cleanly through pip.

## 2. Python environment
`picamera2` only exists in system site-packages, so the venv needs `--system-site-packages` to see it:
```
python3 -m venv --system-site-packages ~/venvs/robot
source ~/venvs/robot/bin/activate
pip install -r requirements.txt
```
If `tflite-runtime` fails to install for your Python version, use `pip install tensorflow` instead — the script falls back to `tensorflow.lite` automatically.

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
It prints every detection above 0.5 confidence to the console and speaks each distinct object name once per 5-second cooldown (so it doesn't repeat "I can see a bottle" every frame). Tune with `--threshold` and `--say-cooldown`.

## Known limits of this v1
- No Coral accelerator yet, so expect a handful of FPS, not real-time video — fine for "walk into frame, get recognized," not for tracking fast motion.
- Nothing is drawn to the 3.5" display yet — that's a follow-up once the display's GPIO pass-through question (from the wiring plan) is resolved and the screen is actually wired up.
- Runs in the foreground in a terminal; turning this into a background service/systemd unit is a later step once you're integrating it with the rest of the robot.
