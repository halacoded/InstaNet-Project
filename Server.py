import socket
import customtkinter as ctk
import threading

# === TODO Students to implement this ===
def handle_client(textbox):
    # TODO implementation goes here
    # 1. Create a socket.
    # 2. Bind it to localhost, port 12345.
    # 3. Listen for one connection.
    # 4. Accept a client.
    # 5. Receive message from client.
    # 6. Show the message in textbox.
    # 7. Send back "Hi Client!" as a reply.
    # 8. Close connection and socket.
    pass

# === GUI below (already working) ===
def start_server():
    threading.Thread(target=lambda: handle_client(textbox), daemon=True).start()

ctk.set_appearance_mode("light")
app = ctk.CTk()
app.title("Server")
app.geometry("300x200")

textbox = ctk.CTkTextbox(app, height=100)
textbox.pack(pady=10)

btn = ctk.CTkButton(app, text="Start Server", command=start_server)
btn.pack(pady=10)

app.mainloop()
