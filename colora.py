import os
import tkinter as tk
import pyautogui
import threading
import time
import pyperclip
import keyboard
import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw
import sys
import mss
from pynput import mouse, keyboard as pynput_keyboard

running = False

def get_pixel_color(x, y):
    with mss.mss() as sct:
        monitor = {"top": y, "left": x, "width": 1, "height": 1}
        img = sct.grab(monitor)
        return img.pixel(0, 0)

def color_picker(main_tk):
    global running
    if running:
        return
    running = True

    preview = tk.Toplevel(main_tk)
    preview.overrideredirect(True)
    preview.attributes('-topmost', True)
    canvas = tk.Canvas(preview, width=100, height=60, highlightthickness=0, bg="black")
    canvas.pack()

    rect = canvas.create_rectangle(10, 10, 90, 40, fill="#000000", outline="#333")
    text = canvas.create_text(50, 50, text="#000000", fill="white", font=("Consolas", 10, "bold"))

    stop_event = threading.Event()
    listeners = {}

    def update_preview():
        while not stop_event.is_set():
            x, y = pyautogui.position()
            try:
                color = get_pixel_color(x, y)
                hex_color = '#%02x%02x%02x' % color
                canvas.itemconfig(rect, fill=hex_color)
                canvas.itemconfig(text, text=hex_color)
                preview.geometry(f"+{x + 20}+{y + 20}")
            except:
                pass
            time.sleep(0.03)

    def on_click(x, y, button, pressed):
        if pressed and button.name == "left":
            try:
                color = get_pixel_color(x, y)
                hex_color = '#%02x%02x%02x' % color
                pyperclip.copy(hex_color)
            except:
                pass
            stop_event.set()
            close_all()
            return False

    def on_press(key):
        if key == pynput_keyboard.Key.esc:
            stop_event.set()
            close_all()
            return False

    def close_all():
        global running
        running = False
        try:
            preview.destroy()
        except:
            pass
        try:
            listeners["mouse"].stop()
        except:
            pass
        try:
            listeners["keyboard"].stop()
        except:
            pass

    threading.Thread(target=update_preview, daemon=True).start()
    listeners["mouse"] = mouse.Listener(on_click=on_click)
    listeners["keyboard"] = pynput_keyboard.Listener(on_press=on_press)
    listeners["mouse"].start()
    listeners["keyboard"].start()

def start_color_picker(main_tk):
    if not running:
        main_tk.after(0, lambda: color_picker(main_tk))

def create_image():
    image = Image.new('RGB', (64, 64), (60, 60, 60))
    draw = ImageDraw.Draw(image)
    draw.rectangle((16, 16, 48, 48), fill="red", outline="white")
    return image

def resource_path(relative_path):
    """Funciona tanto no .py quanto no .exe empacotado"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def quit_app(icon, item, main_tk):
    try:
        icon.stop()
    except:
        pass
    try:
        main_tk.quit()
        main_tk.destroy()
    except:
        pass
    os._exit(0)  # Força encerramento total

def tray_app(main_tk):
    icon = pystray.Icon("Colora")
    icon.icon = Image.open(resource_path("assets/icon.ico"))
    icon.title = "Colora"
    icon.menu = pystray.Menu(
        item('Exit', lambda icon, item: quit_app(icon, item, main_tk))
    )

    keyboard.add_hotkey('windows+shift+c', lambda: start_color_picker(main_tk))
    icon.run()

def main():
    main_tk = tk.Tk()
    main_tk.withdraw()
    threading.Thread(target=tray_app, args=(main_tk,), daemon=True).start()
    main_tk.mainloop()

if __name__ == "__main__":
    main()
