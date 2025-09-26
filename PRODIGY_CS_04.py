# safe_logger_pretty.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from datetime import datetime
import os
import csv

DEFAULT_LOG_FILE = "keystrokes_log.txt"

# --- Utility: small hover helper to change widget style on enter/leave ---
def add_hover(widget, enter_bg=None, leave_bg=None, enter_fg=None, leave_fg=None):
    def on_enter(e):
        if enter_bg is not None:
            try: widget.config(background=enter_bg)
            except: pass
        if enter_fg is not None:
            try: widget.config(foreground=enter_fg)
            except: pass
    def on_leave(e):
        if leave_bg is not None:
            try: widget.config(background=leave_bg)
            except: pass
        if leave_fg is not None:
            try: widget.config(foreground=leave_fg)
            except: pass
    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)

class PrettySafeLogger:
    def __init__(self, root):
        self.root = root
        root.title("✨ Safe Logger — Colorful & Secure (App-only)")
        root.geometry("900x620")
        root.minsize(820, 560)

        # overall style / palette
        self.palette = {
            "bg": "#001f29",         # deep ocean blue
    "panel": "#003543",      # darker teal
    "accent": "#00e0c6",     # aqua mint
    "accent2": "#0099ff",    # bright blue
    "muted": "#94a3b8",      # soft gray-blue
    "card": "#002b36",       # dark cyan card
    "danger": "#ff6b6b",     # coral red
    "button_bg": "#004f5d",  # teal button
    "button_hover": "#006d77" # lighter teal hover
        }

        root.configure(bg=self.palette["bg"])

        # top header
        header = tk.Frame(root, bg=self.palette["panel"], padx=14, pady=14)
        header.pack(fill="x", padx=12, pady=(12,6))

        title = tk.Label(header, text="✨ Safe Keystroke Logger", bg=self.palette["panel"],
                         fg="white", font=("Segoe UI Semibold", 18))
        title.pack(side="left")

        subtitle = tk.Label(header, text="(Logs only while this window has focus — safe & visible)",
                            bg=self.palette["panel"], fg=self.palette["muted"], font=("Segoe UI", 10))
        subtitle.pack(side="left", padx=(12,0))

        # top-right quick buttons
        top_right = tk.Frame(header, bg=self.palette["panel"])
        top_right.pack(side="right")

        self.btn_choose = tk.Button(top_right, text="📁 Choose Log File", command=self.choose_log_file,
                                    bg=self.palette["button_bg"], fg="white", bd=0, padx=10, pady=6)
        self.btn_choose.pack(side="left", padx=6)
        add_hover(self.btn_choose, enter_bg=self.palette["button_hover"], leave_bg=self.palette["button_bg"])

        self.btn_export = tk.Button(top_right, text="⬇️ Export CSV", command=self.export_csv,
                                    bg=self.palette["button_bg"], fg="white", bd=0, padx=10, pady=6)
        self.btn_export.pack(side="left", padx=6)
        add_hover(self.btn_export, enter_bg=self.palette["button_hover"], leave_bg=self.palette["button_bg"])

        # main content area (left = logger controls, right = preview)
        content = tk.Frame(root, bg=self.palette["bg"])
        content.pack(fill="both", expand=True, padx=12, pady=(6,12))

        # left card (controls + typing area)
        left_card = tk.Frame(content, bg=self.palette["card"], bd=0, padx=12, pady=12)
        left_card.place(relx=0.02, rely=0.02, relwidth=0.61, relheight=0.92)

        # Log path display
        self.log_file = DEFAULT_LOG_FILE
        lbl_path = tk.Label(left_card, text="Log File:", bg=self.palette["card"], fg=self.palette["muted"], anchor="w")
        lbl_path.pack(fill="x")
        self.lbl_logpath = tk.Label(left_card, text=self.log_file, bg=self.palette["card"], fg="white", anchor="w", font=("Segoe UI", 10, "bold"))
        self.lbl_logpath.pack(fill="x", pady=(0,8))

        # Controls row
        ctl_row = tk.Frame(left_card, bg=self.palette["card"])
        ctl_row.pack(fill="x", pady=(4,10))

        self.btn_start = tk.Button(ctl_row, text="▶ Start Logging", command=self.start_logging,
                                   bg=self.palette["accent"], fg="#04201B", bd=0, padx=12, pady=8, font=("Segoe UI", 10, "bold"))
        self.btn_start.grid(row=0, column=0, padx=(0,8))
        add_hover(self.btn_start, enter_bg="#4fe0a6", leave_bg=self.palette["accent"])

        self.btn_stop = tk.Button(ctl_row, text="⏸ Stop", command=self.stop_logging, state="disabled",
                                  bg=self.palette["button_bg"], fg="white", bd=0, padx=12, pady=8)
        self.btn_stop.grid(row=0, column=1, padx=(0,8))
        add_hover(self.btn_stop, enter_bg=self.palette["button_hover"], leave_bg=self.palette["button_bg"])

        self.btn_clear = tk.Button(ctl_row, text="🧹 Clear Log", command=self.clear_log_file,
                                   bg=self.palette["button_bg"], fg="white", bd=0, padx=12, pady=8)
        self.btn_clear.grid(row=0, column=2, padx=(0,8))
        add_hover(self.btn_clear, enter_bg=self.palette["button_hover"], leave_bg=self.palette["button_bg"])

        # Status bar
        self.status_var = tk.StringVar(value="Status: Idle")
        status_label = tk.Label(left_card, textvariable=self.status_var, bg=self.palette["card"], fg=self.palette["muted"])
        status_label.pack(anchor="w", pady=(6,8))

        # Typing area (where keys are captured)
        tk.Label(left_card, text="Type here (logging only when started):", bg=self.palette["card"], fg="white").pack(anchor="w")
        self.textbox = scrolledtext.ScrolledText(left_card, width=60, height=12, wrap="word",
                                                 bg="#061426", fg="white", insertbackground="white", relief="flat")
        self.textbox.pack(fill="both", expand=False, pady=(6,8))
        self.textbox.focus_set()
        self.textbox.bind("<Key>", self.on_keypress)

        # small hint
        hint = tk.Label(left_card, text="Tip: Keep this window focused while typing. Logs are saved locally and visible here.",
                        bg=self.palette["card"], fg=self.palette["muted"], wraplength=440, justify="left")
        hint.pack(anchor="w", pady=(6,0))

        # right card (log preview + recent entries)
        right_card = tk.Frame(content, bg=self.palette["card"], bd=0, padx=12, pady=12)
        right_card.place(relx=0.66, rely=0.02, relwidth=0.32, relheight=0.92)

        tk.Label(right_card, text="Recent Log Preview", bg=self.palette["card"], fg="white").pack(anchor="w")
        self.log_display = scrolledtext.ScrolledText(right_card, width=36, height=28, wrap="word",
                                                     bg="#061426", fg="white", state="disabled", relief="flat")
        self.log_display.pack(fill="both", expand=True, pady=(8,4))

        # color legend card
        legend = tk.Frame(right_card, bg=self.palette["card"])
        legend.pack(fill="x", pady=(6,0))
        tk.Label(legend, text="Legend:", bg=self.palette["card"], fg=self.palette["muted"]).grid(row=0, column=0, sticky="w")
        tk.Label(legend, text="Printable chars", bg=self.palette["card"], fg=self.palette["accent"]).grid(row=1, column=0, sticky="w", padx=(8,0))
        tk.Label(legend, text="Special keys", bg=self.palette["card"], fg=self.palette["accent2"]).grid(row=2, column=0, sticky="w", padx=(8,0))

        # bottom footer with small credits
        footer = tk.Frame(root, bg=self.palette["panel"], padx=12, pady=8)
        footer.pack(fill="x", padx=12, pady=(0,12))
        tk.Label(footer, text="Safe Logger • Logs keys only inside this app • Use responsibly", bg=self.palette["panel"],
                 fg=self.palette["muted"]).pack(side="left")

        # initialize state
        self.logging = False
        self.refresh_log_display()

    # ----------------- Actions -----------------
    def choose_log_file(self):
        path = filedialog.asksaveasfilename(defaultextension=".txt",
                                            filetypes=[("Text file", "*.txt"), ("All files", "*.*")])
        if path:
            self.log_file = path
            self.lbl_logpath.config(text=self.log_file)
            self.refresh_log_display()

    def start_logging(self):
        self.logging = True
        self.status_var.set("Status: Logging — window must be active to capture keys")
        self.btn_start.config(state="disabled", bg="#3EE6A9")
        self.btn_stop.config(state="normal")
        self.btn_stop.config(bg=self.palette["button_bg"])

    def stop_logging(self):
        self.logging = False
        self.status_var.set("Status: Idle")
        self.btn_start.config(state="normal", bg=self.palette["accent"])
        self.btn_stop.config(state="disabled", bg=self.palette["button_bg"])

    def clear_log_file(self):
        if os.path.exists(self.log_file):
            try:
                os.remove(self.log_file)
            except Exception as e:
                messagebox.showerror("Error", f"Could not clear log file:\n{e}")
                return
        self.refresh_log_display()
        messagebox.showinfo("Cleared", "Log file cleared.")

    def export_csv(self):
        if not os.path.exists(self.log_file):
            messagebox.showwarning("No Log", "No log file to export.")
            return
        csv_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                                filetypes=[("CSV file", "*.csv"), ("All files", "*.*")])
        if not csv_path:
            return
        try:
            with open(self.log_file, "r", encoding="utf-8") as txt, open(csv_path, "w", newline="", encoding="utf-8") as csvf:
                writer = csv.writer(csvf)
                writer.writerow(["timestamp", "key"])
                for line in txt:
                    line = line.strip()
                    if not line:
                        continue
                    if " - " in line:
                        ts, rest = line.split(" - ", 1)
                        writer.writerow([ts, rest])
                    else:
                        writer.writerow(["", line])
            messagebox.showinfo("Exported", f"Log exported to {csv_path}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Could not export CSV:\n{e}")

    def on_keypress(self, event):
        """capture keys typed into the app's textbox only"""
        if not self.logging:
            return

        char = event.char
        keysym = event.keysym
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if char and char.isprintable():
            to_write = f"{timestamp} - '{char}'\n"
        else:
            to_write = f"{timestamp} - [{keysym}]\n"

        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(to_write)
        except Exception as e:
            messagebox.showerror("File Error", f"Could not write to log file:\n{e}")
            self.stop_logging()
            return

        self.append_to_log_display(to_write)

    def refresh_log_display(self):
        self.log_display.config(state="normal")
        self.log_display.delete(1.0, tk.END)
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, "r", encoding="utf-8") as f:
                    contents = f.read()
            except Exception as e:
                contents = f"[Error reading log file: {e}]"
        else:
            contents = "[Log file is empty]"
        self.log_display.insert(tk.END, contents)
        self.log_display.config(state="disabled")

    def append_to_log_display(self, text):
        self.log_display.config(state="normal")
        self.log_display.insert(tk.END, text)
        self.log_display.see(tk.END)
        self.log_display.config(state="disabled")


if __name__ == "__main__":
    root = tk.Tk()
    app = PrettySafeLogger(root)
    root.mainloop()
