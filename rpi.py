import cv2
import mediapipe as mp
import time
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
from mfrc522 import MFRC522
from threading import Thread, Lock
from flask import Flask, Response

# MQTT Configuration
BROKER_IP = ""
BROKER_PORT = 1883
SUB_TOPICS = ["read/number", "read/rfid", "read/button"]
PUB_TOPIC = "mediapipe/fingers"
HAND_NOT_DETECTED = "mediapipe/handnotdetected"
RFID_TOPIC = "rfid/serial"
BUTTON_TOPIC = "button/number"

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

reader = MFRC522()

app = Flask(__name__)
mp_hands = mp.solutions.hands

class CameraStream:
    def __init__(self, src=0, width=320, height=240):
        """Initialize the camera stream with specified source, width, and height."""
        self.cap = cv2.VideoCapture(src)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.lock = Lock()
        self.ret, self.frame = self.cap.read()
        self.stopped = False
        Thread(target=self.update, args=()).start()

    def update(self):
        """Continuously read frames from the camera."""
        while not self.stopped:
            ret, frame = self.cap.read()
            with self.lock:
                self.ret, self.frame = ret, frame

    def read(self):
        """Return the latest frame from the camera."""
        with self.lock:
            return self.frame.copy()

    def stop(self):
        """Stop the camera stream and release resources."""
        self.stopped = True
        self.cap.release()

# Initialize the camera instance globally
camera = CameraStream(src=0, width=320, height=240)

def handle_mqtt_messages(client, userdata, message):
    """Handle incoming MQTT messages."""
    if message.topic == "read/number":
        handle_mediapipe(client)

def handle_mediapipe(client):
    """Process MediaPipe for finger detection."""
    with mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7, max_num_hands=2) as hands:
        frame = camera.read()
        if frame is None:
            return

        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(image_rgb)
        if results.multi_hand_landmarks:
            total_fingers = 0
            for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                hand_label = results.multi_handedness[idx].classification[0].label
                total_fingers += count_raised_fingers(hand_landmarks, hand_label)
            client.publish(PUB_TOPIC, str(total_fingers))
        else:
            client.publish(HAND_NOT_DETECTED, '100')

def rfid_task(client):
    """Continuously check for RFID input."""
    while True:
        if reader.MFRC522_Request(reader.PICC_REQIDL):
            (status, uid) = reader.MFRC522_Anticoll()
            if status != reader.MI_OK:
                continue
            
            id = ''.join([str(byte) for byte in uid])
            if id == '122135394178':
                message = "1"
            elif id == '20952455423':
                message = "2"
            elif id == '711020918113':
                message = "3"
            else:
                message = "4"

            client.publish(RFID_TOPIC, message)
            print(f"Published '{message}' to topic '{RFID_TOPIC}'")
        else:
            print("No RFID card detected.")
        time.sleep(4)

def button_task(client):
    """Continuously check for button presses with debouncing."""
    BUTTON1, BUTTON2, BUTTON3 = 17, 27, 22
    GPIO.setup(BUTTON1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(BUTTON2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(BUTTON3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    debounce_time = 0.3  # 300ms debounce period
    last_press_time = {BUTTON1: 0, BUTTON2: 0, BUTTON3: 0}

    while True:
        current_time = time.time()

        if GPIO.input(BUTTON1) and current_time - last_press_time[BUTTON1] > debounce_time:
            last_press_time[BUTTON1] = current_time
            message = "1"
            client.publish(BUTTON_TOPIC, message)
            print(f"Published '{message}' to topic '{BUTTON_TOPIC}'")

        elif GPIO.input(BUTTON2) and current_time - last_press_time[BUTTON2] > debounce_time:
            last_press_time[BUTTON2] = current_time
            message = "2"
            client.publish(BUTTON_TOPIC, message)
            print(f"Published '{message}' to topic '{BUTTON_TOPIC}'")

        elif GPIO.input(BUTTON3) and current_time - last_press_time[BUTTON3] > debounce_time:
            last_press_time[BUTTON3] = current_time
            message = "3"
            client.publish(BUTTON_TOPIC, message)
            print(f"Published '{message}' to topic '{BUTTON_TOPIC}'")

        time.sleep(0.4)  # Small delay to avoid high CPU usage

def setup_mqtt():
    """Setup MQTT client and subscribe to topics."""
    client = mqtt.Client()
    client.on_connect = lambda c, u, f, rc: [c.subscribe(topic) for topic in SUB_TOPICS]
    client.on_message = handle_mqtt_messages
    client.connect(BROKER_IP, BROKER_PORT, 60)

    # Start threads for continuous tasks
    Thread(target=rfid_task, args=(client,), daemon=True).start()
    Thread(target=button_task, args=(client,), daemon=True).start()

    client.loop_forever()

def count_raised_fingers(hand_landmarks, handedness):
    """Count the number of raised fingers based on hand landmarks."""
    finger_tips = [4, 8, 12, 16, 20]
    landmarks = hand_landmarks.landmark
    raised_fingers = []

    if handedness == "Right":
        raised_fingers.append(1 if landmarks[finger_tips[0]].x < landmarks[finger_tips[0] - 2].x else 0)
    else:
        raised_fingers.append(1 if landmarks[finger_tips[0]].x > landmarks[finger_tips[0] - 2].x else 0)

    for tip in finger_tips[1:]:
        raised_fingers.append(1 if landmarks[tip].y < landmarks[tip - 2].y else 0)

    return sum(raised_fingers)

def generate_frames(camera):
    """Generate frames from the camera for video feed."""
    while True:
        frame = camera.read()
        if frame is None:
            continue

        frame = cv2.flip(frame, 1)
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    """Route to serve the video feed."""
    return Response(generate_frames(camera), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    try:
        Thread(target=setup_mqtt, daemon=True).start()
        app.run(host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("Shutting down...")
        GPIO.cleanup()