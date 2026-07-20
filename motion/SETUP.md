# Pan/tilt servo control — setup on the Pi

Do the electrical wiring first (see main conversation / your AI-Robot wiring plan: Pi I2C + 3.3V/GND to PCA9685 logic side, buck converter 5V/GND to PCA9685's V+ terminal block, servos onto CH0 = pan, CH1 = tilt). Don't run any code until that's done.

## 1. Enable I2C
```
sudo raspi-config nonint do_i2c 0
sudo reboot
```

## 2. Confirm the PCA9685 is detected
After reboot:
```
sudo apt install -y i2c-tools
i2cdetect -y 1
```
You should see a device at address `40`. If the grid is empty, stop and check the SDA/SCL/logic-power wiring before continuing — don't move on to servo power or code yet.

## 3. Install Python dependencies
From the repo root (`~/Desktop/robot-software`), same venv as the vision module:
```
cd ~/Desktop/robot-software
source ~/venvs/robot/bin/activate
pip install -r requirements.txt
```

## 4. Connect servo power, then test
Only now connect the buck converter's 5V/GND to the PCA9685's V+ terminal block. Run the built-in sweep test first — it exercises full range of motion on both axes so you can visually confirm both servos move correctly and nothing is mechanically binding, before trying to set specific angles:
```
cd motion
python3 pan_tilt.py --sweep
```

## 5. Set specific angles
```
python3 pan_tilt.py --pan 45 --tilt 120
```
Angles are 0-180, servo-dependent — if your bracket's mechanical range doesn't match 0/180 cleanly (common with cheap servo horns), don't force it past resistance. Note where it binds and treat that as your practical min/max instead of 0/180.
