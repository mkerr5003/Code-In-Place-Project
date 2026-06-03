from maze_data import MAZE
import tkinter as tk
from ui import MazeUI
import sys

# enable high-DPI rendering on windows
if sys.platform == "win32":
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

if __name__ == "__main__":
    root = tk.Tk()
    game = MazeUI(root)
    root.mainloop()