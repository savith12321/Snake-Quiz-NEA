import customtkinter as ctk
from tkinter import messagebox, filedialog
import requests
import base64

API_BASE = "http://127.0.0.1:5000"

class AddSnakePage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ctk.CTkLabel(self, text="Add Snake", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=20)

        self.common_name_entry = ctk.CTkEntry(self, placeholder_text="common_name", width=250)
        self.scientific_name_entry = ctk.CTkEntry(self, placeholder_text="Scientific Name", width=250)
        self.venom_level_entry = ctk.CTkOptionMenu(self, values=['non-venomous', 'mild', 'high'])
        self.description_entry = ctk.CTkEntry(self, width=250, placeholder_text="Description")
        self.b64_images = []

        def select_images():

            file_paths = filedialog.askopenfilenames(
                filetypes=[("Image Files", "*.png *.jpg *.jpeg *.gif")]
            )

            for path in file_paths:
                with open(path, "rb") as img_file:
                    encoded = base64.b64encode(img_file.read()).decode("utf-8")
                    self.b64_images.append({"image_base64": encoded})

            print(f"{len(self.b64_images)} images converted.")
        self.common_name_entry.pack(pady=10)
        self.scientific_name_entry.pack(pady=10)
        self.venom_level_entry.pack(pady=10)
        self.description_entry.pack(pady=10)
        ctk.CTkButton(self, text="Select Images", command=select_images).pack(pady=20)
        ctk.CTkButton(self, text="Add snake", command=self.add_snake).pack(pady=20)

    def add_snake(self):
        headers = {"Authorization": self.controller.token}
        data = {
            "common_name": self.common_name_entry.get(),
            "scientific_name": self.scientific_name_entry.get(),
            "venom_level": self.venom_level_entry.get(),
            "description": self.description_entry.get(),
            "images": self.b64_images
        }
        r = requests.post(f"{API_BASE}/snakes", json=data, headers=headers)
        if r.status_code != 201:
            messagebox.showerror("Adding snake failed", r.text)
            return
        messagebox.showinfo("Snake added", "The snake was added successfully")
        self.b64_images = []

    def get_sidebar_buttons(self):
        return [
            ("Home", lambda: self.controller.show_page("home")),
            ("logout", self.controller.logout)
        ]
