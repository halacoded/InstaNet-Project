# InstaNet: Instagram Clone
# Dr. Suood Alroomi - Spring 2025 - Kuwait University - CpE 356 - Project
A local Instagram-like application built with Python, featuring user authentication, image sharing, friend requests, and messaging.

## Features

- User Authentication
- Image Upload and Feed
- Friend Request System
- Messaging System
- Modern GUI with Tkinter
- Local Data Persistence
- Multi-client Server Support

## Setup

1. Install Python 3.8 or higher
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the server:
   ```bash
   python server/server.py
   ```
4. Run the client:
   ```bash
   python client/client.py
   ```

## Project Structure

- `client/`: Client-side application code
- `server/`: Server-side application code
- `data/`: Local data storage
  - `users/`: User information
  - `posts/`: Image posts
  - `messages/`: Chat messages
  - `images/`: Uploaded images

## Default Users

The application comes with 10 default users. You can log in with any of these credentials:

1. username: user1, password: pass1
2. username: user2, password: pass2
... (and so on)

## Note

This is a local application that runs on your machine. All data is stored locally in the `data` directory.
# CHatSocket
