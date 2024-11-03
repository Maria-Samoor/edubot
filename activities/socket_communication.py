import socket
import struct
import logging

class SocketCommunication:
    def __init__(self, host='127.0.0.1', port=5000):
        self.host = host
        self.port = port
        self.sock = None
        self.conn = None

    def connect_client(self):
        """Connects to a server as a client."""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            self.conn = self.sock
            print(f"Connected to server at {self.host}:{self.port}")
            logging.info("Client connected to server at %s:%d", self.host, self.port)
        except socket.error as e:
            logging.error("Failed to connect to server: %s", e)
            self.sock = None
            self.conn = None

    def bind_server(self):
        """Sets up the socket to act as a server and listen for incoming connections."""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.bind((self.host, self.port))
            self.sock.listen(1)
            print("Waiting for connection...")
            self.conn, addr = self.sock.accept()
            print(f"Connected to {addr}")
            logging.info("Server bound and connected to client at %s", addr)
        except socket.error as e:
            logging.error("Failed to bind server: %s", e)
            self.sock = None
            self.conn = None

    def disconnect(self):
        """Closes the socket connection."""
        if self.conn:
            self.conn.close()
        if self.sock:
            self.sock.close()
        logging.info("Socket disconnected")
        self.conn = None
        self.sock = None

    def send_int(self, data):
        """Sends an integer data as 4 bytes."""
        if self.sock:
            try:
                number_str = str(data)
                data_type = 'TXT'
                data_bytes = number_str.encode('utf-8')
                size = len(data_bytes)
                self.conn.sendall(struct.pack('!I', size))
                self.conn.sendall(data_type.encode('utf-8'))
                self.conn.sendall(data_bytes)
                logging.info("Sent integer: %d", data)
            except socket.error as e:
                logging.error("Failed to send integer: %s", e)

    def receive_int(self):
        """Receives an integer from the socket."""
        if self.sock:
            try:
                data = self.sock.recv(4)
                if data:
                    result = struct.unpack('!i', data)[0]
                    logging.info("Received integer: %d", result)
                    return result
            except socket.error as e:
                logging.error("Failed to receive integer: %s", e)
        return None

    def send_image(self, image_data):
        """Sends an image over the socket."""
        if self.sock:
            try:
                size = len(image_data)
                # Send the size of the image
                self.sock.sendall(struct.pack('!I', size))
                # Send the image data
                self.sock.sendall(image_data)
                logging.info("Sent image of size: %d bytes", size)
            except socket.error as e:
                logging.error("Failed to send image: %s", e)

    def receive_image(self):
        """Receives an image sent as binary data over the socket."""
        if self.sock:
            try:
                while True:
                    # Receive the image size
                    size_data = self.sock.recv(4)
                    if not size_data:
                        break
                    size = struct.unpack('!I', size_data)[0]

                    # Receive the actual image data
                    image_data = b''
                    while len(image_data) < size:
                        packet = self.sock.recv(size - len(image_data))
                        if not packet:
                            break
                        image_data += packet
                    
                    logging.info("Received image of size: %d bytes", len(image_data))
                    return image_data
            except socket.error as e:
                logging.error("Failed to receive image: %s", e)
        return None
