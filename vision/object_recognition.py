import argparse
import subprocess
import time

import cv2
import numpy as np
from picamera2 import Picamera2

try:
    from tflite_runtime.interpreter import Interpreter
except ImportError:
    from tensorflow.lite.python.interpreter import Interpreter


def speak(text):
    subprocess.run(["espeak-ng", text])


def load_labels(path):
    with open(path, "r") as f:
        labels = [line.strip() for line in f.readlines()]
    if labels and labels[0] == "???":
        labels = labels[1:]
    return labels


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="models/detect.tflite")
    parser.add_argument("--labels", default="models/labelmap.txt")
    parser.add_argument("--threshold", type=float, default=0.5)
    parser.add_argument("--say-cooldown", type=float, default=5.0)
    parser.add_argument("--headless", action="store_true", help="Don't open a preview window")
    args = parser.parse_args()

    labels = load_labels(args.labels)

    interpreter = Interpreter(model_path=args.model)
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    _, input_height, input_width, _ = input_details[0]["shape"]
    is_floating_model = input_details[0]["dtype"] == np.float32

    last_said = {}

    picam2 = Picamera2()
    config = picam2.create_preview_configuration(main={"size": (640, 480), "format": "RGB888"})
    picam2.configure(config)
    picam2.start()
    time.sleep(1)

    print("Object recognition running. Ctrl+C to stop." if args.headless else "Object recognition running. Press 'q' in the preview window (or Ctrl+C) to stop.")
    try:
        while True:
            frame = picam2.capture_array()
            frame_height, frame_width = frame.shape[:2]
            resized = cv2.resize(frame, (input_width, input_height))
            input_data = np.expand_dims(resized, axis=0)

            if is_floating_model:
                input_data = (np.float32(input_data) - 127.5) / 127.5

            interpreter.set_tensor(input_details[0]["index"], input_data)
            interpreter.invoke()

            boxes = interpreter.get_tensor(output_details[0]["index"])[0]
            classes = interpreter.get_tensor(output_details[1]["index"])[0]
            scores = interpreter.get_tensor(output_details[2]["index"])[0]

            now = time.time()
            for i, score in enumerate(scores):
                if score < args.threshold:
                    continue
                class_id = int(classes[i])
                if class_id >= len(labels):
                    continue
                label = labels[class_id]

                print(f"Detected {label} ({score:.2f})")

                if now - last_said.get(label, 0) > args.say_cooldown:
                    last_said[label] = now
                    speak(f"I can see a {label}.")

                if not args.headless:
                    ymin, xmin, ymax, xmax = boxes[i]
                    x1, y1 = int(xmin * frame_width), int(ymin * frame_height)
                    x2, y2 = int(xmax * frame_width), int(ymax * frame_height)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(
                        frame,
                        f"{label} {score:.2f}",
                        (x1, max(y1 - 8, 12)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0, 255, 0),
                        2,
                    )

            if not args.headless:
                cv2.imshow("Robot Vision", frame)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

    except KeyboardInterrupt:
        pass
    finally:
        picam2.stop()
        if not args.headless:
            cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
