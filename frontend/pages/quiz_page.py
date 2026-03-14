import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk
import io, base64
import requests

API_BASE = "http://127.0.0.1:5000"


class QuizPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.quiz_id = None
        self.current_question = None
        self.question_number = 0
        self.total_questions = 10
        self.current_difficulty = 1
        self.image_refs = []
        self.answered = False

        self._build_ui()
        self._start_quiz()

    def _build_ui(self):
        # Top bar
        top = ctk.CTkFrame(self, fg_color="#2a2a2a")
        top.pack(fill="x", padx=20, pady=(20, 10))

        self.progress_label = ctk.CTkLabel(top, text="Question 0/10", font=ctk.CTkFont(size=14))
        self.progress_label.pack(side="left", padx=10)

        self.difficulty_label = ctk.CTkLabel(top, text="Difficulty: 1", font=ctk.CTkFont(size=14), text_color="#f0c040")
        self.difficulty_label.pack(side="right", padx=10)

        # Image area
        self.image_frame = ctk.CTkFrame(self, fg_color="#1e1e1e", height=180)
        self.image_frame.pack(fill="x", padx=20, pady=5)
        self.image_frame.pack_propagate(False)

        # Question text
        self.question_label = ctk.CTkLabel(
            self, text="", font=ctk.CTkFont(size=16),
            wraplength=700, justify="center"
        )
        self.question_label.pack(pady=15, padx=20)

        # Feedback label
        self.feedback_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=14, weight="bold"))
        self.feedback_label.pack(pady=5)

        # Answer buttons
        self.answer_buttons = []
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=10, padx=40, fill="x")
        btn_frame.grid_columnconfigure((0, 1), weight=1)

        for i in range(4):
            btn = ctk.CTkButton(
                btn_frame, text="", height=50,
                font=ctk.CTkFont(size=13),
                fg_color="#3a3a3a", hover_color="#4a4a4a",
                command=lambda idx=i: self._submit_answer(idx)
            )
            btn.grid(row=i // 2, column=i % 2, padx=10, pady=8, sticky="ew")
            self.answer_buttons.append(btn)

        # Next button
        self.next_btn = ctk.CTkButton(
            self, text="Next Question →", command=self._next_question,
            fg_color="#2a6aad", state="disabled"
        )
        self.next_btn.pack(pady=15)

    def _start_quiz(self):
        headers = {"Authorization": self.controller.token}
        r = requests.post(f"{API_BASE}/quiz/start", json={"user_id": self.controller.user_id}, headers=headers)
        if r.status_code != 201:
            messagebox.showerror("Error", "Could not start quiz")
            self.controller.show_page("home")
            return
        self.quiz_id = r.json()["quiz_id"]
        self._load_question()

    def _load_question(self):
        if self.question_number >= self.total_questions:
            self._finish_quiz()
            return

        self.answered = False
        self.feedback_label.configure(text="")
        self.next_btn.configure(state="disabled")

        for img_widget in self.image_frame.winfo_children():
            img_widget.destroy()
        self.image_refs.clear()

        headers = {"Authorization": self.controller.token}
        r = requests.get(
            f"{API_BASE}/quiz/question",
            params={"difficulty": self.current_difficulty},
            headers=headers
        )

        if r.status_code != 200:
            messagebox.showerror("Error", f"Could not load question: {r.text}")
            return

        self.current_question = r.json()
        self.question_number += 1

        self.progress_label.configure(text=f"Question {self.question_number}/{self.total_questions}")
        self.difficulty_label.configure(text=f"Difficulty: {self.current_difficulty}")

        # Show image if identify_by_image
        if self.current_question.get("images"):
            for img_obj in self.current_question["images"]:
                img_b64 = img_obj.get("image_base64")
                if img_b64:
                    img_bytes = base64.b64decode(img_b64)
                    pil_img = Image.open(io.BytesIO(img_bytes)).resize((160, 160))
                    tk_img = ImageTk.PhotoImage(pil_img)
                    self.image_refs.append(tk_img)
                    ctk.CTkLabel(self.image_frame, image=tk_img, text="").pack(side="left", padx=10, pady=10)

        # Set question text
        qtype = self.current_question["question_type"]
        if qtype == "identify_by_image":
            self.question_label.configure(text="What snake is shown in the image?")
        elif qtype == "identify_by_description":
            desc = self.current_question.get("snake_description", "")
            self.question_label.configure(text=f"Which snake matches this description?\n\n{desc}")
        elif qtype == "venom_level":
            self.question_label.configure(text=f"What is the venom level of the {self.current_question.get('question_text', 'snake')}?")
        elif qtype == "scientific_name":
            self.question_label.configure(text=f"What is the scientific name of the {self.current_question.get('question_text', 'snake')}?")
        else:
            self.question_label.configure(text=self.current_question.get("question_text", ""))

        # Set answer buttons
        choices = self.current_question.get("choices", [])
        for i, btn in enumerate(self.answer_buttons):
            if i < len(choices):
                btn.configure(
                    text=choices[i]["answer_text"],
                    fg_color="#3a3a3a",
                    state="normal"
                )
            else:
                btn.configure(text="", state="disabled")

    def _submit_answer(self, btn_index):
        if self.answered:
            return
        self.answered = True

        choices = self.current_question.get("choices", [])
        selected = choices[btn_index]
        correct_id = self.current_question["correct_answer_id"]

        headers = {"Authorization": self.controller.token}
        r = requests.post(f"{API_BASE}/quiz/answer", json={
            "user_id": self.controller.user_id,
            "question_id": self.current_question["question_id"],
            "answer_id": selected["answer_id"],
            "quiz_id": self.quiz_id
        }, headers=headers)

        if r.status_code != 200:
            messagebox.showerror("Error", r.text)
            return

        result = r.json()
        correct = result["correct"]
        correct_text = result["correct_answer_text"]

        # Colour buttons
        for i, btn in enumerate(self.answer_buttons):
            if i < len(choices):
                if choices[i]["answer_id"] == correct_id:
                    btn.configure(fg_color="#2a7a2a")  # green = correct
                elif i == btn_index and not correct:
                    btn.configure(fg_color="#8b0000")  # red = wrong choice
                btn.configure(state="disabled")

        if correct:
            self.feedback_label.configure(text="✓ Correct!", text_color="#4caf50")
            self.current_difficulty = min(5, self.current_difficulty + 1)
        else:
            self.feedback_label.configure(
                text=f"✗ Wrong! The correct answer was: {correct_text}",
                text_color="#f44336"
            )
            self.current_difficulty = max(1, self.current_difficulty - 1)

        self.next_btn.configure(state="normal")

        # Auto-advance on last question
        if self.question_number >= self.total_questions:
            self.next_btn.configure(text="Finish Quiz →")

    def _next_question(self):
        if self.question_number >= self.total_questions:
            self._finish_quiz()
        else:
            self._load_question()

    def _finish_quiz(self):
        headers = {"Authorization": self.controller.token}
        r = requests.post(f"{API_BASE}/quiz/{self.quiz_id}/finish", headers=headers)

        if r.status_code == 200:
            result = r.json()
            score = result["score"]
            total = result["total"]
            messagebox.showinfo(
                "Quiz Complete!",
                f"You scored {score} out of {total}!\n\n"
                f"{'Excellent!' if score >= 8 else 'Good effort!' if score >= 5 else 'Keep practising!'}"
            )
        else:
            messagebox.showerror("Error", "Could not save quiz result")

        self.controller.show_page("quiz_history")

    def get_sidebar_buttons(self):
        buttons = [("Home", lambda: self.controller.show_page("home"))]
        if self.controller.role == "admin":
            buttons += [("Add Question", lambda: self.controller.show_page("add_question"))]
        buttons += [
            ("Quiz History", lambda: self.controller.show_page("quiz_history")),
            ("Logout", self.controller.logout),
        ]
        return buttons