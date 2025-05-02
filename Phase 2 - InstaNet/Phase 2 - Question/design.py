import customtkinter as ctk
from PIL import Image, ImageTk
import tkinter as tk

INSTAGRAM_COLORS = {
    "background": "#fafafa",
    "card": "#ffffff",
    "primary": "#3897f0",
    "primary_hover": "#4cb5f9",
    "hover_gray": "#efefef",
    "text_main": "#262626",
    "text_subtle": "#8e8e8e",
    "border": "#dbdbdb"
}
FONT_BOLD = ("Helvetica", 14, "bold")
FONT_REGULAR = ("Helvetica", 12)
FONT_SMALL = ("Helvetica", 10)

# Card-style frame
def create_card(master, width=400, height=500):
    return ctk.CTkFrame(master, fg_color="transparent", corner_radius=20, width=width, height=height)

# Title label
def create_title(master, text):
    return ctk.CTkLabel(master, text=text, font=("Billabong", 40), text_color=INSTAGRAM_COLORS["text_main"])

# Rounded entry
def create_entry(master, placeholder, show=None):
    return ctk.CTkEntry(master, placeholder_text=placeholder, width=260, height=40, corner_radius=20, show=show)

# Beautiful button
def create_button(master, text, command, width=260):
    return ctk.CTkButton(
        master, text=text, command=command, width=width, height=40, corner_radius=20,
        fg_color=INSTAGRAM_COLORS["primary"], hover_color=INSTAGRAM_COLORS["primary_hover"],
        text_color="white", font=FONT_BOLD
    )

# Icon button (for nav bar)
def create_icon_button(master, icon, command, selected=False):
    color = INSTAGRAM_COLORS["primary"] if selected else INSTAGRAM_COLORS["card"]
    hover = INSTAGRAM_COLORS["primary_hover"] if selected else INSTAGRAM_COLORS["hover_gray"]
    return ctk.CTkButton(
        master, text=icon, width=50, height=50, corner_radius=25,
        fg_color=color, hover_color=hover, font=("Helvetica", 20, "bold"), command=command, text_color=INSTAGRAM_COLORS["text_main"]
    )

# Bottom navigation bar
def create_bottom_nav(master, buttons):
    nav = ctk.CTkFrame(master, fg_color=INSTAGRAM_COLORS["card"], height=70, corner_radius=0)
    nav.place(relx=0, rely=1, relwidth=1, anchor="sw")
    for idx, (icon, cmd, selected) in enumerate(buttons):
        btn = create_icon_button(nav, icon, cmd, selected)
        btn.place(relx=0.15 + idx*0.2, rely=0.5, anchor="center")
    return nav

# Floating action button (FAB)
def create_fab(master, command):
    return ctk.CTkButton(
        master, text="➕", width=70, height=70, corner_radius=35,
        fg_color=INSTAGRAM_COLORS["primary"], hover_color=INSTAGRAM_COLORS["primary_hover"],
        font=("Helvetica", 32, "bold"), text_color="white", command=command
    )

# Post card
def create_post_card(master, username, image_path, caption, timestamp):
    card = ctk.CTkFrame(master, fg_color=INSTAGRAM_COLORS["card"], corner_radius=16, border_width=1, border_color=INSTAGRAM_COLORS["border"])
    card.pack(fill="x", padx=30, pady=16)
    ctk.CTkLabel(card, text=username, font=FONT_BOLD, text_color=INSTAGRAM_COLORS["text_main"]).pack(anchor="w", padx=20, pady=(16, 0))
    try:
        image = Image.open(image_path).resize((400, 400))
        photo = ImageTk.PhotoImage(image)
        img_label = ctk.CTkLabel(card, image=photo, text="")
        img_label.image = photo
        img_label.pack(pady=10)
    except Exception:
        ctk.CTkLabel(card, text="Image not found", text_color=INSTAGRAM_COLORS["text_subtle"]).pack()
    ctk.CTkLabel(card, text=caption, font=FONT_REGULAR, text_color=INSTAGRAM_COLORS["text_main"]).pack(anchor="w", padx=20)
    ctk.CTkLabel(card, text=timestamp, font=FONT_SMALL, text_color=INSTAGRAM_COLORS["text_subtle"]).pack(anchor="w", padx=20, pady=(0, 10))
    return card

def setup_gui(self):
    self.root = ctk.CTk()
    self.root.title("INstaNet")
    self.root.geometry("400x700")
    self.root.configure(fg_color=INSTAGRAM_COLORS["background"])

    # Gradient background
    self.gradient_canvas = tk.Canvas(self.root, highlightthickness=0)
    self.gradient_canvas.place(x=0, y=0, relwidth=1, relheight=1)
    self.draw_gradient(self.gradient_canvas, 400, 700, "#f58529", "#dd2a7b")

    # Bind resize event
    self.root.bind("<Configure>", self.on_resize)

    # ... rest of your setup_gui code ...

def on_resize(self, event):
    # Redraw the gradient to fill the new window size
    width = event.width
    height = event.height
    self.gradient_canvas.config(width=width, height=height)
    self.gradient_canvas.delete("all")
    self.draw_gradient(self.gradient_canvas, width, height, "#f58529", "#dd2a7b") 