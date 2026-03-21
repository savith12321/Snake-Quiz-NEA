import customtkinter as ctk
from tkinter import messagebox
import requests

API_BASE = "http://127.0.0.1:5000"


class QuizHistoryPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ctk.CTkLabel(self, text="Quiz History", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=20)

        # Stats bar
        self.stats_frame = ctk.CTkFrame(self, fg_color="#2a2a2a")
        self.stats_frame.pack(fill="x", padx=20, pady=5)

        self.total_label = ctk.CTkLabel(self.stats_frame, text="Total Quizzes: -")
        self.total_label.pack(side="left", padx=20, pady=10)

        self.avg_label = ctk.CTkLabel(self.stats_frame, text="Average Score: -")
        self.avg_label.pack(side="left", padx=20)

        self.best_label = ctk.CTkLabel(self.stats_frame, text="Best Score: -")
        self.best_label.pack(side="left", padx=20)

        ctk.CTkButton(
            self, text="▶ Start New Quiz",
            fg_color="#2a7a2a", height=40,
            command=lambda: self.controller.show_page("quiz")
        ).pack(pady=10)

        ctk.CTkLabel(self, text="Past Sessions", font=ctk.CTkFont(size=15, weight="bold")).pack(pady=(10, 5))

        self.sessions_frame = ctk.CTkScrollableFrame(self, height=300)
        self.sessions_frame.pack(padx=20, fill="both", expand=True)

        self._load_history()

    def _load_history(self):
        for w in self.sessions_frame.winfo_children():
            w.destroy()

        r = requests.get(
            f"{API_BASE}/quiz/sessions/{self.controller.user_id}",
            headers={"Authorization": self.controller.token}
        )

        if r.status_code != 200:
            ctk.CTkLabel(self.sessions_frame, text="Could not load history").pack()
            return

        quizzes = r.json()

        if not quizzes:
            ctk.CTkLabel(self.sessions_frame, text="No quizzes completed yet.").pack(pady=20)
            return

        # Update stats
        completed = [q for q in quizzes if q["completed_at"]]
        if completed:
            scores = [q["score"] for q in completed]
            avg = sum(scores) / len(scores)
            self.total_label.configure(text=f"Total Quizzes: {len(completed)}")
            self.avg_label.configure(text=f"Average Score: {avg:.1f}/10")
            self.best_label.configure(text=f"Best Score: {max(scores)}/10")

        # List each session
        for q in quizzes:
            row = ctk.CTkFrame(self.sessions_frame, fg_color="#2e2e2e")
            row.pack(fill="x", pady=4, padx=4)

            score_color = "#4caf50" if q["score"] >= 7 else "#f0c040" if q["score"] >= 5 else "#f44336"
            status = "Completed" if q["completed_at"] else "Incomplete"
            date = (q["started_at"] or "")[:16].replace("T", " ")

            ctk.CTkLabel(
                row,
                text=f"{date}   |   {status}",
                anchor="w", width=280
            ).pack(side="left", padx=10, pady=8)

            ctk.CTkLabel(
                row,
                text=f"{q['score']}/{q['total']}",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color=score_color
            ).pack(side="left", padx=10)
            ctk.CTkButton(
                row, text="Delete Quiz Attempt", width=100, height=28, fg_color="#8b0000", hover_color="#b22222",
                command=lambda qid=q["quiz_id"]: self._delete_attempt(qid)
            ).pack(side="right", padx=10, pady=6)
            ctk.CTkButton(
                row, text="View Answers", width=100, height=28,
                command=lambda qid=q["quiz_id"]: self._show_attempts(qid)
            ).pack(side="right", padx=10, pady=6)
    def _delete_attempt(self, quiz_id):
        r = requests.delete(
            f"{API_BASE}/quiz/attempts/{quiz_id}",
            headers={"Authorization": self.controller.token}
        )
        if r.status_code != 200:
            messagebox.showerror("Error", r.text)
            return
        self._load_history() 
            
    def _show_attempts(self, quiz_id):
        r = requests.get(
            f"{API_BASE}/quiz/{quiz_id}/attempts",
            headers={"Authorization": self.controller.token}
        )
        if r.status_code != 200:
            messagebox.showerror("Error", r.text)
            return

        popup = ctk.CTkToplevel(self)
        popup.title("Quiz Answers")
        popup.geometry("600x500")

        ctk.CTkLabel(popup, text="Quiz Breakdown", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

        scroll = ctk.CTkScrollableFrame(popup)
        scroll.pack(fill="both", expand=True, padx=15, pady=10)

        for i, a in enumerate(r.json(), 1):
            row = ctk.CTkFrame(scroll, fg_color="#2e2e2e")
            row.pack(fill="x", pady=3)

            tick = "✓" if a["correct"] else "✗"
            color = "#4caf50" if a["correct"] else "#f44336"

            ctk.CTkLabel(row, text=tick, text_color=color, font=ctk.CTkFont(size=16, weight="bold"), width=30).pack(side="left", padx=8, pady=6)
            ctk.CTkLabel(
                row,
                text=f"Q{i}: {a['snake']} — {a['question_type']}\nYour answer: {a['chosen_answer'] or 'N/A'}",
                anchor="w", justify="left"
            ).pack(side="left", padx=5, pady=6)

    def get_sidebar_buttons(self):
        buttons = [
            ("Home", lambda: self.controller.show_page("home")),
            ("Start Quiz", lambda: self.controller.show_page("quiz")),
        ]
        if self.controller.role == "admin":
            buttons += [("Add Question", lambda: self.controller.show_page("add_question"))]
        buttons += [("Logout", self.controller.logout)]
        return buttons