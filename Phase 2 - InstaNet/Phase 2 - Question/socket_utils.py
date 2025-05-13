import socket
import json
import time
import base64
from typing import Optional, Tuple, Dict, Any
from constants import (
    DEFAULT_HOST, DEFAULT_PORT, MAX_RETRIES, RETRY_DELAY,
    BUFFER_SIZE
)
def find_available_port(host: str = DEFAULT_HOST, start_port: int = DEFAULT_PORT, max_port: int = 6000) -> int:
    """
    Find an available port in the given range.
    """
    if not (1 <= start_port <= 65535 and 1 <= max_port <= 65535):
        raise ValueError("Port range must be between 1 and 65535.")
    # TODO: Loop through the port range and use `is_port_available` to find a free port.
    for port in range(start_port, max_port+1):
        if is_port_available(port, host):
            return port

    # TODO: Raise RuntimeError if no available port is found in the given range.
    raise RuntimeError("no available port is found in the given range.")
    pass

def is_port_available(port: int, host: str = DEFAULT_HOST) -> bool:
    """
    Check if a port is available for use.
    """
    # TODO: Attempt to bind a socket to the given host and port.
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
    # TODO: If binding succeeds, close the socket and return True.
        sock.bind((host, port))
        sock.close()
        return True
    # TODO: If binding fails due to OSError, return False.
    except OSError:
        return False
    pass

def create_server_socket(host: str = DEFAULT_HOST, port: Optional[int] = None) -> Tuple[socket.socket, int]:
    """
    Create and bind a server socket.
    """

    try:
    # TODO: If port is None, find an available port using `find_available_port`.
        if port is None:
            port = find_available_port()
    # TODO: Create a TCP socket and allow reuse of the address.
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # TODO: Bind the socket and start listening.
        server_socket.bind((host, port))
        server_socket.listen(10)
    # TODO: Return the socket and the port.
        return server_socket, port
    # TODO: On error, close the socket and raise RuntimeError with details.
    except Exception as e:
        if server_socket:
            server_socket.close()
        raise RuntimeError(f"Error creating server socket: {e}")
    pass

def create_client_socket(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT, 
                        max_retries: int = MAX_RETRIES, retry_delay: int = RETRY_DELAY) -> socket.socket:
    """
    Create and connect a client socket with retry logic.
    """
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # TODO: Attempt to connect to the server in a loop, retrying on failure.
    for attempt in range(max_retries):
        try:
            client_socket.connect((host, port))
    # TODO: On successful connection, return the socket.
            return client_socket
    # TODO: Print retry attempts and wait between retries.
        except socket.error as e:
            print(f"retry attempt: {attempt + 1} Error: {e}")
            if attempt == max_retries - 1:  # Raise error only after all retries fail
                raise RuntimeError(f"Error creating client socket: {e}")
            time.sleep(retry_delay)
    # TODO: Raise RuntimeError if all retries fail or if unexpected error occurs.
    pass

def send_json_message(sock: socket.socket, message: Dict[str, Any]) -> None:
    """
    Send a JSON message over a socket.
    """
    # TODO: Convert the message dictionary to a JSON string and encode to bytes.
    try:
        json_str = json.dumps(message)
        encoded_message = json_str.encode('utf-8')
    # TODO: Send the encoded message using `sock.send`.
        sock.send(encoded_message)
    # TODO: Raise RuntimeError on any sending error.
    except (socket.error, json.JSONEncodeError) as e:
        raise RuntimeError(f"Error sending JSON message: {e}")
    pass

def receive_json_message(sock: socket.socket, buffer_size: int = BUFFER_SIZE) -> Dict[str, Any]:
    """
    Receive a JSON message from a socket.
    """
    # TODO: Initialize empty bytes object for data.
    data = b''
    # TODO: Receive chunks of data in a loop and append to data buffer.
    while True:
        try:
            chunk = sock.recv(buffer_size)
            if not chunk:
                raise RuntimeError("Connection closed while receiving data")
            data += chunk
    # TODO: Try to decode and parse as JSON.
            try:
                message = json.loads(data.decode('utf-8'))
    # TODO: Continue until a valid JSON message is received.
                return message
            except json.JSONDecodeError:
                continue
    # TODO: Raise RuntimeError on decode failure or closed connection.
        except socket.error as e:
            raise RuntimeError(f"Error receiving JSON message: {e}")
    pass

