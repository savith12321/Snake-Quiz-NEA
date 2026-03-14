import customtkinter as ctk
from tkinter import messagebox
import requests

API_BASE = "http://127.0.0.1:5000"

class LoginPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ctk.CTkLabel(self, text="Login", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=20)

        self.username_entry = ctk.CTkEntry(self, placeholder_text="Username", width=250)
        self.password_entry = ctk.CTkEntry(self, placeholder_text="Password", show="⦿", width=250)
        self.username_entry.pack(pady=10)
        self.password_entry.pack(pady=10)

        ctk.CTkButton(self, text="Login", command=self.try_login).pack(pady=20)

    def try_login(self):
        data = {
            "username": self.username_entry.get(),
            "password": self.password_entry.get()
        }
        r = requests.post(f"{API_BASE}/auth/login", json=data)
        if r.status_code != 200:
            messagebox.showerror("Login Failed", "Invalid credentials")
            return

        res = r.json()
        self.controller.token = res["token"]
        self.controller.role = res["role"]
        self.controller.user_id = res["user_id"]
        print(self.controller.user_id)
        self.controller.status_label.configure(
            text=f"Logged in ({self.controller.role})",
            text_color="lightgreen"
        )
        self.controller.show_page("home")

    def get_sidebar_buttons(self):
        return [
            ("Login", lambda: self.controller.show_page("login")),
            ("Sign Up", lambda: self.controller.show_page("signup")),
            ("Quit", self.controller.quit)
        ]
