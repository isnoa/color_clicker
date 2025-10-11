# 영역을 정할떄 거의 꽉 채운 한 줄만 선택하고, 오래 사용할 경우 컴퓨터가 뒤질 수 있음. <<<< @@뒤질 뻔함. 

import pyautogui
from PIL import ImageGrab
import tkinter as tk
from tkinter import messagebox
import time
import threading
import sys
from pynput import mouse

EXCLUDED_COLORS = [(184, 223, 230), (255, 255, 255), (216, 233, 243), (108, 117, 125)]

region = None
clicking = False
mouse_listener = None

def select_region():
    global region

    start_x, start_y, end_x, end_y = 0, 0, 0, 0

    def on_drag_start(event):
        nonlocal start_x, start_y
        start_x, start_y = event.x, event.y
        canvas.delete("selection")

    def on_drag(event):
        nonlocal start_x, start_y
        canvas.delete("selection")
        canvas.create_rectangle(start_x, start_y, event.x, event.y, outline="red", width=2, tags="selection")

    def on_drag_end(event):
        global region
        nonlocal end_x, end_y
        end_x, end_y = event.x, event.y
        region = (start_x, start_y, end_x, end_y)
        messagebox.showinfo("영역 선택 완료", f"선택된 영역: {region}")
        root.destroy()

    root = tk.Tk()
    root.attributes("-fullscreen", True)
    root.attributes("-alpha", 0.3)
    root.title("영역 선택")

    canvas = tk.Canvas(root, bg="gray", highlightthickness=0)
    canvas.pack(fill=tk.BOTH, expand=True)

    canvas.bind("<ButtonPress-1>", on_drag_start)
    canvas.bind("<B1-Motion>", on_drag)
    canvas.bind("<ButtonRelease-1>", on_drag_end)

    root.mainloop()

def fast_click():
    global region, clicking, mouse_listener
    if not region:
        messagebox.showerror("오류", "먼저 영역을 선택하세요.")
        return

    pyautogui.PAUSE = 0.01
    pyautogui.FAILSAFE = True

    clicking = True

    def on_click(x, y, button, pressed):
        global clicking
        if button == mouse.Button.right and pressed:
            clicking = False
            stop_mouse_listener()
            sys.exit()

    mouse_listener = mouse.Listener(on_click=on_click)
    mouse_listener.start()

    def click_loop():
        global clicking
        try:
            while clicking:
                screenshot = ImageGrab.grab(bbox=region)
                pixels = screenshot.load()

                found_target = False
                for y in range(0, screenshot.height, 10):
                    if found_target or not clicking:
                        break
                    for x in range(0, screenshot.width, 10):
                        if not clicking:
                            break
                        color = pixels[x, y]
                        if color not in EXCLUDED_COLORS:
                            pyautogui.click(x + region[0], y + region[1])
                            found_target = True
                            break

                time.sleep(0.035)
        except KeyboardInterrupt:
            clicking = False
        except Exception as e:
            clicking = False

    click_thread = threading.Thread(target=click_loop, daemon=True)
    click_thread.start()

def stop_clicking():
    global clicking, mouse_listener
    clicking = False
    stop_mouse_listener()

def stop_mouse_listener():
    global mouse_listener
    if mouse_listener:
        mouse_listener.stop()
        mouse_listener = None

def create_gui():
    global clicking
    root = tk.Tk()
    root.title("Color Clicker")

    def on_key_press(event):
        global clicking
        if event.keysym == 'Escape':
            clicking = False

    def on_right_click(event):
        root.quit()
        sys.exit()

    def on_close():
        global clicking
        clicking = False
        stop_mouse_listener()
        root.quit()
        sys.exit()

    tk.Label(root, text="Color Clicker", font=("Arial", 16)).pack(pady=10)

    select_button = tk.Button(root, text="영역 선택", command=select_region, font=("Arial", 12))
    select_button.pack(pady=5)

    start_button = tk.Button(root, text="클릭 시작", command=fast_click, font=("Arial", 12))
    start_button.pack(pady=5)

    stop_button = tk.Button(root, text="클릭 중지", command=stop_clicking, font=("Arial", 12))
    stop_button.pack(pady=5)

    quit_button = tk.Button(root, text="프로그램 종료", command=on_close, font=("Arial", 12), bg="red", fg="white")
    quit_button.pack(pady=5)

    tk.Label(root, text="우클릭 또는 빨간 버튼으로 프로그램 종료", font=("Arial", 10)).pack(pady=5)

    root.bind('<KeyPress>', on_key_press)
    root.bind('<Button-3>', on_right_click)
    root.protocol("WM_DELETE_WINDOW", on_close)
    root.focus_set()

    root.mainloop()

if __name__ == "__main__":
    create_gui()