def send_image(sock: socket.socket, image_data: bytes) -> None:
    """
    Send image data over a socket.
    """
    # TODO: Send the length of the image as an 8-byte integer.
    try:
        # Send image size first
        image_size = len(image_data)
        sock.sendall(image_size.to_bytes(8, byteorder='big'))
    # TODO: Send the image data in chunks using a loop.
        # Send image data in chunks
        total_sent = 0
        while total_sent < image_size:
            sent = sock.send(image_data[total_sent:total_sent + BUFFER_SIZE])
    # TODO: Handle partial sends and connection issues.
            if sent == 0:
                raise RuntimeError("Socket connection broken")
            total_sent += sent
    # TODO: Raise RuntimeError if any step fails.
    except socket.error as e:
        raise RuntimeError(f"Error sending image: {e}")
    pass

def receive_image(sock: socket.socket) -> bytes:
    """
    Receive image data from a socket.
    """
    # TODO: Receive 8 bytes for image size and convert to integer.
    try:
        # Receive image size first
        size_data = sock.recv(8)
        if len(size_data) != 8:
            raise RuntimeError("Incomplete image size received")
        image_size = int.from_bytes(size_data, byteorder='big')
        received_data = bytearray()
    # TODO: Receive the expected number of bytes in chunks.
        while len(received_data) < image_size:
            chunk = sock.recv(min(BUFFER_SIZE, image_size - len(received_data)))
    # TODO: Handle closed connections and incomplete data.
            if not chunk:
                raise RuntimeError("Connection closed before receiving complete image")
            received_data.extend(chunk)
        return bytes(received_data)
    # TODO: Raise RuntimeError on any error or incomplete data.
    except socket.error as e:
        raise RuntimeError(f"Error receiving image: {e}")
    pass

def send_json_message_with_image(sock: socket.socket, message: Dict[str, Any], image_data: bytes) -> None:
    """
    Send a JSON message with image data over a socket.
    """
    # TODO: Send the JSON message using `send_json_message`.
    try:
        send_json_message(sock, message)
    # TODO: Wait for 'ready' acknowledgment from receiver.
        ack = receive_json_message(sock)
        if ack.get('status') != 'ready':
            raise RuntimeError("Did not receive 'ready' acknowledgment")

    # TODO: Send the image data using `send_image`.
        send_image(sock, image_data)

    # TODO: Wait for 'success' acknowledgment after image is received.
        ack = receive_json_message(sock)
    # TODO: Raise RuntimeError on any failure in these steps.
        if ack.get('status') != 'success':
            raise RuntimeError("Did not receive 'success' acknowledgment")
    except Exception as e:
        raise RuntimeError(f"Error in send_json_message_with_image: {e}")
    pass

def receive_json_message_with_image(sock: socket.socket) -> Tuple[Dict[str, Any], bytes]:
    """
    Receive a JSON message with image data from a socket.
    """
    # TODO: Receive JSON message using `receive_json_message`.
    try:
        message = receive_json_message(sock)
    # TODO: Send a 'ready' acknowledgment to the sender.
        send_json_message(sock, {'status': 'ready'})
    # TODO: Receive the image using `receive_image`.
        image_data = receive_image(sock)
    # TODO: Send a 'success' acknowledgment after successful reception.
        send_json_message(sock, {'status': 'success'})
    # TODO: Return the received message and image data.
        return message, image_data
    # TODO: Raise RuntimeError on failure in any of the steps.
    except Exception as e:
        raise RuntimeError(f"Error in receive_json_message_with_image: {e}")
    pass
