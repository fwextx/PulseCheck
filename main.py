from tkinter import PhotoImage
import time
import customtkinter as ctk
from monitor import Monitor
import matplotlib.pyplot as plt
import datetime
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import datetime
import matplotlib.dates as mdates
import json

with open("config.json", "r") as f:
    config = json.load(f)

cInterval = config.get("monitor_interval", 10)
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class PulseCheckApp(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.title("PulseCheck - Uptime Monitor")
        self.geometry("1200x650")
        self.resizable(True, True)
        self.targets = []
        self.target_labels = []
        self.graph_view = "daily"  # (default value) can be "hourly", "daily", "weekly", "monthly"
        self.history = {}
        self.last_graph_url = None

        self.title_label = ctk.CTkLabel(self, text="PulseCheck", font=("Arial", 24, "bold"))
        self.title_label.pack(pady=(15, 10))

        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.pack(pady=10)

        self.input_entry = ctk.CTkEntry(self.input_frame, width=300, placeholder_text="Enter full URL or IP")
        self.input_entry.pack(side="left", padx=(10, 5), pady=10)

        self.add_button = ctk.CTkButton(self.input_frame, text="Add", command=self.add_target)
        self.add_button.pack(side="left", padx=(5, 10))

        self.view_button_frame = ctk.CTkFrame(self)
        self.view_button_frame.pack(pady=(5, 0))
        self.hourly_button = ctk.CTkButton(
            self.view_button_frame,
            text="Hourly",
            width=80,
            command=lambda: self.set_graph_view("hourly")
        )
        self.hourly_button.pack(side="left", padx=5)

        self.daily_button = ctk.CTkButton(self.view_button_frame, text="Daily", width=80,
                                          command=lambda: self.set_graph_view("daily"))
        self.daily_button.pack(side="left", padx=5)

        self.weekly_button = ctk.CTkButton(self.view_button_frame, text="Weekly", width=80,
                                           command=lambda: self.set_graph_view("weekly"))
        self.weekly_button.pack(side="left", padx=5)

        self.monthly_button = ctk.CTkButton(self.view_button_frame, text="Monthly", width=80,
                                            command=lambda: self.set_graph_view("monthly"))
        self.monthly_button.pack(side="left", padx=5)

        self.target_frame = ctk.CTkScrollableFrame(self, width=550, height=260)
        self.target_frame.pack(pady=10, padx=20, fill="both", expand=True)

        self.graph_frame = ctk.CTkFrame(self, height=200)
        self.graph_frame.pack(fill="x", padx=20, pady=(0, 10))

        self.monitor = Monitor(
            interval=cInterval,
            get_targets_callback=lambda: self.targets,
            update_callback=self.update_statuses
        )

        self.fig = Figure(figsize=(5.5, 2.5), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self.canvas.get_tk_widget().pack_forget()
        self.after(500, self.monitor.start)

    def update_statuses(self, results):
        timestamp = time.time()
        for i, url in enumerate(self.targets):
            status, latency = results.get(url, (False, 0))
            label = self.target_labels[i]

            # Save history
            self.history.setdefault(url, []).append((timestamp, status, latency))

            # GUI update
            if status:
                label.configure(text=f"{url} ✅ Online ({latency:.1f} ms)", text_color="green")
            else:
                label.configure(text=f"{url} ❌ Offline", text_color="red")

        # Refresh graph for currently selected URL
        if hasattr(self, 'last_graph_url'):
            self.show_graph(self.last_graph_url)

    def set_graph_view(self, view):
        self.graph_view = view
        if hasattr(self, 'last_graph_url'):
            self.show_graph(self.last_graph_url)

    def make_graph_command(self, url):
        return lambda: self.show_graph(url)

    def add_target(self):
        url = self.input_entry.get().strip()
        if not url:
            return

        self.targets.append(url)
        self.input_entry.delete(0, "end")

        row_frame = ctk.CTkFrame(self.target_frame)
        row_frame.pack(fill="x", pady=2, padx=5)

        label = ctk.CTkLabel(row_frame, text=f"{url} ⏳ Waiting...", anchor="w")
        label.pack(side="left", fill="x", expand=True, padx=(5, 0))
        self.target_labels.append(label)

        btn = ctk.CTkButton(
            row_frame,
            text="📈",
            width=36,
            height=26,
            fg_color="#1f6aa5",
            hover_color="#155b8c",
            command=self.make_graph_command(url)
        )
        btn.pack(side="right", padx=(0, 5), pady=3)

    def show_graph(self, url):
        self.last_graph_url = url
        if url not in self.history:
            return

        now = time.time()

        if self.graph_view == "hourly":
            cutoff = now - 3600
            window_start = datetime.datetime.fromtimestamp(cutoff)
        elif self.graph_view == "daily":
            cutoff = now - 86400
            window_start = datetime.datetime.fromtimestamp(cutoff)
        elif self.graph_view == "weekly":
            cutoff = now - 86400 * 7
            window_start = datetime.datetime.fromtimestamp(cutoff)
        elif self.graph_view == "monthly":
            cutoff = now - 86400 * 31
            window_start = datetime.datetime.fromtimestamp(cutoff)
        else:
            cutoff = 0
            window_start = None

        timestamps, pings = [], []
        for ts, online, latency in self.history[url]:
            if ts >= cutoff:
                timestamps.append(datetime.datetime.fromtimestamp(ts))
                pings.append(latency if online else None)

        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.ax.clear()
        self.ax.plot(timestamps, pings, color="deepskyblue")

        # Styling
        self.fig.patch.set_facecolor('#2b2b2b')
        self.ax.set_facecolor('#2b2b2b')
        self.ax.tick_params(colors='white')
        for spine in self.ax.spines.values():
            spine.set_color('white')
        self.ax.title.set_color('white')
        self.ax.xaxis.label.set_color('white')
        self.ax.yaxis.label.set_color('white')
        self.ax.grid(True, color='#444444')

        self.ax.set_title(f"{url} - {self.graph_view.title()} View")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Latency (ms)")

        if window_start is not None:
            self.ax.set_xlim(window_start, datetime.datetime.fromtimestamp(now))

        self.canvas.draw()


if __name__ == "__main__":
    app = PulseCheckApp()
    app.mainloop()
