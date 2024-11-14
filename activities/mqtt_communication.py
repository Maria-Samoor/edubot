import paho.mqtt.client as mqtt
import ssl

# MQTT Configuration
MQTT_BROKER ="" # Define the IP address of the MQTT broker to connect to.
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
        self.correct_answers = 0
        self.incorrect_answers = 0
        self.average_time = 0.0

    def connect(self):
        """Connect to the MQTT broker and start the client loop.

        Establishes a connection to the MQTT broker with the specified host and port.
        The loop is started to handle incoming messages asynchronously.
        """        
        self.client.connect(MQTT_BROKER, MQTT_PORT, 60)
        self.client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        """Handle the connection result.

        Parameters:
            client (mqtt.Client): The MQTT client instance.
            userdata: Private user data (not used).
            flags (dict): Response flags sent by the broker.
            rc (int): Connection result status code (0 indicates successful connection).

        Prints connection status based on the result code.
        """
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect")

    def on_message(self, client, userdata, msg):
        """Handle incoming messages on subscribed topics.

        Parses performance data if the topic starts with 'activity/performance/'.

        Parameters:
            client (mqtt.Client): The MQTT client instance.
            userdata: Private user data (not used).
            msg (mqtt.MQTTMessage): The message received from the broker, containing
                                    topic and payload attributes.
        
        Updates `correct_answers`, `incorrect_answers`, and `average_time` if
        performance data is received, and sets `performance_data_received` to True.
        """
        if msg.topic.startswith("activity/performance/"):
            data = msg.payload.decode().split(',')
            self.correct_answers, self.incorrect_answers = map(int, data[:2])
            self.average_time = float(data[2])
            self.performance_data_received = True
            print(f"Performance data received: {self.correct_answers}, {self.incorrect_answers}, {self.average_time}")

    def publish(self, topic, payload):
        """Publish a message to a specified topic.

        Parameters:
            topic (str): The topic to which the message should be published.
            payload (str): The message payload to be sent to the broker.
        """
        self.client.publish(topic, payload)

    def subscribe(self, topic):
        """Subscribe to a specified topic.

        Parameters:
            topic (str): The topic to subscribe to, enabling receipt of messages sent to it.
        """
        self.client.subscribe(topic)

    def unsubscribe(self, topic):
        """Unsubscribe from a specified topic.

        Parameters:
            topic (str): The topic to unsubscribe from, stopping receipt of its messages.
        """
        self.client.unsubscribe(topic)

    def reset_performance_data(self):
        """Reset performance data flags and values.

        Resets `performance_data_received` to False, and sets `correct_answers`,
        `incorrect_answers`, and `average_time` to their initial values.
        """
        self.performance_data_received = False
        self.correct_answers = 0
        self.incorrect_answers = 0
        self.average_time = 0.0