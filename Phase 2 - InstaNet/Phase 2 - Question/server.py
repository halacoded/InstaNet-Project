"""
Dr. Suood Alroomi - Spring 2025 - Kuwait University - CpE 356 - Project

This module implements the server-side functionality of the Instagram Clone application.

The module provides:
- User authentication and management
- Post storage and retrieval
- Friend request handling
- Message management
- Real-time updates
- Image message handling

The server handles client connections using sockets and maintains the application's
state through JSON file storage.
"""

import threading
import json
import os
from pathlib import Path
import base64
import sys
import argparse
from socket_utils import create_server_socket, send_json_message, receive_json_message, send_json_message_with_image, receive_json_message_with_image, receive_image
from constants import (
    DEFAULT_HOST, DEFAULT_PORT, DATA_DIRECTORIES,
    USERS_FILE, DEFAULT_USERS_COUNT, DEFAULT_USER_PREFIX,
    DEFAULT_PASS_PREFIX
)

class InstagramServer:
    """
    The main server class for the Instagram Clone application.
    
    This class handles:
    - Client connections and communication
    - User authentication and management
    - Post storage and retrieval
    - Friend request processing
    - Message handling
    """
    
    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT):
        """
        Initialize the Instagram server.
        
        Args:
            host (str): The host address to bind to
            port (int): The port number to bind to
        """
        self.host = host
        self.server_socket, self.port = create_server_socket(host, port)
        print(f"Server started on {self.host}:{self.port}")
            
        self.clients = {}
        self.setup_data_directories()
        self.load_default_users()
        self.images = {}  # Store images in memory
        self.posts = []   # Store posts in memory

    def setup_data_directories(self):
        """
        Create necessary data directories if they don't exist.
        
        This method ensures all required directories for storing:
        - User data
        - Posts
        - Messages
        - Images
        are present in the filesystem.
        """
        for directory in DATA_DIRECTORIES:
            Path(directory).mkdir(parents=True, exist_ok=True)

    def load_default_users(self):
        """
        Load or create default users.
        
        If no users exist, this method creates a set of default users
        with predictable usernames and passwords for testing purposes.
        """
        if not os.path.exists(USERS_FILE):
            default_users = {
                f"{DEFAULT_USER_PREFIX}{i}": {"password": f"{DEFAULT_PASS_PREFIX}{i}", "friends": [], "requests": []}
                for i in range(1, DEFAULT_USERS_COUNT + 1)
            }
            with open(USERS_FILE, 'w') as f:
                json.dump(default_users, f, indent=4)

    def handle_client(self, client_socket, address):
        """
        Handle individual client connections.
        
        Args:
            client_socket: The socket connected to the client
            address: The client's address tuple
            
        This method:
        1. Receives and processes client requests
        2. Sends appropriate responses
        3. Handles connection cleanup
        """
        try:
            while True:
                request = receive_json_message(client_socket)
                if not request:
                    break
                response = self.process_request(request, client_socket)
                send_json_message(client_socket, response)

        except Exception as e:
            print(f"Error handling client {address}: {e}")
        finally:
            if address in self.clients:
                del self.clients[address]
            client_socket.close()

    def process_request(self, request, client_socket):
        """
        Process client requests and return appropriate responses.
        
        Args:
            request (dict): The client's request
            client_socket: The socket connected to the client
            
        Returns:
            dict: The response to send back to the client
        """
        action = request.get('action')
        if action == 'login':
            return self.handle_login(request)
        elif action == 'upload_post':
            return self.handle_upload_post(request, client_socket)
        elif action == 'get_feed':
            return self.handle_get_feed(request)
        elif action == 'send_friend_request':
            return self.handle_friend_request(request)
        elif action == 'accept_friend_request':
            return self.handle_accept_friend_request(request)
        elif action == 'reject_friend_request':
            return self.handle_reject_friend_request(request)
        elif action == 'send_message':
            return self.handle_send_message(request, client_socket)
        elif action == 'get_messages':
            return self.handle_get_messages(request)
        elif action == 'get_user_data':
            return self.handle_get_user_data(request)
        elif action == 'get_all_users':
            return self.handle_get_all_users(request)
        elif action == 'add_comment':
            return self.handle_add_comment(request)
        
        return {'status': 'error', 'message': 'Invalid action'}

    def handle_login(self, request):
        """
        Handle user login requests.
        
        Args:
            request (dict): The login request containing username and password
            
        Returns:
            dict: Login success/failure response
        """
        username = request.get('username', '').lower()
        password = request.get('password')
        
        with open('data/users/users.json', 'r') as f:
            users = json.load(f)
        
        if username in users and users[username]['password'] == password:
            return {'status': 'success', 'message': 'Login successful'}
        return {'status': 'error', 'message': 'Invalid credentials'}
    
    def handle_add_comment(self, request):
        """
        Handle adding comments to posts.
        
        Args:
            request (dict): The comment request containing post info and comment text
            
        Returns:
            dict: Comment addition success/failure response
        """
        post_image_path = request.get('post_image_path')
        user = request.get('user')
        text = request.get('text')

        posts_file = 'data/posts/posts.json'
        if not os.path.exists(posts_file):
            return {'status': 'error', 'message': 'No posts found'}

        with open(posts_file, 'r') as f:
            posts = json.load(f)

        # Find the post by image_path
        for post in posts:
            if post['image_path'] == post_image_path:
                if 'comments' not in post:
                    post['comments'] = []
                post['comments'].append({'user': user, 'text': text})
                break
        else:
            return {'status': 'error', 'message': 'Post not found'}

        with open(posts_file, 'w') as f:
            json.dump(posts, f, indent=4)

        return {'status': 'success'}

    def handle_upload_post(self, request, client_socket):
        """
        Handle post upload requests.
        
        Args:
            request (dict): The upload request containing image data and caption
            client_socket: The socket connected to the client
            
        Returns:
            dict: Upload success/failure response
        """
        try:
            username = request.get('username')
            caption = request.get('caption', '')
            timestamp = request.get('timestamp')
            
            # Create images directory if it doesn't exist
            images_dir = Path('data/images')
            images_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate unique filename
            image_filename = f"{username}_{timestamp.replace(':', '-')}.jpg"
            image_path = images_dir / image_filename
            
            # Send acknowledgment that we're ready for the image
            send_json_message(client_socket, {'status': 'ready'})
            
            # Receive and save the image data
            try:
                image_data = receive_image(client_socket)
                with open(image_path, 'wb') as f:
                    f.write(image_data)
                
                # Send success acknowledgment
                send_json_message(client_socket, {'status': 'success'})
            except Exception as e:
                print(f"Error saving image: {e}")
                send_json_message(client_socket, {'status': 'error', 'message': 'Failed to save image'})
                return {'status': 'error', 'message': 'Failed to save image'}
            
            # Create new post entry
            new_post = {
                'username': username,
                'image_path': str(image_path),
                'caption': caption,
                'timestamp': timestamp
            }
            
            # Update posts.json
            posts_file = 'data/posts/posts.json'
            try:
                with open(posts_file, 'r') as f:
                    posts = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                posts = []
            
            posts.append(new_post)
            
            with open(posts_file, 'w') as f:
                json.dump(posts, f, indent=4)
            
            return {'status': 'success', 'message': 'Post uploaded successfully'}
        except Exception as e:
            print(f"[ERROR] Exception in handle_upload_post: {e}")
            return {'status': 'error', 'message': str(e)}

    def handle_get_feed(self, request):
        """
        Handle feed retrieval requests.
        
        Args:
            request (dict): The feed request
            
        Returns:
            dict: Feed data response with image data
        """
        try:
            # Get posts with image data
            feed_posts = []
            for post in self.posts:
                post_data = post.copy()
                post_data['image_data'] = self.images.get(post['image_id'], '')
                feed_posts.append(post_data)
            
            return {'status': 'success', 'posts': feed_posts}
        except Exception as e:
            print(f"[ERROR] Exception in handle_get_feed: {e}")
            return {'status': 'error', 'message': str(e)}

    def handle_friend_request(self, request):
        """
        Handle friend request sending.
        
        Args:
            request (dict): The friend request containing sender and receiver
            
        Returns:
            dict: Request success/failure response
        """
        sender = request.get('sender')
        receiver = request.get('receiver')
        
        with open('data/users/users.json', 'r') as f:
            users = json.load(f)
        
        if receiver in users and receiver not in users[sender]['friends']:
            users[receiver]['requests'].append(sender)
            with open('data/users/users.json', 'w') as f:
                json.dump(users, f, indent=4)
            return {'status': 'success', 'message': 'Friend request sent'}
        return {'status': 'error', 'message': 'Invalid request'}

    def handle_accept_friend_request(self, request):
        """
        Handle friend request acceptance.
        
        Args:
            request (dict): The acceptance request containing user and friend
            
        Returns:
            dict: Acceptance success/failure response
        """
        user = request.get('user')
        friend = request.get('friend')
        
        with open('data/users/users.json', 'r') as f:
            users = json.load(f)
        
        if friend in users[user]['requests']:
            users[user]['friends'].append(friend)
            users[friend]['friends'].append(user)
            users[user]['requests'].remove(friend)
            
            with open('data/users/users.json', 'w') as f:
                json.dump(users, f, indent=4)
            return {'status': 'success', 'message': 'Friend request accepted'}
        return {'status': 'error', 'message': 'Invalid request'}

    def handle_reject_friend_request(self, request):
        """
        Handle friend request rejection.
        
        Args:
            request (dict): The rejection request containing user and friend
            
        Returns:
            dict: Rejection success/failure response
        """
        user = request.get('user')
        friend = request.get('friend')
        
        with open('data/users/users.json', 'r') as f:
            users = json.load(f)
        
        if friend in users[user]['requests']:
            users[user]['requests'].remove(friend)
            with open('data/users/users.json', 'w') as f:
                json.dump(users, f, indent=4)
            return {'status': 'success', 'message': 'Friend request rejected'}
        return {'status': 'error', 'message': 'Invalid request'}

    def handle_send_message(self, request, client_socket):
        """
        Handle message sending.
        
        Args:
            request (dict): The message request containing sender, receiver, and message
            client_socket: The socket connected to the client
            
        Returns:
            dict: Message sending success/failure response
        """
        try:
            sender = request.get('sender')
            receiver = request.get('receiver')
            message = request.get('message')
            is_image = request.get('is_image', False)
            
            # Create message file name (sorted usernames)
            usernames = sorted([sender, receiver])
            message_file = f'data/messages/{usernames[0]}_{usernames[1]}.json'
            
            if os.path.exists(message_file):
                with open(message_file, 'r') as f:
                    messages = json.load(f)
            else:
                messages = []
            
            message_data = {
                'sender': sender,
                'receiver': receiver,
                'message': message,
                'timestamp': request.get('timestamp'),
                'is_image': is_image
            }
            
            if is_image:
                # Create images directory if it doesn't exist
                images_dir = Path('data/images')
                images_dir.mkdir(parents=True, exist_ok=True)
                
                # Generate unique filename for the image
                timestamp = request.get('timestamp').replace(':', '-')
                image_filename = f"{sender}_{receiver}_{timestamp}.jpg"
                image_path = images_dir / image_filename
                
                # Send acknowledgment that we're ready for the image
                send_json_message(client_socket, {'status': 'ready'})
                
                # Receive and save the image data
                try:
                    image_data = receive_image(client_socket)
                    with open(image_path, 'wb') as f:
                        f.write(image_data)
                    
                    message_data['image_path'] = str(image_path)
                    
                    # Send success acknowledgment
                    send_json_message(client_socket, {'status': 'success'})
                except Exception as e:
                    print(f"Error saving image: {e}")
                    send_json_message(client_socket, {'status': 'error', 'message': 'Failed to save image'})
                    return {'status': 'error', 'message': 'Failed to save image'}
            
            messages.append(message_data)
            
            with open(message_file, 'w') as f:
                json.dump(messages, f, indent=4)
            
            return {'status': 'success', 'message': 'Message sent'}
        except Exception as e:
            print(f"Error in handle_send_message: {e}")
            return {'status': 'error', 'message': str(e)}

    def handle_get_messages(self, request):
        """
        Handle message retrieval requests.
        
        Args:
            request (dict): The message retrieval request containing user1 and user2
            
        Returns:
            dict: Message data response
        """
        user1 = request.get('user1')
        user2 = request.get('user2')
        
        # Create message file name (sorted usernames)
        usernames = sorted([user1, user2])
        message_file = f'data/messages/{usernames[0]}_{usernames[1]}.json'
        
        if os.path.exists(message_file):
            with open(message_file, 'r') as f:
                messages = json.load(f)
            return {'status': 'success', 'messages': messages}
        return {'status': 'success', 'messages': []}

    def handle_get_user_data(self, request):
        """
        Handle user data retrieval requests.
        
        Args:
            request (dict): The user data request containing username
            
        Returns:
            dict: User data response
        """
        username = request.get('username')
        
        with open('data/users/users.json', 'r') as f:
            users = json.load(f)
        
        if username in users:
            return {'status': 'success', 'user_data': users[username]}
        return {'status': 'error', 'message': 'User not found'}

    def handle_get_all_users(self, request):
        """
        Handle all users retrieval requests.
        
        Args:
            request (dict): The all users request
            
        Returns:
            dict: All users data response
        """
        with open('data/users/users.json', 'r') as f:
            users = json.load(f)
        
        return {'status': 'success', 'users': list(users.keys())}

    def start(self):
        """
        Start the server and begin accepting client connections.
        
        This method:
        1. Listens for incoming connections
        2. Creates a new thread for each client
        3. Handles client communication
        """
        print(f"Server listening on {self.host}:{self.port}")
        while True:
            client_socket, address = self.server_socket.accept()
            print(f"New connection from {address}")
            self.clients[address] = client_socket
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket, address))
            client_thread.start()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Instagram Clone Server')
    parser.add_argument('--port', type=int, help='Port number to use (optional)')
    args = parser.parse_args()
    
    server = InstagramServer(port=args.port)
    server.start() 