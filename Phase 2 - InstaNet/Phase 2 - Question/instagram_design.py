from PIL import Image
import customtkinter as ctk

# --- Colors and Fonts ---
INSTAGRAM_COLORS = {
    "background": "#FAFAFA",
    "primary": "#0095F6",  # Instagram blue
    "text": "#262626",
    "subtext": "#8e8e8e",
    "border": "#DBDBDB",
}

INSTAGRAM_FONTS = {
    "title": ("Arial", 32, "bold"),
    "heading": ("Arial", 18, "bold"),
    "normal": ("Arial", 14),
    "small": ("Arial", 12),
}

PAD_X = 20
PAD_Y = 10

# --- Utility Functions ---

def load_icon(path, size=(24, 24)):
    img = Image.open(path)
    img = img.resize(size, Image.Resampling.LANCZOS)
    return ctk.CTkImage(light_image=img, dark_image=img, size=size)

def create_sidebar_button(parent, text, icon_path, command=None):
    icon = load_icon(icon_path)
    button = ctk.CTkButton(
        parent,
        text=text,
        image=icon,
        compound="left",
        command=command,
        fg_color="transparent",
        text_color=INSTAGRAM_COLORS["text"],
        font=INSTAGRAM_FONTS["heading"],
        hover_color="#efefef",
        anchor="w",
        width=180,
        height=40
    )
    return button

def create_icon_button(parent, icon_path, command=None, size=(32,32)):
    icon = load_icon(icon_path, size=size)
    button = ctk.CTkButton(
        parent,
        text="",
        image=icon,
        command=command,
        width=40,
        height=40,
        fg_color="transparent",
        hover_color="#efefef"
    )
    return button

def create_title(parent, text):
    label = ctk.CTkLabel(
        parent,
        text=text,
        font=INSTAGRAM_FONTS["title"],
        text_color=INSTAGRAM_COLORS["text"]
    )
    return label

def create_card(parent):
    frame = ctk.CTkFrame(
        parent,
        fg_color="white",
        corner_radius=10,
        border_width=1,
        border_color=INSTAGRAM_COLORS["border"]
    )
    return frame

def create_label(parent, text, small=False):
    font = INSTAGRAM_FONTS["small"] if small else INSTAGRAM_FONTS["normal"]
    label = ctk.CTkLabel(
        parent,
        text=text,
        font=font,
        text_color=INSTAGRAM_COLORS["text"]
    )
    return label

def create_divider(parent):
    divider = ctk.CTkLabel(
        parent,
        text="",
        height=1,
        width=200,
        fg_color=INSTAGRAM_COLORS["border"]
    )
    return divider
