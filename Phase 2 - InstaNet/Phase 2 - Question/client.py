"""
Dr. Suood Alroomi - Spring 2025 - Kuwait University - CpE 356 - Project

This module implements the client-side functionality of the Instagram Clone application.

The module provides:
- A GUI interface using customtkinter
- User authentication and session management
- Post creation and viewing
- Friend management and messaging
- Real-time updates and notifications
- Image message support

The client communicates with the server using JSON messages over sockets
and provides a modern, Instagram-like user interface.
"""

import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import customtkinter as ctk
from design import create_card, create_title, create_entry, create_button, create_icon_button, create_bottom_nav, create_fab, create_post_card
from PIL import Image, ImageTk
from datetime import datetime
import base64
import sys
import argparse
from socket_utils import (
    create_client_socket, send_json_message, receive_json_message,
    send_json_message_with_image, receive_json_message_with_image
)
from constants import (
    INSTAGRAM_COLORS, FONT_BOLD, FONT_REGULAR, FONT_SMALL,
    DEFAULT_HOST, DEFAULT_PORT, MAX_RETRIES, RETRY_DELAY,
    WINDOW_TITLE, WINDOW_SIZE, LOGIN_FRAME_SIZE,
    INPUT_FIELD_HEIGHT, BUTTON_HEIGHT, CORNER_RADIUS, PADDING,
    MESSAGE_BUBBLE_RADIUS, MESSAGE_WRAP_LENGTH, MESSAGE_PADDING, MESSAGE_VERTICAL_PADDING
)
import io
import os
import shutil
from pathlib import Path

