import os
import time
import threading
import ctypes
from ctypes import wintypes
import pyautogui
import keyboard
import cv2
import numpy as np
import shutil
import sys

# ========= Config =========
IMAGE_PATH = "pesca.png"
CONFIDENCE = 0.8
SEARCH_INTERVAL = 0.2
COOLDOWN_AFTER_DETECT = 3
USE_GRAYSCALE = True
DOUBLE_TAP_GAP = 0.5
REGION = None

# ========= Estado =========
paused = False
image_visible = False
want_region_selection = False
fish_count = 0  # contador

# ========= WinAPI (keybd_event) =========
VK_LCONTROL = 0xA2      # Left Ctrl
VK_RMENU    = 0xA5      # Right Alt (AltGr)
SCAN_LCTRL  = 0x1D
SCAN_RALT   = 0x38

KEYEVENTF_KEYUP       = 0x0002
KEYEVENTF_EXTENDEDKEY = 0x0001

user32 = ctypes.windll.user32

def _keybd_event(vk: int, scan: int, key_up: bool = False, extended: bool = False):
    flags = (KEYEVENTF_KEYUP if key_up else 0) | (KEYEVENTF_EXTENDEDKEY if extended else 0)
    user32.keybd_event(ctypes.c_ubyte(vk), ctypes.c_ubyte(scan), flags, 0)

def press_altgr_once():
    """ALT GR = Ctrl izquierdo + Alt derecho (keybd_event)"""
    _keybd_event(VK_LCONTROL, SCAN_LCTRL, key_up=False, extended=False)
    _keybd_event(VK_RMENU,    SCAN_RALT,  key_up=False, extended=True)
    _keybd_event(VK_RMENU,    SCAN_RALT,  key_up=True,  extended=True)
    _keybd_event(VK_LCONTROL, SCAN_LCTRL, key_up=True,  extended=False)

def double_press_altgr():
    press_altgr_once()
    time.sleep(DOUBLE_TAP_GAP)
    press_altgr_once()

# ========= Util: imprimir en la MISMA línea =========
def status_line(text: str):
    width = shutil.get_terminal_size((80, 20)).columns
    # Sobrescribe la línea actual y limpia el resto con espacios
    sys.stdout.write("\r" + text.ljust(width))
    sys.stdout.flush()

def println(text: str):
    # Imprime en una nueva línea (para mensajes puntuales) y luego re-muestra el estado
    sys.stdout.write("\n" + text + "\n")
    sys.stdout.flush()

# ========= Hotkeys =========
def toggle_pause():
    global paused
    paused = not paused
    println("⏸️ Pausado" if paused else "▶️ Reanudado")

def request_region_selection():
    global want_region_selection
    want_region_selection = True

def clear_region():
    global REGION
    REGION = None
    println("🔄 Región restablecida a pantalla completa.")

def hotkey_listener():
    keyboard.add_hotkey("F10", toggle_pause)
    keyboard.add_hotkey("F9", request_region_selection)
    keyboard.add_hotkey("F8", clear_region)
    keyboard.wait()

# ========= Selector de región =========
def select_region_interactive():
    screenshot = pyautogui.screenshot()
    img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    clone = img.copy()

    selecting = False
    start_pt = None
    end_pt = None
    rect_ready = False

    WIN = "Selecciona región (ENTER=OK, ESC=Cancelar)"
    cv2.namedWindow(WIN, cv2.WINDOW_NORMAL)
    try:
        cv2.setWindowProperty(WIN, cv2.WND_PROP_TOPMOST, 1)
    except Exception:
        pass
    cv2.resizeWindow(WIN, min(1280, img.shape[1]), min(720, img.shape[0]))

    def on_mouse(event, x, y, flags, param):
        nonlocal selecting, start_pt, end_pt, img, rect_ready
        if event == cv2.EVENT_LBUTTONDOWN:
            selecting = True
            start_pt = (x, y)
            end_pt = (x, y)
        elif event == cv2.EVENT_MOUSEMOVE and selecting:
            end_pt = (x, y)
            img = clone.copy()
            cv2.rectangle(img, start_pt, end_pt, (0, 255, 0), 2)
        elif event == cv2.EVENT_LBUTTONUP:
            selecting = False
            end_pt = (x, y)
            img = clone.copy()
            cv2.rectangle(img, start_pt, end_pt, (0, 255, 0), 2)
            rect_ready = True

    cv2.setMouseCallback(WIN, on_mouse)

    while True:
        cv2.imshow(WIN, img)
        k = cv2.waitKey(1) & 0xFF
        if k == 27:  # ESC
            cv2.destroyWindow(WIN)
            return None
        if k == 13 and rect_ready:  # ENTER
            cv2.destroyWindow(WIN)
            (x1, y1) = start_pt
            (x2, y2) = end_pt
            x, y = min(x1, x2), min(y1, y2)
            w, h = abs(x2 - x1), abs(y2 - y1)
            if w < 5 or h < 5:
                println("⚠️ Región demasiado pequeña; cancelado.")
                return None
            return (x, y, w, h)

# ========= Búsqueda =========
def image_is_visible(region=None) -> bool:
    try:
        loc = pyautogui.locateOnScreen(
            IMAGE_PATH,
            confidence=CONFIDENCE,
            grayscale=USE_GRAYSCALE,
            region=region
        )
        return loc is not None
    except pyautogui.ImageNotFoundException:
        return False

# ========= Main =========
def main():
    global image_visible, want_region_selection, REGION, fish_count

    if not os.path.isfile(IMAGE_PATH):
        println(f"❌ No se encontró el archivo: {IMAGE_PATH}")
        return

    println("▶️ Script iniciado. F10=Pause/Reanudar | F9=Seleccionar región | F8=Pantalla completa | CTRL+C=Salir")

    # Muestra un primer estado
    status_line(f"Esperando pique | Pescas: {fish_count} | Región: {'Completa' if REGION is None else REGION}")

    while True:
        # Selección de región bajo demanda
        if want_region_selection:
            was_running = not paused
            if was_running:
                toggle_pause()
            reg = select_region_interactive()
            if reg:
                REGION = reg
                println(f"✅ Región establecida a: {REGION} (x, y, w, h)")
            else:
                println("ℹ️ Selección cancelada, sin cambios.")
            want_region_selection = False
            if was_running:
                toggle_pause()

        # Detección
        if not paused:
            visible_now = image_is_visible(region=REGION)

            if visible_now and not image_visible:
                double_press_altgr()
                fish_count += 1
                image_visible = True
                time.sleep(COOLDOWN_AFTER_DETECT)

            elif not visible_now and image_visible:
                image_visible = False

        # Actualiza la misma línea con el estado actual
        status_line(
            f"{'⏸️' if paused else '▶️'} "
            f"Esperando pique | Pescas: {fish_count} | "
            f"Región: {'Completa' if REGION is None else REGION}"
        )

        time.sleep(SEARCH_INTERVAL)

if __name__ == "__main__":
    threading.Thread(target=hotkey_listener, daemon=True).start()
    try:
        main()
    except KeyboardInterrupt:
        println("\n👋 Programa terminado.")
