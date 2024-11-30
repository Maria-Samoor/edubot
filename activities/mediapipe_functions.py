from .mqtt_communication import MQTTClient
import numpy as np
import cv2
import mediapipe as mp


class MediaPipeServer:
    """
    A class to handle image processing and hand gesture detection using MediaPipe,
    integrated with MQTT for communication.

    Attributes:
        mqtt_client (MQTTClient): An instance of MQTTClient for MQTT communication.
        mp_hands (mp.solutions.hands): MediaPipe Hands solution for hand landmark detection.
        mp_drawing (mp.solutions.drawing_utils): MediaPipe drawing utility for visualizing hand landmarks.
    """

    def __init__(self, mqtt_client):
        """
        Initializes the MediaPipeServer with an MQTT client.

        Args:
            mqtt_client (MQTTClient): The MQTT client for subscribing to topics and publishing messages.
        """
        self.mqtt_client = mqtt_client
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils

        # Subscribe to topics
        self.mqtt_client.subscribe("activity/stop/3")
        self.mqtt_client.subscribe("mediapipe/image")

        # Add an on_message callback
        self.mqtt_client.client.on_message = self.on_message

    def start(self):
        """Starts the MediaPipe server."""
        self.running = True
        print("MediaPipe server started. Waiting for images...")

    def stop(self):
        """Stops the MediaPipe server."""
        self.mqtt_client.unsubscribe("mediapipe/image")
        print("MediaPipe server stopped.")

    def on_message(self, client, userdata, msg):
        """Handle incoming MQTT messages."""
        if msg.topic == "mediapipe/image":
            try:
                # Print payload size for debugging
                print(f"Payload size: {len(msg.payload)}")

                # Attempt to decode the image
                np_img = np.frombuffer(msg.payload, dtype=np.uint8)

                # Check if size matches the expected dimensions
                expected_size = 240 * 320 * 3
                if len(np_img) == expected_size:
                    # Reshape if the size matches
                    reshaped_img = np_img.reshape((240, 320, 3))
                else:
                    print(f"Unexpected image size: {len(np_img)}. Resizing...")
                    # Assume the image is encoded (e.g., JPEG)
                    reshaped_img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
                    reshaped_img = cv2.resize(reshaped_img, (320, 240))

                print("Image received. Processing...")
                self.process_image(reshaped_img)
            except Exception as e:
                print(f"Error processing image: {e}")

        elif msg.topic == "activity/stop/3":
            self.stop()


    def process_image(self, image):
        """
        Processes an image to detect hands, count fingers, or detect no hands.
        """
        # Preprocess the image
        preprocessed_image = self.preprocess_image(image)

        # Initialize MediaPipe hands processing
        with self.mp_hands.Hands(
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7,
            max_num_hands=2
        ) as hands:
            try:
                # Convert the image to RGB as required by MediaPipe
                image_rgb = cv2.cvtColor(preprocessed_image, cv2.COLOR_BGR2RGB)

                # Process the image to detect hand landmarks
                results = hands.process(image_rgb)

                if results.multi_hand_landmarks:  # If hands are detected
                    total_fingers = 0

                    for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                        # Draw hand landmarks on the image
                        self.mp_drawing.draw_landmarks(
                            preprocessed_image, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
                        )

                        # Draw a bounding box (palm detection frame) around the hand
                        self.draw_palm_detection_frame(preprocessed_image, hand_landmarks)

                        # Count fingers for each detected hand
                        hand_label = results.multi_handedness[idx].classification[0].label
                        num_fingers = self.count_raised_fingers(hand_landmarks, hand_label)
                        total_fingers += num_fingers

                    # Publish the total fingers detected
                    self.mqtt_client.publish("mediapipe/fingers", str(total_fingers))

                else:  # No hands detected
                    print("No hands detected in the image.")
                    self.mqtt_client.publish("mediapipe/handnotdetected", "100")

                # Display the processed image for debugging
                cv2.imshow("Processed Image", preprocessed_image)
                cv2.waitKey(1)

            except Exception as e:
                print(f"Error during MediaPipe processing: {e}")

    def preprocess_image(self, image):
        """
        Enhances the input image for better hand detection.
        """
        try:
            # Resize image to 240x320 if needed
            resized_image = cv2.resize(image, (320, 240), interpolation=cv2.INTER_LINEAR)

            # Apply Gaussian blur to reduce noise
            blurred_image = cv2.GaussianBlur(resized_image, (5, 5), 0)

            # Adjust contrast
            enhanced_image = cv2.convertScaleAbs(blurred_image, alpha=1.2, beta=30)

            # Upscale image for better processing (optional)
            high_res_image = cv2.resize(enhanced_image, (640, 480), interpolation=cv2.INTER_CUBIC)

            # Further enhance edges for better hand landmark detection
            enhanced_edges = cv2.Canny(high_res_image, threshold1=100, threshold2=200)

            # Combine original high-resolution image with edges (for visualization/debugging)
            final_preprocessed_image = cv2.addWeighted(high_res_image, 0.8, cv2.cvtColor(enhanced_edges, cv2.COLOR_GRAY2BGR), 0.2, 0)

            return final_preprocessed_image
        except Exception as e:
            print(f"Error in preprocessing: {e}")
            return image  # Return original image in case of failure

    def count_raised_fingers(self, hand_landmarks, handedness):
        """
        Counts the number of raised fingers for a given hand.
        """
        finger_tips = [4, 8, 12, 16, 20]  # Index of fingertips in the landmarks
        landmarks = hand_landmarks.landmark
        raised_fingers = []

        # Check thumb direction based on handedness
        if handedness == "Right":
            if landmarks[finger_tips[0]].x < landmarks[finger_tips[0] - 2].x:
                raised_fingers.append(1)  # Thumb raised
            else:
                raised_fingers.append(0)  # Thumb not raised
        else:
            if landmarks[finger_tips[0]].x > landmarks[finger_tips[0] - 2].x:
                raised_fingers.append(1)  # Thumb raised
            else:
                raised_fingers.append(0)  # Thumb not raised

        # Check other four fingers
        for i in range(1, 5):
            if landmarks[finger_tips[i]].y < landmarks[finger_tips[i] - 2].y:
                raised_fingers.append(1)  # Finger raised
            else:
                raised_fingers.append(0)  # Finger not raised

        return sum(raised_fingers)

    def draw_palm_detection_frame(self, image, hand_landmarks):
        """
        Draws a bounding box (palm detection frame) around the detected hand.
        """
        h, w, _ = image.shape
        x_min, y_min = w, h
        x_max, y_max = 0, 0

        # Get bounding box coordinates from hand landmarks
        for lm in hand_landmarks.landmark:
            x, y = int(lm.x * w), int(lm.y * h)
            x_min, y_min = min(x, x_min), min(y, y_min)
            x_max, y_max = max(x, x_max), max(y, y_max)

        # Draw the bounding box
        cv2.rectangle(image, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
