import customtkinter as ctk
import requests
from tkinter import messagebox, filedialog, Toplevel
from PIL import Image, ImageTk
import io
import base64

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

        # FORCE logout on window close
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.build_layout()
        self.show_login()

    # ======================
    # Layout
    # ======================
    def build_layout(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.sidebar.grid_rowconfigure(99, weight=1)

        self.title_label = ctk.CTkLabel(
            self.sidebar,
            text="🐍 Snake ID",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        self.title_label.pack(pady=(20, 10))

        self.status_label = ctk.CTkLabel(
            self.sidebar,
            text="Not logged in",
            text_color="gray"
        )
        self.status_label.pack(pady=(0, 20))

        # Main content
        self.content = ctk.CTkFrame(self, corner_radius=0)
        self.content.grid(row=0, column=1, sticky="nsew")

    # ======================
    # Sidebar Buttons
    # ======================
    def clear_sidebar_buttons(self):
        for widget in self.sidebar.winfo_children():
            if isinstance(widget, ctk.CTkButton):
                widget.destroy()

    def add_sidebar_button(self, text, command):
        btn = ctk.CTkButton(
            self.sidebar,
            text=text,
            corner_radius=20,
            height=40,
            command=command
        )
        btn.pack(padx=20, pady=8, fill="x")

    # ======================
    # Screens
    # ======================
    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def show_login(self):
        self.clear_content()
        self.clear_sidebar_buttons()

        frame = ctk.CTkFrame(self.content)
        frame.pack(expand=True)

        ctk.CTkLabel(
            frame,
            text="Login",
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(pady=20)

        self.username_entry = ctk.CTkEntry(
            frame,
            placeholder_text="Username",
            width=250
        )
        self.password_entry = ctk.CTkEntry(
            frame,
            placeholder_text="Password",
            show="⦿",
            width=250
        )

        self.username_entry.pack(pady=10)
        self.password_entry.pack(pady=10)

        ctk.CTkButton(
            frame,
            text="Login",
            corner_radius=20,
            command=self.login
        ).pack(pady=20)

    # ======================
    # View Snakes Grid
    # ======================
    def show_view_snakes(self):
        self.clear_content()

        ctk.CTkLabel(
            self.content,
            text="All Snakes",
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(pady=20)

        canvas = ctk.CTkCanvas(self.content, bg="#1e1e1e", highlightthickness=0)
        scrollbar = ctk.CTkScrollbar(self.content, orientation="vertical", command=canvas.yview)
        scroll_frame = ctk.CTkFrame(canvas, fg_color="#2a2a2a")
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Load snakes
        headers = {"Authorization": self.token}
        r = requests.get(f"{API_BASE}/snakes", headers=headers)
        if r.status_code != 200:
            messagebox.showerror("Error", r.text)
            return

        snakes = r.json()
        self.snake_images = []

        def place_snakes():
            frame_width = 200
            frame_height = 200
            padding = 10
            columns = 4  # lock to 4 snakes per row

            x, y = 0, 0
            count = 0

            for s in snakes:
                frame = ctk.CTkFrame(scroll_frame, width=frame_width, height=frame_height, corner_radius=10, fg_color="#3a3a3a")
                frame.place(x=x, y=y)
                frame.pack_propagate(False)

                # Image
                if s.get("images"):
                    img_b64 = s["images"][0].get("image_base64")
                    if img_b64:
                        img_bytes = base64.b64decode(img_b64)
                        pil_img = Image.open(io.BytesIO(img_bytes)).resize((150, 150))
                        tk_img = ImageTk.PhotoImage(pil_img)
                    else:
                        pil_img = Image.new("RGB", (150,150), color="#555555")
                        tk_img = ImageTk.PhotoImage(pil_img)
                else:
                    pil_img = Image.new("RGB", (150,150), color="#555555")
                    tk_img = ImageTk.PhotoImage(pil_img)

                self.snake_images.append(tk_img)
                lbl_img = ctk.CTkLabel(frame, image=tk_img, text="", fg_color="#3a3a3a")
                lbl_img.pack(pady=5)

                lbl_name = ctk.CTkLabel(frame, text=s["common_name"], fg_color="#3a3a3a")
                lbl_name.pack()

                # Bind click to show detail popup
                frame.bind("<Button-1>", lambda e, snake=s: self.show_snake_detail(snake))
                lbl_img.bind("<Button-1>", lambda e, snake=s: self.show_snake_detail(snake))
                lbl_name.bind("<Button-1>", lambda e, snake=s: self.show_snake_detail(snake))

                count += 1
                if count % columns == 0:
                    x = 0
                    y += frame_height + padding
                else:
                    x += frame_width + padding

            # Update scroll region
            total_rows = (len(snakes) + columns - 1) // columns
            scroll_frame.configure(width=columns * (frame_width + padding), height=total_rows * (frame_height + padding))
            canvas.configure(scrollregion=canvas.bbox("all"))

        # Call after to get actual width
        self.after(50, place_snakes)



    # ======================
    # Snake detail popup
    # ======================
    def show_snake_detail(self, snake):
        popup = ctk.CTkToplevel(self)
        popup.title(snake["common_name"])
        popup.geometry("500x500")
        popup.configure(bg="#121212")

        ctk.CTkLabel(popup, text=snake["common_name"], font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)
        ctk.CTkLabel(popup, text=f"Scientific: {snake['scientific_name']}").pack()
        ctk.CTkLabel(popup, text=f"Venom: {snake['venom_level']}").pack()
        ctk.CTkLabel(popup, text=f"Description: {snake.get('description','')}").pack(pady=5)

        images_frame = ctk.CTkFrame(popup)
        images_frame.pack(pady=10)

        popup.images_refs = []
        for img_obj in snake.get("images", []):
            img_b64 = img_obj.get("image_base64")
            if img_b64:
                img_bytes = base64.b64decode(img_b64)
                pil_img = Image.open(io.BytesIO(img_bytes)).resize((150,150))
                tk_img = ImageTk.PhotoImage(pil_img)
            else:
                pil_img = Image.new("RGB", (150,150), color="#121212")
                tk_img = ImageTk.PhotoImage(pil_img)

            lbl = ctk.CTkLabel(images_frame, image=tk_img, text="")
            lbl.pack(side="left", padx=5)
            popup.images_refs.append(tk_img)

    # ======================
    # Add Snake (Admin) with image upload
    # ======================
    def show_add_snake(self):
        self.clear_content()

        ctk.CTkLabel(
            self.content,
            text="Add Snake (Admin)",
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(pady=20)

        self.entries = {}
        for label in ["Common Name", "Scientific Name", "Venom Level", "Description"]:
            entry = ctk.CTkEntry(self.content, placeholder_text=label, width=400)
            entry.pack(pady=8)
            self.entries[label] = entry

        # Images upload
        self.image_files = []

        def upload_images():
            files = filedialog.askopenfilenames(
                title="Select images",
                filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.gif")]
            )
            self.image_files.extend(files)
            messagebox.showinfo("Images Added", f"{len(files)} images added")

        ctk.CTkButton(
            self.content,
            text="Upload Images",
            corner_radius=20,
            command=upload_images
        ).pack(pady=10)

        ctk.CTkButton(
            self.content,
            text="Create Snake",
            corner_radius=20,
            command=self.create_snake_with_images
        ).pack(pady=20)

    # ======================
    # API Calls
    # ======================
    def create_snake_with_images(self):
        headers = {"Authorization": self.token}
        data = {k.lower().replace(" ", "_"): v.get() for k, v in self.entries.items()}

        # Convert images to base64
        images = []
        for f in getattr(self, "image_files", []):
            with open(f, "rb") as img_file:
                images.append({
                    "image_base64": base64.b64encode(img_file.read()).decode("utf-8")
                })
        data["images"] = images

        r = requests.post(f"{API_BASE}/snakes", json=data, headers=headers)
        if r.status_code == 201:
            messagebox.showinfo("Success", "Snake added")
            self.show_view_snakes()
        else:
            messagebox.showerror("Error", r.text)

    # ======================
    # Auth
    # ======================
    def show_add_user(self):
        self.clear_content()

        ctk.CTkLabel(
            self.content,
            text="Create User (Admin)",
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(pady=20)

        self.new_username = ctk.CTkEntry(self.content, placeholder_text="Username", width=400)
        self.new_password = ctk.CTkEntry(self.content, placeholder_text="Password", show="*", width=400)
        self.new_role = ctk.CTkEntry(self.content, placeholder_text="Role (admin/user)", width=400)

        self.new_username.pack(pady=8)
        self.new_password.pack(pady=8)
        self.new_role.pack(pady=8)

        ctk.CTkButton(
            self.content,
            text="Create User",
            corner_radius=20,
            command=self.create_user
        ).pack(pady=20)

    def login(self):
        data = {
            "username": self.username_entry.get(),
            "password": self.password_entry.get()
        }

        r = requests.post(f"{API_BASE}/auth/login", json=data)
        if r.status_code != 200:
            messagebox.showerror("Login Failed", "Invalid credentials")
            return

        res = r.json()
        self.token = res["token"]
        self.role = res["role"]

        self.status_label.configure(
            text=f"Logged in ({self.role})",
            text_color="lightgreen"
        )

        self.build_authenticated_ui()
        self.show_view_snakes()

    def api_logout(self):
        if not self.token:
            return
        try:
            requests.post(
                f"{API_BASE}/auth/logout",
                headers={"Authorization": self.token},
                timeout=3
            )
        except requests.RequestException:
            pass

    def logout(self):
        self.api_logout()
        self.token = None
        self.role = None
        self.status_label.configure(text="Not logged in", text_color="gray")
        self.show_login()

    def on_close(self):
        self.api_logout()
        self.destroy()

    def build_authenticated_ui(self):
        self.clear_sidebar_buttons()
        self.add_sidebar_button("View Snakes", self.show_view_snakes)
        if self.role == "admin":
            self.add_sidebar_button("Add Snake", self.show_add_snake)
            self.add_sidebar_button("Add User", self.show_add_user)
        self.add_sidebar_button("Logout", self.logout)

    def create_user(self):
        headers = {"Authorization": self.token}
        data = {
            "username": self.new_username.get(),
            "password": self.new_password.get(),
            "role": self.new_role.get()
        }

        r = requests.post(f"{API_BASE}/users", json=data, headers=headers)
        if r.status_code == 201:
            messagebox.showinfo("Success", "User created")
            self.show_view_snakes()
        else:
            messagebox.showerror("Error", r.text)
    def update_snake(self, snake_id, entries):
        headers = {"Authorization": self.token}

        data = {
            "common_name": entries["Common Name"].get(),
            "scientific_name": entries["Scientific Name"].get(),
            "venom_level": entries["Venom Level"].get(),
            "description": entries["Description"].get(),
        }

        r = requests.put(
            f"{API_BASE}/snakes/{snake_id}",
            json=data,
            headers=headers
        )

        if r.status_code == 200:
            messagebox.showinfo("Success", "Snake updated")
            self.show_view_snakes()
        else:
            messagebox.showerror("Error", r.text)



if __name__ == "__main__":
    app = SnakeApp()
    app.mainloop()
