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
    # TODO: Loop through the port range and use `is_port_available` to find a free port.
    # TODO: Return the first available port found.
    # TODO: Raise RuntimeError if no available port is found in the given range.
    pass

def is_port_available(port: int, host: str = DEFAULT_HOST) -> bool:
    """
    Check if a port is available for use.
    """
    # TODO: Attempt to bind a socket to the given host and port.
    # TODO: If binding succeeds, close the socket and return True.
    # TODO: If binding fails due to OSError, return False.
    pass

def create_server_socket(host: str = DEFAULT_HOST, port: Optional[int] = None) -> Tuple[socket.socket, int]:
    """
    Create and bind a server socket.
    """
    # TODO: If port is None, find an available port using `find_available_port`.
    # TODO: Create a TCP socket and allow reuse of the address.
    # TODO: Bind the socket and start listening.
    # TODO: Return the socket and the port.
    # TODO: On error, close the socket and raise RuntimeError with details.
    pass

def create_client_socket(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT, 
                        max_retries: int = MAX_RETRIES, retry_delay: int = RETRY_DELAY) -> socket.socket:
    """
    Create and connect a client socket with retry logic.
    """
    # TODO: Attempt to connect to the server in a loop, retrying on failure.
    # TODO: On successful connection, return the socket.
    # TODO: Print retry attempts and wait between retries.
    # TODO: Raise RuntimeError if all retries fail or if unexpected error occurs.
    pass

def send_json_message(sock: socket.socket, message: Dict[str, Any]) -> None:
    """
    Send a JSON message over a socket.
    """
    # TODO: Convert the message dictionary to a JSON string and encode to bytes.
    # TODO: Send the encoded message using `sock.send`.
    # TODO: Raise RuntimeError on any sending error.
    pass

def receive_json_message(sock: socket.socket, buffer_size: int = BUFFER_SIZE) -> Dict[str, Any]:
    """
    Receive a JSON message from a socket.
    """
    # TODO: Initialize empty bytes object for data.
    # TODO: Receive chunks of data in a loop and append to data buffer.
    # TODO: Try to decode and parse as JSON.
    # TODO: Continue until a valid JSON message is received.
    # TODO: Raise RuntimeError on decode failure or closed connection.
    pass

def send_image(sock: socket.socket, image_data: bytes) -> None:
    """
    Send image data over a socket.
    """
    # TODO: Send the length of the image as an 8-byte integer.
    # TODO: Send the image data in chunks using a loop.
    # TODO: Handle partial sends and connection issues.
    # TODO: Raise RuntimeError if any step fails.
    pass

def receive_image(sock: socket.socket) -> bytes:
    """
    Receive image data from a socket.
    """
    # TODO: Receive 8 bytes for image size and convert to integer.
    # TODO: Receive the expected number of bytes in chunks.
    # TODO: Handle closed connections and incomplete data.
    # TODO: Raise RuntimeError on any error or incomplete data.
    pass

def send_json_message_with_image(sock: socket.socket, message: Dict[str, Any], image_data: bytes) -> None:
    """
    Send a JSON message with image data over a socket.
    """
    # TODO: Send the JSON message using `send_json_message`.
    # TODO: Wait for 'ready' acknowledgment from receiver.
    # TODO: Send the image data using `send_image`.
    # TODO: Wait for 'success' acknowledgment after image is received.
    # TODO: Raise RuntimeError on any failure in these steps.
    pass

def receive_json_message_with_image(sock: socket.socket) -> Tuple[Dict[str, Any], bytes]:
    """
    Receive a JSON message with image data from a socket.
    """
    # TODO: Receive JSON message using `receive_json_message`.
    # TODO: Send a 'ready' acknowledgment to the sender.
    # TODO: Receive the image using `receive_image`.
    # TODO: Send a 'success' acknowledgment after successful reception.
    # TODO: Return the received message and image data.
    # TODO: Raise RuntimeError on failure in any of the steps.
    pass
