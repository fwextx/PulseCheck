from tkinter import PhotoImage

import customtkinter as ctk
from monitor import Monitor

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")



class PulseCheckApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("PulseCheck - Uptime Monitor")
        self.geometry("600x400")
        self.resizable(False, False)


        # Initialize targets **before** using it
        self.targets = []
        self.target_labels = []

        # === Title ===
        self.title_label = ctk.CTkLabel(self, text="PulseCheck", font=("Arial", 24, "bold"))
        self.title_label.pack(pady=(15, 10))

        # === Input Field ===
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.pack(pady=10)

        self.input_entry = ctk.CTkEntry(self.input_frame, width=300, placeholder_text="Enter full URL or IP")
        self.input_entry.pack(side="left", padx=(10, 5), pady=10)

        self.add_button = ctk.CTkButton(self.input_frame, text="Add", command=self.add_target)
        self.add_button.pack(side="left", padx=(5, 10))

        # === Target List Display ===
        self.target_frame = ctk.CTkScrollableFrame(self, width=550, height=260)
        self.target_frame.pack(pady=10, padx=20, fill="both", expand=True)

        # Create the Monitor instance but DO NOT start yet
        self.monitor = Monitor(
            interval=10,
            get_targets_callback=lambda: self.targets,
            update_callback=self.update_statuses
        )

        # Start the monitor AFTER 500ms to ensure GUI is fully initialized
        self.after(500, self.monitor.start)

    def update_statuses(self, results):
        for i, url in enumerate(self.targets):
            status, latency = results.get(url, (False, 0))
            label = self.target_labels[i]

            if status:
                label.configure(text=f"{url} ✅ Online ({latency:.1f} ms)", text_color="green")
            else:
                label.configure(text=f"{url} ❌ Offline", text_color="red")


    def add_target(self):
        url = self.input_entry.get().strip()
        if not url:
            return

        # Optional: prepend http if not present

        self.targets.append(url)
        self.input_entry.delete(0, "end")

        label = ctk.CTkLabel(self.target_frame, text=f"{url} ⏳ Waiting...", anchor="w")
        label.pack(fill="x", pady=2, padx=5)
        self.target_labels.append(label)


if __name__ == "__main__":
    app = PulseCheckApp()
    app.mainloop()
