import customtkinter as ctk
import requests
import io
import base64
from PIL import Image, ImageTk
from pages.login_page import LoginPage
from pages.signup_page import SignupPage
from pages.home_page import HomePage
from pages.add_snake_page import AddSnakePage
from pages.update_delete_snake import UpdateDeleteSnakePage
from pages.quiz_page import QuizPage
from pages.add_question_page import AddQuestionPage
from pages.quiz_history_page import QuizHistoryPage
from pages.leaderboard_page import LeaderboardPage

API_BASE = "http://127.0.0.1:5000"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class SnakeApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Snake Identification System")
        self.geometry("1030x600")
        self.resizable(False, False)

        self.token = None
        self.role = None
        self.user_id = None

        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.sidebar.grid_rowconfigure(99, weight=1)

        self.status_label = ctk.CTkLabel(self.sidebar, text="Not logged in", text_color="gray")
        self.status_label.pack(pady=(0, 20))

        self.content = ctk.CTkFrame(self, corner_radius=0)
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

        self.pages = {}
        for PageClass, name in [
            (LoginPage, "login"),
            (SignupPage, "signup"),
            (HomePage, "home"),
            (AddSnakePage, "add_snake"),
            (UpdateDeleteSnakePage, "update_delete_snake"),
            (QuizPage, "quiz"),
            (AddQuestionPage, "add_question"),
            (QuizHistoryPage, "quiz_history"),
            (LeaderboardPage, "leaderboard"),
        ]:
            page = PageClass(self.content, self)
            self.pages[name] = page
            page.grid(row=0, column=0, sticky="nsew")

        self.show_page("login")

    def show_page(self, name):
        old_page = self.pages[name]
        old_page.destroy()

        PageClass = {
            "login": LoginPage,
            "signup": SignupPage,
            "home": HomePage,
            "add_snake": AddSnakePage,
            "update_delete_snake": UpdateDeleteSnakePage,
            "quiz": QuizPage,
            "add_question": AddQuestionPage,
            "quiz_history": QuizHistoryPage,
            "leaderboard": LeaderboardPage
        }[name]

        page = PageClass(self.content, self)
        self.pages[name] = page
        page.grid(row=0, column=0, sticky="nsew")
        page.tkraise()
        self.draw_sidebar(page.get_sidebar_buttons())

    def draw_sidebar(self, buttons):
        for widget in self.sidebar.winfo_children():
            if isinstance(widget, ctk.CTkButton):
                widget.destroy()
        for text, command in buttons:
            ctk.CTkButton(self.sidebar, text=text, corner_radius=20, height=40, command=command).pack(padx=20, pady=8, fill="x")

    def show_snake_detail(self, snake):
        popup = ctk.CTkToplevel(self)
        popup.title(snake["common_name"])
        popup.geometry("500x520")

        ctk.CTkLabel(popup, text=snake["common_name"], font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)
        ctk.CTkLabel(popup, text=f"Scientific: {snake['scientific_name']}").pack()
        ctk.CTkLabel(popup, text=f"Venom: {snake['venom_level']}").pack()
        ctk.CTkLabel(popup, text=f"Description: {snake.get('description', '')}").pack(pady=5)

        images_frame = ctk.CTkFrame(popup)
        images_frame.pack(pady=10)

        popup.image_refs = []
        for img_obj in snake.get("images", []):
            img_b64 = img_obj.get("image_base64")
            if img_b64:
                img_bytes = base64.b64decode(img_b64)
                pil_img = Image.open(io.BytesIO(img_bytes)).resize((150, 150))
            else:
                pil_img = Image.new("RGB", (150, 150), color="#3a3a3a")
            tk_img = ImageTk.PhotoImage(pil_img)
            ctk.CTkLabel(images_frame, image=tk_img, text="").pack(side="left", padx=5)
            popup.image_refs.append(tk_img)

    def logout(self):
        self.token = None
        self.role = None
        self.user_id = None
        self.status_label.configure(text="Not logged in", text_color="gray")
        self.show_page("login")

    def api_logout(self):
        if self.token:
            try:
                requests.post(f"{API_BASE}/auth/logout", headers={"Authorization": self.token}, timeout=3)
            except:
                pass

    def on_close(self):
        self.api_logout()
        self.destroy()


if __name__ == "__main__":
    app = SnakeApp()
    app.mainloop()