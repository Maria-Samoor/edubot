import paho.mqtt.client as mqtt
import json 
import logging

logger = logging.getLogger("activities")
# MQTT Configuration
# MQTT_BROKER ="" # Define the IP address of the MQTT broker to connect to.
MQTT_BROKER ="localhost" 
MQTT_PORT = 1883

class MQTTClient:
    """
    MQTT Client for managing communication with a remote MQTT broker.

    This class provides functionality to connect, subscribe, publish, and handle
    messages from an MQTT broker, designed to communicate performance data between
    Choregraphe and a Django application.

    Attributes:
        client (mqtt.Client): The Paho MQTT client instance.
        performance_data_received (bool): Flag to indicate if performance data has been received.
        correct_answers (int): Number of correct answers received.
        incorrect_answers (int): Number of incorrect answers received.
        average_time (float): Average time per activity, received in performance data.
    """
    def __init__(self):
        """Initialize the MQTT client and set up callbacks."""
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.performance_data_received = False
        self.performance_data = {}

    def connect(self):
        """Connect to the MQTT broker and start the client loop."""
        try:
            self.client.connect(MQTT_BROKER, MQTT_PORT, 60)
            self.client.loop_start()
            logger.info("Connected to MQTT Broker at %s:%d", MQTT_BROKER, MQTT_PORT)
        except Exception as e:
            logger.error("Failed to connect to MQTT Broker: %s", str(e))

    def on_connect(self, client, userdata, flags, rc):
        """Handle the connection result."""
        if rc == 0:
            logger.info("Successfully connected to MQTT Broker")
        else:
            logger.warning("Failed to connect to MQTT Broker with code: %d", rc)

    def on_message(self, client, userdata, msg):
        """Handle incoming messages on subscribed topics."""
        if msg.topic.startswith("activity/performance/"):
            try:
                data = json.loads(msg.payload.decode())
                self.performance_data = data
                self.performance_data_received = True
            except json.JSONDecodeError:
                logger.error("Failed to parse JSON payload from topic: %s", msg.topic)

    def publish(self, topic, payload):
        """Publish a message to a specified topic."""
        self.client.publish(topic, payload)
        logger.debug("Published message to %s: %s", topic, payload)

    def subscribe(self, topic):
        """Subscribe to a specified topic."""
        self.client.subscribe(topic)
        logger.info("Subscribed to topic: %s", topic)

    def unsubscribe(self, topic):
        """Unsubscribe from a specified topic."""
        self.client.unsubscribe(topic)
        logger.info("Unsubscribed from topic: %s", topic)

    def reset_performance_data(self):
        """Reset performance data flags and values."""
        self.performance_data_received = False
        self.performance_data = {}