import paho.mqtt.client as mqtt
import ssl

# MQTT Configuration for HiveMQ Cloud
# MQTT_BROKER = "ae73dc29b27647769759e19c6aeaaa52.s1.eu.hivemq.cloud"
MQTT_BROKER ="192.168.0.137"
MQTT_PORT = 1883
# MQTT_PORT = 8883
# MQTT_USERNAME = "edubot"
# MQTT_PASSWORD = "Edubot@123"
# CERT_PATH = r"C:\\isrgrootx1.pem"

class MQTTClient:
    def __init__(self):
        """Initialize the MQTT client and set up callbacks."""
        self.client = mqtt.Client()
        # self.client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
        # self.client.tls_set(CERT_PATH, tls_version=ssl.PROTOCOL_TLSv1_2)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.performance_data_received = False
        self.correct_answers = 0
        self.incorrect_answers = 0
        self.average_time = 0.0

    def connect(self):
        """Connect to the MQTT broker and start the loop."""
        self.client.connect(MQTT_BROKER, MQTT_PORT, 60)
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        """Handle the connection result."""
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect")

    def on_message(self, client, userdata, msg):
        """Handle incoming messages on subscribed topics."""
        if msg.topic.startswith("activity/performance/"):
            data = msg.payload.decode().split(',')
            self.correct_answers, self.incorrect_answers = map(int, data[:2])
            self.average_time = float(data[2])
            self.performance_data_received = True
            print(f"Performance data received: {self.correct_answers}, {self.incorrect_answers}, {self.average_time}")

    def publish(self, topic, payload):
        """Publish a message to a specified topic."""
        self.client.publish(topic, payload)

    def subscribe(self, topic):
        """Subscribe to a specified topic."""
        self.client.subscribe(topic)

    def unsubscribe(self, topic):
        """Unsubscribe from a specified topic."""
        self.client.unsubscribe(topic)

    def reset_performance_data(self):
        """Reset performance data flags and values."""
        self.performance_data_received = False
        self.correct_answers = 0
        self.incorrect_answers = 0
        self.average_time = 0.0