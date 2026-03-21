import customtkinter as ctk
from tkinter import messagebox
import requests

API_BASE = "http://127.0.0.1:5000"


class LeaderboardPage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        ctk.CTkLabel(self, text="🏆 Leaderboard", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=20)

        # Stats bar
        self.stats_frame = ctk.CTkFrame(self, fg_color="#2a2a2a")
        self.stats_frame.pack(fill="x", padx=20, pady=5)

        self.players_label = ctk.CTkLabel(self.stats_frame, text="Players: -")
        self.players_label.pack(side="left", padx=20, pady=10)

        self.top_label = ctk.CTkLabel(self.stats_frame, text="Top Player: -")
        self.top_label.pack(side="left", padx=20)

        # Header row
        header = ctk.CTkFrame(self, fg_color="#1a1a1a")
        header.pack(fill="x", padx=20, pady=(10, 0))

        ctk.CTkLabel(header, text="Rank",     width=60,  font=ctk.CTkFont(weight="bold"), anchor="center").pack(side="left", padx=10, pady=8)
        ctk.CTkLabel(header, text="Username", width=200, font=ctk.CTkFont(weight="bold"), anchor="w").pack(side="left", padx=10)
        ctk.CTkLabel(header, text="EXP",      width=100, font=ctk.CTkFont(weight="bold"), anchor="center").pack(side="right", padx=20)

        # Scrollable list
        self.list_frame = ctk.CTkScrollableFrame(self, height=380)
        self.list_frame.pack(padx=20, fill="both", expand=True, pady=(0, 10))

        self._load_leaderboard()

    def _load_leaderboard(self):
        for w in self.list_frame.winfo_children():
            w.destroy()

        r = requests.get(
            f"{API_BASE}/leaderboard",
            headers={"Authorization": self.controller.token}
        )

        if r.status_code != 200:
            ctk.CTkLabel(self.list_frame, text="Could not load leaderboard.").pack(pady=20)
            return

        users = r.json()

        if not users:
            ctk.CTkLabel(self.list_frame, text="No players yet.").pack(pady=20)
            return

        # Update stats bar
        self.players_label.configure(text=f"Players: {len(users)}")
        self.top_label.configure(text=f"Top Player: {users[0]['username']} ({users[0]['exp']} EXP)")

        rank_colors = {1: "#FFD700", 2: "#C0C0C0", 3: "#CD7F32"}  # gold, silver, bronze

        for u in users:
            rank = u["rank"]
            is_me = u["username"] == getattr(self.controller, "username", None)

            row_color = "#2e2e2e" if not is_me else "#1a3a1a"
            row = ctk.CTkFrame(self.list_frame, fg_color=row_color, corner_radius=8)
            row.pack(fill="x", pady=3, padx=4)

            # Rank badge
            rank_text = {1: "🥇", 2: "🥈", 3: "🥉"}.get(rank, f"#{rank}")
            rank_color = rank_colors.get(rank, "white")
            ctk.CTkLabel(
                row, text=rank_text, width=60,
                text_color=rank_color,
                font=ctk.CTkFont(size=15, weight="bold"),
                anchor="center"
            ).pack(side="left", padx=10, pady=10)

            # Username
            name_text = f"{u['username']} (you)" if is_me else u["username"]
            ctk.CTkLabel(
                row, text=name_text, width=200, anchor="w"
            ).pack(side="left", padx=10)

            # EXP bar background
            bar_frame = ctk.CTkFrame(row, fg_color="transparent")
            bar_frame.pack(side="left", fill="x", expand=True, padx=10)

            max_exp = users[0]["exp"] if users[0]["exp"] > 0 else 1
            bar_pct = u["exp"] / max_exp
            bar_width = int(200 * bar_pct)

            bar_bg = ctk.CTkFrame(bar_frame, fg_color="#3a3a3a", width=200, height=12, corner_radius=6)
            bar_bg.pack(anchor="w", pady=4)
            bar_bg.pack_propagate(False)

            bar_fill = ctk.CTkFrame(bar_bg, fg_color=rank_color if rank <= 3 else "#2a6aad",
                                    width=max(bar_width, 4), height=12, corner_radius=6)
            bar_fill.place(x=0, y=0)

            # EXP value
            ctk.CTkLabel(
                row, text=f"{u['exp']} XP", width=80,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=rank_color if rank <= 3 else "white",
                anchor="center"
            ).pack(side="right", padx=20, pady=10)

    def get_sidebar_buttons(self):
        buttons = [
            ("Home",        lambda: self.controller.show_page("home")),
            ("Leaderboard", lambda: self.controller.show_page("leaderboard")),
            ("Start Quiz",  lambda: self.controller.show_page("quiz")),
        ]
        if self.controller.role == "admin":
            buttons += [("Add Question", lambda: self.controller.show_page("add_question"))]
        buttons += [("Logout", self.controller.logout)]
        return buttons