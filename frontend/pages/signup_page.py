import customtkinter as ctk
from tkinter import messagebox
import requests

API_BASE = "http://127.0.0.1:5000"

class SignupPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ctk.CTkLabel(self, text="Sign Up", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=20)

        self.username_entry = ctk.CTkEntry(self, placeholder_text="Username", width=250)
        self.password_entry = ctk.CTkEntry(self, placeholder_text="Password", width=250, show="⦿")
        self.confirm_password = ctk.CTkEntry(self, placeholder_text="Confirm password", width=250, show="⦿")
        self.username_entry.pack(pady=10)
        self.password_entry.pack(pady=10)
        self.confirm_password.pack(pady=10)

        ctk.CTkButton(self, text="Create User", command=self.create_user).pack(pady=20)

    def create_user(self):
        if self.confirm_password.get() == self.password_entry.get():

            data = {
                "username": self.username_entry.get(),
                "password": self.password_entry.get(),
            }
            r = requests.post(f"{API_BASE}/auth/register", json=data)
            if r.status_code == 201:
                messagebox.showinfo("Success", "User created")
                self.controller.show_page("login")
            else:
                messagebox.showerror("Error", r.text)
        else:
            messagebox.showerror("Error", "Password confirmation does not match.")

    def get_sidebar_buttons(self):
        return [
            ("Login", lambda: self.controller.show_page("login")),
            ("Quit", self.controller.quit)
        ]
