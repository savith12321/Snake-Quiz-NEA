import customtkinter as ctk
from tkinter import messagebox
import requests

API_BASE = "http://127.0.0.1:5000"


class AddQuestionPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.snakes = []

        # Scrollable container for the whole page
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=0, pady=0)

        ctk.CTkLabel(scroll, text="Add Quiz Question", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=20)

        form = ctk.CTkFrame(scroll)
        form.pack(padx=40, pady=10, fill="x")

        # Snake picker
        ctk.CTkLabel(form, text="Snake:").pack(anchor="w", pady=(10, 0))
        self.snake_var = ctk.StringVar(value="Loading...")
        self.snake_menu = ctk.CTkOptionMenu(form, variable=self.snake_var, values=["Loading..."], width=400)
        self.snake_menu.pack(pady=4)

        # Question type
        ctk.CTkLabel(form, text="Question Type:").pack(anchor="w", pady=(10, 0))
        self.type_var = ctk.StringVar(value="identify_by_image")
        ctk.CTkOptionMenu(
            form, variable=self.type_var,
            values=["identify_by_image", "identify_by_description", "venom_level", "scientific_name"],
            width=400
        ).pack(pady=4)

        # Difficulty
        ctk.CTkLabel(form, text="Difficulty (1=easy, 5=hard):").pack(anchor="w", pady=(10, 0))
        self.difficulty_var = ctk.StringVar(value="1")
        ctk.CTkOptionMenu(form, variable=self.difficulty_var, values=["1", "2", "3", "4", "5"], width=400).pack(pady=4)

        # Question text
        ctk.CTkLabel(form, text="Question Text (optional):").pack(anchor="w", pady=(10, 0))
        self.question_text_entry = ctk.CTkEntry(form, placeholder_text="e.g. What snake is this?", width=400)
        self.question_text_entry.pack(pady=4)

        # Correct answer
        ctk.CTkLabel(form, text="Correct Answer:").pack(anchor="w", pady=(10, 0))
        self.answer_entry = ctk.CTkEntry(form, placeholder_text="e.g. Spectacled Cobra", width=400)
        self.answer_entry.pack(pady=4)

        ctk.CTkButton(scroll, text="Add Question", command=self._add_question, fg_color="#2a7a2a").pack(pady=20)

        # Questions list
        ctk.CTkLabel(scroll, text="Existing Questions", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(10, 5))
        self.questions_frame = ctk.CTkScrollableFrame(scroll, height=400)
        self.questions_frame.pack(padx=20, fill="x", pady=(0, 20))

        self._load_snakes()
        self._load_questions()

    def _load_snakes(self):
        r = requests.get(f"{API_BASE}/snakes", headers={"Authorization": self.controller.token})
        if r.status_code == 200:
            self.snakes = r.json()
            names = [s["common_name"] for s in self.snakes]
            self.snake_menu.configure(values=names)
            self.snake_var.set(names[0] if names else "")

    def _load_questions(self):
        for w in self.questions_frame.winfo_children():
            w.destroy()

        r = requests.get(f"{API_BASE}/quiz/questions", headers={"Authorization": self.controller.token})
        if r.status_code != 200:
            return

        for q in r.json():
            row = ctk.CTkFrame(self.questions_frame, fg_color="#2e2e2e")
            row.pack(fill="x", pady=3, padx=4)

            ctk.CTkLabel(
                row,
                text=f"[{q['question_type']}] {q['snake']} — diff:{q['difficulty']} — {q['question_text'] or 'no text'}",
                anchor="w"
            ).pack(side="left", padx=8, pady=4, fill="x", expand=True)

            ctk.CTkButton(
                row, text="Delete", width=70, height=28,
                fg_color="#8b0000", hover_color="#b22222",
                command=lambda qid=q["question_id"]: self._delete_question(qid)
            ).pack(side="right", padx=6, pady=4)

    def _add_question(self):
        selected_name = self.snake_var.get()
        snake = next((s for s in self.snakes if s["common_name"] == selected_name), None)
        if not snake:
            messagebox.showerror("Error", "Please select a snake")
            return

        correct_answer = self.answer_entry.get().strip()
        if not correct_answer:
            messagebox.showerror("Error", "Correct answer cannot be empty")
            return

        data = {
            "snake_id": snake["snake_id"],
            "question_type": self.type_var.get(),
            "question_text": self.question_text_entry.get().strip() or None,
            "correct_answer": correct_answer,
            "difficulty": int(self.difficulty_var.get())
        }

        r = requests.post(
            f"{API_BASE}/quiz/questions",
            json=data,
            headers={"Authorization": self.controller.token}
        )

        if r.status_code == 201:
            messagebox.showinfo("Success", "Question added successfully")
            self.answer_entry.delete(0, "end")
            self.question_text_entry.delete(0, "end")
            self._load_questions()
        else:
            messagebox.showerror("Error", r.text)

    def _delete_question(self, question_id):
        r = requests.delete(
            f"{API_BASE}/quiz/questions/{question_id}",
            headers={"Authorization": self.controller.token}
        )
        if r.status_code == 200:
            self._load_questions()
        else:
            messagebox.showerror("Error", r.text)

    def get_sidebar_buttons(self):
        return [
            ("Home", lambda: self.controller.show_page("home")),
            ("Add Question", lambda: self.controller.show_page("add_question")),
            ("Quiz History", lambda: self.controller.show_page("quiz_history")),
            ("Logout", self.controller.logout),
        ]