class InstagramClient:
    """
    The main client class for the Instagram Clone application.
    
    This class handles:
    - Server connection and communication
    - User interface creation and management
    - User authentication
    - Post creation and viewing
    - Friend management
    - Messaging functionality
    """
    
    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT, max_retries=MAX_RETRIES, retry_delay=RETRY_DELAY):
        """
        Initialize the Instagram client.
        
        Args:
            host (str): The server host address
            port (int): The server port number
            max_retries (int): Maximum number of connection retries
            retry_delay (int): Delay between retries in seconds
        """
        self.host = host
        self.port = port
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.connected = False
        self.current_user = None
        self.socket = None
        self.last_message_timestamp = None
        self.setup_gui()
        self.connect_to_server()

    def connect_to_server(self):
        """
        Establish connection to the server with retry logic.
        
        Raises:
            RuntimeError: If connection fails after all retries
        """
        try:
            self.socket = create_client_socket(self.host, self.port, self.max_retries, self.retry_delay)
            self.connected = True
            print(f"Connected to server at {self.host}:{self.port}")
        except RuntimeError as e:
            print(str(e))
            messagebox.showerror("Connection Error", 
                               f"Could not connect to server at {self.host}:{self.port}\n"
                               "Please make sure the server is running and try again.")
            sys.exit(1)

    def send_message(self, friend):
        """
        Send a message to a friend.
        
        Args:
            friend (str): The username of the friend to message
            
        Raises:
            RuntimeError: If message sending fails
        """
        message = self.message_entry.get()
        if message:
            request = {
                'action': 'send_message',
                'sender': self.current_user,
                'receiver': friend,
                'message': message,
                'timestamp': datetime.now().isoformat(),
                'is_image': False
            }
            send_json_message(self.socket, request)
            response = receive_json_message(self.socket)

            if response['status'] == 'success':
                self.message_entry.delete(0, tk.END)
                self.load_messages(friend)
            else:
                messagebox.showerror("Error", "Failed to send message")

    def send_image(self, friend):
        """
        Send an image to a friend.
        
        Args:
            friend (str): The username of the friend to send the image to
            
        Raises:
            RuntimeError: If image sending fails
        """
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif")]
        )
        
        if file_path:
            try:
                with open(file_path, 'rb') as f:
                    image_data = f.read()
                
                request = {
                    'action': 'send_message',
                    'sender': self.current_user,
                    'receiver': friend,
                    'message': "Image",
                    'timestamp': datetime.now().isoformat(),
                    'is_image': True
                }
                
                send_json_message_with_image(self.socket, request, image_data)
                response = receive_json_message(self.socket)
                
                if response['status'] == 'success':
                    self.load_messages(friend)
                else:
                    messagebox.showerror("Error", "Failed to send image")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to send image: {str(e)}")

    def reconnect(self):
        """
        Attempt to reconnect to the server.
        
        This is called when the connection is lost and the user needs to
        re-establish communication with the server.
        """
        if self.socket:
            self.socket.close()
        self.connect_to_server()

    def setup_gui(self):
        """
        Initialize and set up the graphical user interface.
        
        This method creates all the necessary UI components including:
        - Login screen
        - Main content area
        - Navigation bars
        - Message interface
        - Post creation interface
        """
        self.root = ctk.CTk()
        self.root.title(WINDOW_TITLE)
        self.root.geometry(WINDOW_SIZE)
        self.root.configure(fg_color=INSTAGRAM_COLORS["background"])

        # Login frame (centered card)
        self.login_frame = ctk.CTkFrame(self.root, width=LOGIN_FRAME_SIZE[0], height=LOGIN_FRAME_SIZE[1])
        self.login_frame.configure(fg_color="transparent")
        self.login_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Logo/Title
        logo_label = ctk.CTkLabel(
            self.login_frame,
            text="InstaNet",
            font=("Billabong", 48),
            text_color="#000000"
        )
        logo_label.pack(pady=(40, 20))
        
        # Username entry
        self.username_entry = create_entry(self.login_frame, "Username")
        self.username_entry.configure(
            fg_color="#fafafa",
            border_color="#dbdbdb",
            width=280,
            height=40,
            text_color="#000000"
        )
        self.username_entry.pack(pady=10)
        
        # Password entry
        self.password_entry = create_entry(self.login_frame, "Password", show="*")
        self.password_entry.configure(
            fg_color="#fafafa",
            border_color="#dbdbdb",
            width=280,
            height=40,
            text_color="#000000"
        )
        self.password_entry.pack(pady=10)
        
        # Login button
        login_button = ctk.CTkButton(
            self.login_frame,
            text="Log In",
            command=self.login,
            width=280,
            height=40,
            fg_color=INSTAGRAM_COLORS["primary"],
            hover_color=INSTAGRAM_COLORS["primary_hover"],
            text_color="white",
            font=("Helvetica", 14, "bold")
        )
        login_button.pack(pady=(20, 10))

        # Main content area (hidden at start)
        self.content_frame = ctk.CTkFrame(self.root, fg_color="transparent")

        # Top bar (hidden at start)
        self.top_bar = ctk.CTkFrame(self.root, fg_color="transparent", height=60)
        ctk.CTkLabel(self.top_bar, text="InstaNet", font=("Billabong", 32), text_color=INSTAGRAM_COLORS["text_main"]).pack(side="left", padx=20)
        ctk.CTkButton(self.top_bar, text="💬", width=50, height=50, corner_radius=20, fg_color=INSTAGRAM_COLORS["primary"], hover_color=INSTAGRAM_COLORS["primary_hover"], command=self.show_messages).pack(side="right", padx=10)
        ctk.CTkButton(self.top_bar, text="🤝", width=50, height=50, corner_radius=20, fg_color=INSTAGRAM_COLORS["primary"], hover_color= INSTAGRAM_COLORS["primary_hover"], command=self.show_friend_requests).pack(side="right", padx=10)

        # Bottom nav bar (hidden at start)
        self.nav_bar = ctk.CTkFrame(self.root, fg_color="transparent", height=70)
        ctk.CTkButton(self.nav_bar, text="🏠", width=50, height=50, corner_radius=25, fg_color="transparent", hover_color=INSTAGRAM_COLORS["hover_gray"], command=self.show_home).place(relx=0.1, rely=0.5, anchor="center")
         # Upload button (center, floating)
        self.upload_btn = ctk.CTkButton(self.root, text="➕", width=70, height=70, corner_radius=35, fg_color=INSTAGRAM_COLORS["primary"], hover_color=INSTAGRAM_COLORS["primary_hover"], text_color="white", font=("Helvetica", 32, "bold"), command=self.show_upload)

        # Universal back button (hidden at start)
        self.back_btn = ctk.CTkButton(
            self.root, text="←", width=40, height=40, corner_radius=20,
            fg_color=INSTAGRAM_COLORS["primary"], hover_color=INSTAGRAM_COLORS["primary_hover"],
            text_color="white", font=("Helvetica", 20, "bold"), command=self.go_back
        )
        self.page_stack = []  # For navigation history

        # Bind resize event to update layout
        self.root.bind("<Configure>", self.on_resize)

    def on_resize(self, event):
        """
        Handle window resize events.
        
        Args:
            event: The resize event containing new window dimensions
        """
        width = event.width
        height = event.height
        self.login_frame.place(relx=0.5, rely=0.5, anchor="center")

    def login(self):
        """
        Handle user login process.
        
        This method:
        1. Collects username and password
        2. Sends authentication request to server
        3. Updates UI based on login success/failure
        """
        username = self.username_entry.get().lower()
        password = self.password_entry.get()

        request = {
            'action': 'login',
            'username': username,
            'password': password
        }

        self.socket.send(json.dumps(request).encode('utf-8'))
        response = json.loads(self.socket.recv(4096).decode('utf-8'))

        if response['status'] == 'success':
            self.current_user = username
            self.login_frame.place_forget()
            self.top_bar.pack(side="top", fill="x")
            self.content_frame.pack(expand=True, fill="both")
            self.nav_bar.pack(side="bottom", fill="x")
            self.upload_btn.place(relx=0.5, rely=0.93, anchor="center")
            self.show_home()
        else:
            messagebox.showerror("Error", "Invalid credentials")

    def show_home(self):
        """
        Display the home feed with posts from friends.
        """
        self.back_btn.place_forget()
        if "home" not in self.page_stack:
            self.page_stack.append("home")
        self.clear_content()
        self.nav_bar.pack(side="bottom", fill="x")
        self.upload_btn.place(relx=0.5, rely=0.93, anchor="center")
        scrollable_feed = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
        scrollable_feed.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Load posts from local JSON file
        try:
            with open('data/posts/posts.json', 'r') as f:
                posts = json.load(f)
            
            # Display posts in reverse chronological order
            for post in reversed(posts):
                self.create_post_widget(post, parent=scrollable_feed)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load feed: {str(e)}")

    def create_post_widget(self, post, parent=None):
        """
        Create a widget for displaying a post.
        """
        if parent is None:
            parent = self.content_frame
        post_frame = ctk.CTkFrame(
            parent,
            fg_color="transparent",
            corner_radius=10
        )
        post_frame.pack(fill="x", padx=20, pady=10)

        # Username and timestamp
        header_frame = ctk.CTkFrame(post_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        username_label = ctk.CTkLabel(
            header_frame,
            text=post['username'],
            font=("Helvetica", 14, "bold"),
            text_color="#000000"
        )
        username_label.pack(side="left")
        
        timestamp_label = ctk.CTkLabel(
            header_frame,
            text=post['timestamp'],
            font=("Helvetica", 10)
        )
        timestamp_label.pack(side="right")

        # Image
        try:
            image_path = post['image_path']
            if os.path.exists(image_path):
                image = Image.open(image_path)
                image = image.resize((400, 400), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                image_label = ctk.CTkLabel(post_frame, image=photo, text="")
                image_label.image = photo
                image_label.pack(pady=5)
            else:
                ctk.CTkLabel(post_frame, text="Image not found", font=("Helvetica", 12)).pack(pady=5)
        except Exception as e:
            print(f"Error loading image: {e}")
            ctk.CTkLabel(post_frame, text="Error loading image", font=("Helvetica", 12)).pack(pady=5)

        # Caption
        if post.get('caption'):
            caption_label = ctk.CTkLabel(
                post_frame,
                text=post['caption'],
                font=("Helvetica", 12),
                text_color="#000000",
                wraplength=400
            )
            caption_label.pack(padx=10, pady=5)

    def show_search(self):
        """
        Display the search interface for finding users.
        
        This method:
        1. Clears current content
        2. Creates a search interface
        3. Fetches and displays all users
        4. Allows sending friend requests
        """
        self.clear_content()
        self.back_btn.place(relx=0.95, rely=0.95, anchor="se")
        self.page_stack.append("search")
        
        search_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        search_frame.pack(fill="x", padx=20, pady=10)
        
        search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search users...",
            width=300,
            height=40
        )
        search_entry.pack(side="left", padx=5)
        
        search_button = ctk.CTkButton(
            search_frame,
            text="Search",
            width=60,
            height=40,
            command=lambda: self.search_users(search_entry.get())
        )
        search_button.pack(side="right", padx=5)
        
        # Get all users
        request = {'action': 'get_all_users'}
        send_json_message(self.socket, request)
        response = receive_json_message(self.socket)
        
        if response['status'] == 'success':
            users_frame = ctk.CTkScrollableFrame(self.content_frame, fg_color="transparent")
            users_frame.pack(fill="both", expand=True, padx=20, pady=10)
            
            for user in response['users']:
                if user != self.current_user:
                    user_frame = ctk.CTkFrame(users_frame, fg_color="transparent")
                    user_frame.pack(fill="x", pady=5)
                    
                    ctk.CTkLabel(
                        user_frame,
                        text=user,
                        font=("Helvetica", 14),
                        text_color="#000000"
                    ).pack(side="left", padx=10)
                    
                    ctk.CTkButton(
                        user_frame,
                        text="Add Friend",
                        width=100,
                        height=30,
                        command=lambda u=user: self.send_friend_request(u)
                    ).pack(side="right", padx=10)

    def show_friend_requests(self):
        """
        Display pending friend requests and available users to add as friends.
        
        This method:
        1. Clears current content
        2. Shows pending requests at the top
        3. Shows available users below
        """
        self.clear_content()
        self.back_btn.place(relx=0.95, rely=0.95, anchor="se")
        if "friend_requests" not in self.page_stack:
            self.page_stack.append("friend_requests")
        
        # Main scrollable frame with white background
        main_frame = ctk.CTkScrollableFrame(self.content_frame, fg_color="white")
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Friend Requests Section
        requests_label = ctk.CTkLabel(
            main_frame,
            text="Friend Requests",
            font=("Helvetica", 18, "bold"),
            text_color="#000000"
        )
        requests_label.pack(pady=(10, 5), anchor="w")
        
        # Get user data to check requests
        request = {
            'action': 'get_user_data',
            'username': self.current_user
        }
        send_json_message(self.socket, request)
        response = receive_json_message(self.socket)
        
        if response['status'] == 'success':
            requests = response['user_data'].get('requests', [])
            if not requests:
                ctk.CTkLabel(
                    main_frame,
                    text="No pending friend requests",
                    font=("Helvetica", 14),
                    text_color="#000000"
                ).pack(pady=10)
            else:
                for requester in requests:
                    request_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
                    request_frame.pack(fill="x", pady=5)
                    
                    ctk.CTkLabel(
                        request_frame,
                        text=requester,
                        font=("Helvetica", 14),
                        text_color="#000000"
                    ).pack(side="left", padx=10)
                    
                    ctk.CTkButton(
                        request_frame,
                        text="Accept",
                        width=80,
                        height=30,
                        fg_color=INSTAGRAM_COLORS["primary"],
                        hover_color=INSTAGRAM_COLORS["primary_hover"],
                        command=lambda r=requester: self.accept_friend_request(r)
                    ).pack(side="right", padx=5)
                    
                    ctk.CTkButton(
                        request_frame,
                        text="Reject",
                        width=80,
                        height=30,
                        fg_color="#ff4444",
                        hover_color="#ff6666",
                        command=lambda r=requester: self.reject_friend_request(r)
                    ).pack(side="right", padx=5)
        
        # Divider line
        divider = ctk.CTkFrame(main_frame, height=1, fg_color="#dbdbdb")
        divider.pack(fill="x", pady=20)
        
        # Available Users Section
        users_label = ctk.CTkLabel(
            main_frame,
            text="Add Friends",
            font=("Helvetica", 18, "bold"),
            text_color="#000000"
        )
        users_label.pack(pady=(0, 5), anchor="w")
        
        # Get all users
        request = {'action': 'get_all_users'}
        send_json_message(self.socket, request)
        response = receive_json_message(self.socket)
        
        if response['status'] == 'success':
            # Get current user's friends
            request = {
                'action': 'get_user_data',
                'username': self.current_user
            }
            send_json_message(self.socket, request)
            user_response = receive_json_message(self.socket)
            
            if user_response['status'] == 'success':
                current_friends = user_response['user_data'].get('friends', [])
                
                for user in response['users']:
                    if user != self.current_user and user not in current_friends:
                        user_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
                        user_frame.pack(fill="x", pady=5)
                        
                        ctk.CTkLabel(
                            user_frame,
                            text=user,
                            font=("Helvetica", 14),
                            text_color="#000000"
                        ).pack(side="left", padx=10)
                        
                        ctk.CTkButton(
                            user_frame,
                            text="Add Friend",
                            width=100,
                            height=30,
                            command=lambda u=user: self.send_friend_request(u)
                        ).pack(side="right", padx=10)

    def accept_friend_request(self, requester):
        """
        Accept a friend request.
        
        Args:
            requester (str): The username of the person who sent the request
        """
        request = {
            'action': 'accept_friend_request',
            'user': self.current_user,
            'friend': requester
        }
        send_json_message(self.socket, request)
        response = receive_json_message(self.socket)
        
        if response['status'] == 'success':
            # Refresh the requests view while maintaining navigation state
            current_page = self.page_stack[-1]
            self.show_friend_requests()
            if current_page not in self.page_stack:
                self.page_stack.append(current_page)
        else:
            messagebox.showerror("Error", "Failed to accept friend request")

    def reject_friend_request(self, requester):
        """
        Reject a friend request.
        
        Args:
            requester (str): The username of the person who sent the request
        """
        request = {
            'action': 'reject_friend_request',
            'user': self.current_user,
            'friend': requester
        }
        send_json_message(self.socket, request)
        response = receive_json_message(self.socket)
        
        if response['status'] == 'success':
            # Refresh the requests view while maintaining navigation state
            current_page = self.page_stack[-1]
            self.show_friend_requests()
            if current_page not in self.page_stack:
                self.page_stack.append(current_page)
        else:
            messagebox.showerror("Error", "Failed to reject friend request")

    def send_friend_request(self, user):
        """
        Send a friend request to another user.
        
        Args:
            user (str): The username to send the request to
        """
        request = {
            'action': 'send_friend_request',
            'sender': self.current_user,
            'receiver': user
        }
        send_json_message(self.socket, request)
        response = receive_json_message(self.socket)
        
        if response['status'] == 'success':
            messagebox.showinfo("Success", "Friend request sent")
        else:
            messagebox.showerror("Error", "Failed to send friend request")

    def start_chat(self, friend):
        """
        Start a chat with a friend.
        
        Args:
            friend (str): The username of the friend to chat with
        """
        self.show_messages(selected_friend=friend)

    def show_upload(self):
        """
        Display the post upload interface.
        
        This method:
        1. Clears current content
        2. Creates upload interface
        3. Handles image selection
        4. Manages post creation
        """
        self.clear_content()
        self.back_btn.place(relx=0.95, rely=0.95, anchor="se")
        self.page_stack.append("upload")
        
        upload_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        upload_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Image preview
        self.image_preview = ctk.CTkLabel(
            upload_frame,
            text="No image selected",
            font=("Helvetica", 14),
            text_color="#000000"
        )
        self.image_preview.pack(pady=20)
        
        # Choose image button
        choose_button = ctk.CTkButton(
            upload_frame,
            text="Choose Image",
            width=200,
            height=40,
            command=self.choose_image
        )
        choose_button.pack(pady=10)
        
        # Caption entry
        self.caption_entry = ctk.CTkEntry(
            upload_frame,
            placeholder_text="Write a caption...",
            width=300,
            height=40
        )
        self.caption_entry.pack(pady=10)
        
        # Upload button
        upload_button = ctk.CTkButton(
            upload_frame,
            text="Upload",
            width=200,
            height=40,
            fg_color=INSTAGRAM_COLORS["primary"],
            hover_color=INSTAGRAM_COLORS["primary_hover"],
            command=self.post_image
        )
        upload_button.pack(pady=10)

    def choose_image(self):
        """
        Open a file dialog to choose an image for upload.
        
        This method:
        1. Opens a file dialog
        2. Validates the selected file
        3. Updates the preview
        4. Stores the image path for upload
        """
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png")]
        )
        if file_path:
            try:
                image = Image.open(file_path)
                image = image.resize((300, 300), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                self.image_preview.configure(image=photo, text="")
                self.image_preview.image = photo
                self.selected_image_path = file_path
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {e}")

    def post_image(self):
        """
        Upload the selected image to the server.
        """
        if not self.selected_image_path:
            messagebox.showerror("Error", "Please select an image first")
            return
            
        try:
            # Read the image file
            with open(self.selected_image_path, 'rb') as f:
                image_data = f.read()
            
            # Get caption
            caption = self.caption_entry.get()
            
            # Prepare the upload request
            request = {
                'action': 'upload_post',
                'username': self.current_user,
                'caption': caption,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Send the request and image data
            send_json_message_with_image(self.socket, request, image_data)
            
            # Wait for server response
            response = receive_json_message(self.socket)
            
            if response['status'] == 'success':
                messagebox.showinfo("Success", "Image uploaded successfully")
                self.show_home()  # Refresh feed
            else:
                messagebox.showerror("Error", response.get('message', 'Failed to upload image'))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to upload image: {str(e)}")

    def show_messages(self, selected_friend=None):
        """
        Display the messaging interface.
        
        Args:
            selected_friend (str, optional): The friend to start chatting with
            
        This method:
        1. Clears current content
        2. Creates message interface
        3. Loads message history
        4. Sets up real-time updates
        """
        self.clear_content()
        self.back_btn.place(relx=0.95, rely=0.95, anchor="se")
        self.page_stack.append("messages")
        
        # Main messages container with proper spacing
        messages_frame = ctk.CTkFrame(self.content_frame, fg_color=INSTAGRAM_COLORS["background"])
        messages_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        if not selected_friend:
            # Friends list with modern styling (only shown when no chat is selected)
            friends_frame = ctk.CTkFrame(messages_frame, fg_color="white")
            friends_frame.pack(fill="both", expand=True, padx=0, pady=0)
            
            # Friends list header
            friends_header = ctk.CTkFrame(friends_frame, fg_color="white", height=60)
            friends_header.pack(fill="x", padx=20, pady=10)
            ctk.CTkLabel(
                friends_header,
                text="Messages",
                font=("Helvetica", 20, "bold"),
                text_color=INSTAGRAM_COLORS["text_main"]
            ).pack(side="left")
            
            # Get user data to show friends
            request = {
                'action': 'get_user_data',
                'username': self.current_user
            }
            send_json_message(self.socket, request)
            response = receive_json_message(self.socket)
            
            if response['status'] == 'success':
                friends = response['user_data'].get('friends', [])
                if not friends:
                    ctk.CTkLabel(
                        friends_frame,
                        text="No friends yet",
                        font=("Helvetica", 14),
                        text_color=INSTAGRAM_COLORS["text_subtle"]
                    ).pack(pady=20)
                else:
                    # Scrollable friends list
                    friends_scroll = ctk.CTkScrollableFrame(friends_frame, fg_color="white")
                    friends_scroll.pack(fill="both", expand=True, padx=0, pady=0)
                    
                    for friend in friends:
                        friend_button = ctk.CTkButton(
                            friends_scroll,
                            text=friend,
                            width=230,
                            height=60,
                            fg_color="white",
                            hover_color=INSTAGRAM_COLORS["hover_gray"],
                            text_color=INSTAGRAM_COLORS["text_main"],
                            font=("Helvetica", 14),
                            anchor="w",
                            command=lambda f=friend: self.start_chat(f)
                        )
                        friend_button.pack(pady=2, padx=10)
        
        else:
            # Full-width chat area when a friend is selected
            self.current_chat_friend = selected_friend
            
            # Chat header with friend's name
            chat_header = ctk.CTkFrame(messages_frame, fg_color="white", height=60)
            chat_header.pack(fill="x", padx=0, pady=0)
            ctk.CTkLabel(
                chat_header,
                text=selected_friend,
                font=("Helvetica", 18, "bold"),
                text_color=INSTAGRAM_COLORS["text_main"]
            ).pack(pady=20)
            
            # Messages area with proper spacing
            self.messages_area = ctk.CTkScrollableFrame(messages_frame, fg_color=INSTAGRAM_COLORS["background"])
            self.messages_area.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Message input area with modern styling
            message_frame = ctk.CTkFrame(messages_frame, fg_color="white", height=70)
            message_frame.pack(fill="x", padx=0, pady=0)
            
            self.message_entry = ctk.CTkEntry(
                message_frame,
                placeholder_text="Message...",
                width=300,
                height=40,
                fg_color=INSTAGRAM_COLORS["hover_gray"],
                border_color=INSTAGRAM_COLORS["hover_gray"],
                text_color=INSTAGRAM_COLORS["text_main"],
                font=("Helvetica", 14)
            )
            self.message_entry.pack(side="left", padx=15, pady=15)
            
            # Image upload button
            image_button = ctk.CTkButton(
                message_frame,
                text="📷",
                width=40,
                height=40,
                fg_color=INSTAGRAM_COLORS["primary"],
                hover_color=INSTAGRAM_COLORS["primary_hover"],
                text_color="white",
                font=("Helvetica", 14, "bold"),
                command=lambda: self.send_image(selected_friend)
            )
            image_button.pack(side="right", padx=5, pady=15)
            
            send_button = ctk.CTkButton(
                message_frame,
                text="Send",
                width=80,
                height=40,
                fg_color=INSTAGRAM_COLORS["primary"],
                hover_color=INSTAGRAM_COLORS["primary_hover"],
                text_color="white",
                font=("Helvetica", 14, "bold"),
                command=lambda: self.send_message(selected_friend)
            )
            send_button.pack(side="right", padx=15, pady=15)
            
            # Load existing messages
            self.load_messages(selected_friend)
            # Start auto-refresh
            self.auto_refresh_chat()

    def add_message_bubble(self, parent, sender, text, time_str, sent_by_me, is_image=False, image_path=None):
        """
        Add a message bubble to the chat.
        
        Args:
            parent: The parent widget to add the bubble to
            sender (str): The username of the message sender
            text (str): The message text
            time_str (str): The message timestamp
            sent_by_me (bool): Whether the message was sent by the current user
            is_image (bool): Whether the message contains an image
            image_path (str): Path to the image file if is_image is True
        """
        # Create a container frame for the entire message
        message_container = ctk.CTkFrame(parent, fg_color="transparent")
        message_container.pack(fill="x", pady=5)
        
        if sent_by_me:
            # Right-aligned for current user's messages
            message_container.pack(anchor="e")
            bubble_color = INSTAGRAM_COLORS["primary"]
            text_color = "white"
            bubble_frame = ctk.CTkFrame(message_container, fg_color="transparent")
            bubble_frame.pack(anchor="e")
        else:
            # Left-aligned for sender's messages
            message_container.pack(anchor="w")
            bubble_color = "white"
            text_color = INSTAGRAM_COLORS["text_main"]
            bubble_frame = ctk.CTkFrame(message_container, fg_color="transparent")
            bubble_frame.pack(anchor="w")
        
        # Main message bubble
        bubble = ctk.CTkFrame(
            bubble_frame,
            fg_color=bubble_color,
            corner_radius=20
        )
        bubble.pack(padx=10)
        
        if is_image and image_path:
            try:
                # Load and resize image
                image = Image.open(image_path)
                image.thumbnail((300, 300))  # Resize while maintaining aspect ratio
                photo = ImageTk.PhotoImage(image)
                
                # Create image label
                image_label = ctk.CTkLabel(
                    bubble,
                    image=photo,
                    text=""
                )
                image_label.image = photo  # Keep a reference
                image_label.pack(padx=15, pady=8)
            except Exception as e:
                print(f"Error loading image: {e}")
                text = "Failed to load image"
            message_label = ctk.CTkLabel(
                bubble,
                text=text,
                font=("Helvetica", 14),
                text_color=text_color,
                wraplength=300,
                justify="left"
            )
            message_label.pack(padx=15, pady=8)
        else:
            # Message text with proper wrapping
            message_label = ctk.CTkLabel(
                bubble,
                text=text,
                font=("Helvetica", 14),
                text_color=text_color,
                wraplength=300,
                justify="left"
            )
            message_label.pack(padx=15, pady=8)
        
        # Timestamp with subtle styling
        time_label = ctk.CTkLabel(
            bubble_frame,
            text=time_str,
            font=("Helvetica", 11),
            text_color=INSTAGRAM_COLORS["text_subtle"]
        )
        time_label.pack(pady=2)

    def load_messages(self, friend):
        """
        Load and display messages with a friend.
        
        Args:
            friend (str): The username of the friend to load messages with
        """
        request = {
            'action': 'get_messages',
            'user1': self.current_user,
            'user2': friend
        }
        send_json_message(self.socket, request)
        response = receive_json_message(self.socket)
        
        if response['status'] == 'success':
            # Clear existing messages
            for widget in self.messages_area.winfo_children():
                widget.destroy()
            
            # Add messages
            for message in response['messages']:
                sent_by_me = message['sender'] == self.current_user
                time_str = datetime.fromisoformat(message['timestamp']).strftime("%H:%M")
                self.add_message_bubble(
                    self.messages_area,
                    message['sender'],
                    message['message'],
                    time_str,
                    sent_by_me,
                    message.get('is_image', False),
                    message.get('image_path')
                )
            
            # Scroll to bottom
            self.messages_area._parent_canvas.yview_moveto(1.0)

    def auto_refresh_chat(self):
        """
        Set up automatic refresh of the chat messages.
        
        This method:
        1. Checks for new messages periodically
        2. Updates the chat display
        3. Maintains scroll position
        """
        if hasattr(self, 'current_chat_friend'):
            self.load_messages(self.current_chat_friend)
            self.root.after(5000, self.auto_refresh_chat)  # Refresh every 5 seconds

    def show_profile(self):
        """
        Display the user's profile.
        
        This method:
        1. Clears current content
        2. Shows user information
        3. Displays user's posts
        4. Provides logout option
        """
        self.clear_content()
        self.back_btn.place(relx=0.95, rely=0.95, anchor="se")
        self.page_stack.append("profile")
        
        profile_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        profile_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Profile info
        info_frame = ctk.CTkFrame(profile_frame, fg_color="transparent")
        info_frame.pack(fill="x", pady=20)
        
        ctk.CTkLabel(
            info_frame,
            text=self.current_user,
            font=("Helvetica", 24, "bold"),
            text_color="#000000"
        ).pack(pady=10)
        
        # Get user's posts
        request = {'action': 'get_feed'}
        send_json_message(self.socket, request)
        response = receive_json_message(self.socket)
        
        if response['status'] == 'success':
            user_posts = [post for post in response['posts'] if post['username'] == self.current_user]
            
            if user_posts:
                posts_frame = ctk.CTkScrollableFrame(profile_frame, fg_color="transparent")
                posts_frame.pack(fill="both", expand=True)
                
                for post in reversed(user_posts):
                    self.create_post_widget(post, parent=posts_frame)
            else:
                ctk.CTkLabel(
                    profile_frame,
                    text="No posts yet",
                    font=("Helvetica", 14),
                    text_color="#000000"
                ).pack(pady=20)
        
        # Logout button
        logout_button = ctk.CTkButton(
            profile_frame,
            text="Logout",
            width=200,
            height=40,
            fg_color="#ff4444",
            hover_color="#ff6666",
            command=self.logout
        )
        logout_button.pack(pady=20)

    def logout(self):
        """
        Handle user logout.
        
        This method:
        1. Closes the socket connection
        2. Resets user state
        3. Returns to login screen
        """
        if self.socket:
            self.socket.close()
        self.current_user = None
        self.connected = False
        self.clear_content()
        self.top_bar.pack_forget()
        self.nav_bar.pack_forget()
        self.upload_btn.place_forget()
        self.back_btn.place_forget()
        self.login_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.connect_to_server()  # Reconnect for next login

    def clear_content(self):
        """
        Clear the current content frame.
        
        This method removes all widgets from the content frame
        to prepare for displaying new content.
        """
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def go_back(self):
        """
        Handle back navigation.
        
        This method:
        1. Pops the last page from the navigation stack
        2. Returns to the previous view
        3. Updates UI accordingly
        """
        if len(self.page_stack) > 1:  # Only go back if there's more than one page
            current_page = self.page_stack.pop()  # Remove current page
            previous_page = self.page_stack[-1]  # Get the previous page
            
            if previous_page == "home":
                self.show_home()
            elif previous_page == "messages":
                self.show_messages()
            elif previous_page == "friend_requests":
                self.show_friend_requests()
            elif previous_page == "upload":
                self.show_upload()
            elif previous_page == "profile":
                self.show_profile()
            elif previous_page == "search":
                self.show_search()

    def run(self):
        """
        Start the client application.
        
        This method:
        1. Starts the main event loop
        2. Handles application shutdown
        """
        self.root.mainloop()
        if self.socket:
            self.socket.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Instagram Client')
    parser.add_argument('--port', type=int, default=5000, help='Port number to connect to')
    parser.add_argument('--host', type=str, default='localhost', help='Host to connect to')
    args = parser.parse_args()
    
    client = InstagramClient(host=args.host, port=args.port)
    client.run() 