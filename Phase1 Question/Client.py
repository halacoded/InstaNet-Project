import socket
import customtkinter as ctk

# === TODO Students to implement this ===
def send_message(entry, textbox):
    # TODO implementation goes here
    # 1. Create a socket.
    client_socket = socket.socket()
    # 2. Connect to localhost, port 12345.
    client_socket.connect(('localhost', 12345))
    # 3. Read message from entry field.
    message = entry.get()
    # 4. Send it to the server.
    client_socket.send(message.encode())
    # 5. Receive and decode reply.
    received  = client_socket.recv(1024).decode()
    # 6. Show the reply in textbox.
    textbox.insert("end",received + "\n")
    # 7. Close the socket.
    client_socket.close()
    pass

# === GUI below (already working) ===
def call_send():
    send_message(entry, textbox)

ctk.set_appearance_mode("light")
app = ctk.CTk()
app.title("Client")
app.geometry("300x200")

entry = ctk.CTkEntry(app, width=200)
entry.pack(pady=10)

btn = ctk.CTkButton(app, text="Send", command=call_send)
btn.pack(pady=5)

textbox = ctk.CTkTextbox(app, height=100)
textbox.pack(pady=10)

app.mainloop()
