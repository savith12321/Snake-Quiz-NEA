import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk
import io, base64
import requests

API_BASE = "http://127.0.0.1:5000"

class HomePage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.snake_canvas = None
        self.snake_images = []

        ctk.CTkLabel(self, text="All Snakes", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=20)
        self.load_snakes()

    def load_snakes(self):
        if self.snake_canvas:
            self.snake_canvas.destroy()

        canvas = ctk.CTkCanvas(self, bg="#1e1e1e", highlightthickness=0)
        scrollbar = ctk.CTkScrollbar(self, orientation="vertical", command=canvas.yview)
        scroll_frame = ctk.CTkFrame(canvas, fg_color="#2a2a2a")
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        headers = {"Authorization": self.controller.token}
        r = requests.get(f"{API_BASE}/snakes", headers=headers)
        if r.status_code != 200:
            messagebox.showerror("Error", r.text)
            return

        snakes = r.json()
        self.snake_images = []

        def place_snakes():
            frame_width, frame_height, padding, columns = 200, 200, 10, 4
            x = y = count = 0
            for s in snakes:
                frame = ctk.CTkFrame(scroll_frame, width=frame_width, height=frame_height, corner_radius=10, fg_color="#3a3a3a")
                frame.place(x=x, y=y)
                frame.pack_propagate(False)

                img_data = s.get("images", [{}])[0].get("image_base64")
                if img_data:
                    img_bytes = base64.b64decode(img_data)
                    pil_img = Image.open(io.BytesIO(img_bytes)).resize((150,150))
                else:
                    pil_img = Image.new("RGB", (150,150), color="#555555")
                tk_img = ImageTk.PhotoImage(pil_img)
                self.snake_images.append(tk_img)

                lbl_img = ctk.CTkLabel(frame, image=tk_img, text="", fg_color="#3a3a3a")
                lbl_img.pack(pady=5)
                lbl_name = ctk.CTkLabel(frame, text=s["common_name"], fg_color="#3a3a3a")
                lbl_name.pack()

                frame.bind("<Button-1>", lambda e, snake=s: self.controller.show_snake_detail(snake))
                lbl_img.bind("<Button-1>", lambda e, snake=s: self.controller.show_snake_detail(snake))
                lbl_name.bind("<Button-1>", lambda e, snake=s: self.controller.show_snake_detail(snake))

                count += 1
                if count % columns == 0:
                    x = 0
                    y += frame_height + padding
                else:
                    x += frame_width + padding

            scroll_frame.configure(width=columns*(frame_width+padding), height=((len(snakes)+columns-1)//columns)*(frame_height+padding))
            canvas.configure(scrollregion=canvas.bbox("all"))

        self.after(50, place_snakes)
        self.snake_canvas = canvas

    def get_sidebar_buttons(self):
        buttons = [("Home", lambda: self.controller.show_page("home"))]
        if self.controller.role == "admin":
            buttons += [
                ("Add Snake", lambda: self.controller.show_page("add_snake")),
                ("Manage Snakes", lambda: self.controller.show_page("update_delete_snake")),
            ]
        buttons += [("Logout", self.controller.logout)]
        return buttons
