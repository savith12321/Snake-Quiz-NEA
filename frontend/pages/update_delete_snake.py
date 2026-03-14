import customtkinter as ctk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import io, base64
import requests

API_BASE = "http://127.0.0.1:5000"


class UpdateDeleteSnakePage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.snake_canvas = None
        self.snake_images = []

        ctk.CTkLabel(self, text="Manage Snakes", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=20)
        self.load_snakes()

    def load_snakes(self):
        if self.snake_canvas:
            self.snake_canvas.destroy()

        container = ctk.CTkFrame(self, fg_color="#1e1e1e")
        container.pack(side="left", fill="both", expand=True)
        self.snake_canvas = container

        canvas = ctk.CTkCanvas(container, bg="#1e1e1e", highlightthickness=0)
        scrollbar = ctk.CTkScrollbar(container, orientation="vertical", command=canvas.yview)
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
            frame_width, frame_height, padding, columns = 200, 220, 10, 4
            x = y = count = 0

            for s in snakes:
                frame = ctk.CTkFrame(
                    scroll_frame, width=frame_width, height=frame_height,
                    corner_radius=10, fg_color="#3a3a3a"
                )
                frame.place(x=x, y=y)
                frame.pack_propagate(False)

                img_data = s.get("images", [{}])[0].get("image_base64")
                if img_data:
                    img_bytes = base64.b64decode(img_data)
                    pil_img = Image.open(io.BytesIO(img_bytes)).resize((130, 130))
                else:
                    pil_img = Image.new("RGB", (130, 130), color="#555555")
                tk_img = ImageTk.PhotoImage(pil_img)
                self.snake_images.append(tk_img)

                lbl_img = ctk.CTkLabel(frame, image=tk_img, text="", fg_color="#3a3a3a")
                lbl_img.pack(pady=(5, 2))

                lbl_name = ctk.CTkLabel(frame, text=s["common_name"], fg_color="#3a3a3a")
                lbl_name.pack()

                ctk.CTkButton(
                    frame, text="Edit", height=24, fg_color="#2a6aad",
                    command=lambda snake=s: self.open_edit_popup(snake)
                ).pack(pady=(4, 0), padx=10, fill="x")

                count += 1
                if count % columns == 0:
                    x = 0
                    y += frame_height + padding
                else:
                    x += frame_width + padding

            scroll_frame.configure(
                width=columns * (frame_width + padding),
                height=((len(snakes) + columns - 1) // columns) * (frame_height + padding)
            )
            canvas.configure(scrollregion=canvas.bbox("all"))

        self.after(50, place_snakes)

    # ======================
    # Edit Popup
    # ======================
    def open_edit_popup(self, snake):
        popup = ctk.CTkToplevel(self)
        popup.title(f"Edit: {snake['common_name']}")
        popup.geometry("560x700")
        popup.grab_set()

        ctk.CTkLabel(popup, text="Edit Snake Details", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(15, 5))

        fields_frame = ctk.CTkFrame(popup)
        fields_frame.pack(padx=20, fill="x")

        common_name = ctk.CTkEntry(fields_frame, placeholder_text="Common Name", width=400)
        common_name.insert(0, snake["common_name"])
        common_name.pack(pady=6)

        scientific_name = ctk.CTkEntry(fields_frame, placeholder_text="Scientific Name", width=400)
        scientific_name.insert(0, snake["scientific_name"])
        scientific_name.pack(pady=6)

        venom_level = ctk.CTkOptionMenu(fields_frame, values=["non-venomous", "mild", "high"])
        venom_level.set(snake["venom_level"])
        venom_level.pack(pady=6)

        description = ctk.CTkEntry(fields_frame, placeholder_text="Description", width=400)
        description.insert(0, snake.get("description") or "")
        description.pack(pady=6)

        def save_details():
            headers = {"Authorization": self.controller.token}
            data = {
                "common_name": common_name.get(),
                "scientific_name": scientific_name.get(),
                "venom_level": venom_level.get(),
                "description": description.get(),
            }
            r = requests.put(f"{API_BASE}/snakes/{snake['snake_id']}", json=data, headers=headers)
            if r.status_code == 200:
                messagebox.showinfo("Saved", "Snake details updated.", parent=popup)
                self.after(100, self.load_snakes)
            else:
                messagebox.showerror("Error", r.text, parent=popup)

        ctk.CTkButton(popup, text="Save Details", fg_color="#2a7a2a", command=save_details).pack(pady=(8, 4))

        def delete_snake():
            if not messagebox.askyesno(
                "Confirm Delete",
                f"Permanently delete '{snake['common_name']}'?\nThis cannot be undone.",
                parent=popup
            ):
                return
            headers = {"Authorization": self.controller.token}
            r = requests.delete(f"{API_BASE}/snakes/{snake['snake_id']}", headers=headers)
            if r.status_code == 200:
                messagebox.showinfo("Deleted", "Snake deleted.", parent=popup)
                popup.destroy()
                self.after(100, self.load_snakes)
            else:
                messagebox.showerror("Error", r.text, parent=popup)

        ctk.CTkButton(
            popup, text="🗑 Delete Snake", fg_color="#8b0000", hover_color="#b22222",
            command=delete_snake
        ).pack(pady=(0, 10))

        ctk.CTkLabel(popup, text="Images", font=ctk.CTkFont(size=15, weight="bold")).pack(pady=(5, 2))

        images_outer = ctk.CTkScrollableFrame(popup, height=200)
        images_outer.pack(padx=20, fill="x")

        popup.img_refs = []

        def refresh_images():
            for w in images_outer.winfo_children():
                w.destroy()
            popup.img_refs.clear()

            headers = {"Authorization": self.controller.token}
            r = requests.get(f"{API_BASE}/snakes/{snake['snake_id']}/images", headers=headers)
            if r.status_code != 200:
                ctk.CTkLabel(images_outer, text="Could not load images").pack()
                return

            images = r.json().get("images", [])

            for img_obj in images:
                row = ctk.CTkFrame(images_outer, fg_color="#2e2e2e")
                row.pack(fill="x", pady=4, padx=4)

                img_b64 = img_obj.get("image_base64")
                if img_b64:
                    img_bytes = base64.b64decode(img_b64)
                    pil_img = Image.open(io.BytesIO(img_bytes)).resize((70, 70))
                else:
                    pil_img = Image.new("RGB", (70, 70), "#555")
                tk_img = ImageTk.PhotoImage(pil_img)
                popup.img_refs.append(tk_img)

                ctk.CTkLabel(row, image=tk_img, text="").pack(side="left", padx=6, pady=4)

                badge_text = "★ Primary" if img_obj.get("is_primary") else ""
                ctk.CTkLabel(row, text=badge_text, text_color="#f0c040", width=80).pack(side="left")

                btn_frame = ctk.CTkFrame(row, fg_color="#2e2e2e")
                btn_frame.pack(side="right", padx=6)

                image_id = img_obj.get("image_id")

                if not img_obj.get("is_primary") and image_id:
                    def make_primary(iid=image_id):
                        headers = {"Authorization": self.controller.token}
                        r = requests.put(
                            f"{API_BASE}/snakes/{snake['snake_id']}/images/{iid}/primary",
                            headers=headers
                        )
                        if r.status_code == 200:
                            refresh_images()
                        else:
                            messagebox.showerror("Error", r.text, parent=popup)

                    ctk.CTkButton(
                        btn_frame, text="Set Primary", width=90, height=28,
                        fg_color="#2a6aad", command=make_primary
                    ).pack(side="left", padx=4)

                if image_id:
                    def delete_image(iid=image_id):
                        headers = {"Authorization": self.controller.token}
                        r = requests.delete(
                            f"{API_BASE}/snakes/{snake['snake_id']}/images/{iid}",
                            headers=headers
                        )
                        if r.status_code == 200:
                            refresh_images()
                        else:
                            messagebox.showerror("Error", r.text, parent=popup)

                    ctk.CTkButton(
                        btn_frame, text="Delete", width=70, height=28,
                        fg_color="#8b0000", hover_color="#b22222",
                        command=delete_image
                    ).pack(side="left", padx=4)

        refresh_images()

        def add_images():
            file_paths = filedialog.askopenfilenames(
                parent=popup,
                filetypes=[("Image Files", "*.png *.jpg *.jpeg *.gif")]
            )
            if not file_paths:
                return

            images = []
            for path in file_paths:
                with open(path, "rb") as f:
                    images.append({"image_base64": base64.b64encode(f.read()).decode("utf-8")})

            headers = {"Authorization": self.controller.token}
            r = requests.post(
                f"{API_BASE}/snakes/{snake['snake_id']}/images",
                json={"images": images},
                headers=headers
            )
            if r.status_code == 201:
                refresh_images()
                self.after(100, self.load_snakes)
            else:
                messagebox.showerror("Error", r.text, parent=popup)

        ctk.CTkButton(popup, text="+ Add Images", command=add_images).pack(pady=10)

    def get_sidebar_buttons(self):
        return [
            ("Home", lambda: self.controller.show_page("home")),
            ("Manage Snakes", lambda: self.controller.show_page("update_delete_snake")),
            ("Logout", self.controller.logout),
        ]