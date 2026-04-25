import random
import statistics
import time
import tkinter as tk


WIDTH = 1000
HEIGHT = 700
PLAYGROUND_PADDING = 20
BACKGROUND = "#0f1220"
PANEL_BG = "#171b2f"
TEXT = "#e6ecff"
MUTED = "#9aa7cf"
SUCCESS = "#58d68d"
WARNING = "#f5b041"
DANGER = "#ff6b6b"
TARGET_COLORS = ["#ff6b6b", "#5cc8ff", "#9b6dff", "#ffc857", "#72f1b8"]


DIFFICULTIES = {
    "Easy": {
        "target_radius": 38,
        "round_time": 45,
        "target_lifetime": 2.2,
        "spawn_gap": 0.75,
        "score_mult": 1.0,
        "max_targets": 1,
    },
    "Medium": {
        "target_radius": 28,
        "round_time": 50,
        "target_lifetime": 1.5,
        "spawn_gap": 0.6,
        "score_mult": 1.5,
        "max_targets": 2,
    },
    "Hard": {
        "target_radius": 20,
        "round_time": 55,
        "target_lifetime": 1.15,
        "spawn_gap": 0.48,
        "score_mult": 2.2,
        "max_targets": 3,
    },
    "Insane": {
        "target_radius": 16,
        "round_time": 60,
        "target_lifetime": 0.85,
        "spawn_gap": 0.38,
        "score_mult": 3.0,
        "max_targets": 4,
    },
}


class AimTrainerGame:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Aim Trainer — Advanced Mode")
        self.root.geometry(f"{WIDTH}x{HEIGHT}")
        self.root.configure(bg=BACKGROUND)
        self.root.resizable(False, False)

        self.difficulty = tk.StringVar(value="Medium")
        self.status_var = tk.StringVar(value="Pick a difficulty and press Start Round")

        self.score = 0
        self.hits = 0
        self.misses = 0
        self.shots = 0
        self.streak = 0
        self.best_streak = 0
        self.round_end_time = 0.0
        self.last_spawn_time = 0.0
        self.reaction_times: list[float] = []
        self.targets: dict[int, dict[str, float]] = {}
        self.spawn_job: str | None = None
        self.tick_job: str | None = None
        self.round_active = False

        self._build_ui()
        self._refresh_metrics()

    def _build_ui(self) -> None:
        self.container = tk.Frame(self.root, bg=BACKGROUND)
        self.container.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(
            self.container,
            width=700,
            height=HEIGHT - 2 * PLAYGROUND_PADDING,
            bg="#0c1020",
            highlightthickness=2,
            highlightbackground="#2a3358",
            cursor="crosshair",
        )
        self.canvas.place(x=PLAYGROUND_PADDING, y=PLAYGROUND_PADDING)

        panel_x = 740
        self.panel = tk.Frame(self.container, bg=PANEL_BG, width=240, height=HEIGHT - 2 * PLAYGROUND_PADDING)
        self.panel.place(x=panel_x, y=PLAYGROUND_PADDING)

        tk.Label(self.panel, text="AIM TRAINER", fg=TEXT, bg=PANEL_BG, font=("Helvetica", 18, "bold")).place(x=20, y=18)
        tk.Label(self.panel, text="Advanced Practice", fg=MUTED, bg=PANEL_BG, font=("Helvetica", 10)).place(x=20, y=48)

        tk.Label(self.panel, text="Difficulty", fg=TEXT, bg=PANEL_BG, font=("Helvetica", 11, "bold")).place(x=20, y=88)
        self.diff_menu = tk.OptionMenu(self.panel, self.difficulty, *DIFFICULTIES.keys())
        self.diff_menu.config(width=13, bg="#212849", fg=TEXT, activebackground="#353f66", activeforeground=TEXT)
        self.diff_menu["menu"].config(bg="#1b2342", fg=TEXT)
        self.diff_menu.place(x=20, y=114)

        self.start_btn = tk.Button(
            self.panel,
            text="Start Round",
            bg="#2e8bff",
            fg="white",
            activebackground="#4a9cff",
            relief="flat",
            command=self.start_round,
            font=("Helvetica", 11, "bold"),
            padx=12,
            pady=6,
        )
        self.start_btn.place(x=20, y=156)

        self.reset_btn = tk.Button(
            self.panel,
            text="Reset Stats",
            bg="#596083",
            fg="white",
            activebackground="#6f79a1",
            relief="flat",
            command=self.reset_stats,
            font=("Helvetica", 10, "bold"),
            padx=12,
            pady=6,
        )
        self.reset_btn.place(x=132, y=156)

        self.labels = {}
        y = 220
        for key in [
            "Score",
            "Time Left",
            "Accuracy",
            "Avg Reaction",
            "Best Reaction",
            "Current Streak",
            "Best Streak",
            "Shots / Hits / Misses",
        ]:
            tk.Label(self.panel, text=key, fg=MUTED, bg=PANEL_BG, font=("Helvetica", 10)).place(x=20, y=y)
            label = tk.Label(self.panel, text="-", fg=TEXT, bg=PANEL_BG, font=("Helvetica", 12, "bold"))
            label.place(x=20, y=y + 18)
            self.labels[key] = label
            y += 52

        self.status = tk.Label(
            self.panel,
            textvariable=self.status_var,
            fg=WARNING,
            bg=PANEL_BG,
            wraplength=210,
            justify="left",
            font=("Helvetica", 10, "bold"),
        )
        self.status.place(x=20, y=642 - 70)

        self.canvas.bind("<Button-1>", self.handle_click)

    def start_round(self) -> None:
        self.clear_targets()
        self.round_active = True
        config = DIFFICULTIES[self.difficulty.get()]

        self.round_end_time = time.perf_counter() + config["round_time"]
        self.last_spawn_time = 0.0
        self.status_var.set(f"Round started: {self.difficulty.get()} mode")

        self._cancel_jobs()
        self._spawn_loop()
        self._tick_loop()

    def reset_stats(self) -> None:
        self._cancel_jobs()
        self.clear_targets()
        self.score = 0
        self.hits = 0
        self.misses = 0
        self.shots = 0
        self.streak = 0
        self.best_streak = 0
        self.reaction_times.clear()
        self.round_active = False
        self.status_var.set("Stats reset. Choose a level and start again.")
        self._refresh_metrics()

    def _spawn_loop(self) -> None:
        if not self.round_active:
            return

        now = time.perf_counter()
        config = DIFFICULTIES[self.difficulty.get()]

        if now >= self.round_end_time:
            self.end_round()
            return

        while len(self.targets) < config["max_targets"] and (now - self.last_spawn_time) >= config["spawn_gap"]:
            self.spawn_target()
            self.last_spawn_time = now

        self._expire_targets()
        self.spawn_job = self.root.after(20, self._spawn_loop)

    def _tick_loop(self) -> None:
        if not self.round_active:
            return
        self._refresh_metrics()
        if time.perf_counter() >= self.round_end_time:
            self.end_round()
            return
        self.tick_job = self.root.after(80, self._tick_loop)

    def spawn_target(self) -> None:
        config = DIFFICULTIES[self.difficulty.get()]
        radius = config["target_radius"]
        x = random.randint(radius + 8, int(self.canvas.winfo_width()) - radius - 8)
        y = random.randint(radius + 8, int(self.canvas.winfo_height()) - radius - 8)
        color = random.choice(TARGET_COLORS)

        outer = self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill=color, outline="#101010", width=2)
        inner = self.canvas.create_oval(x - radius * 0.46, y - radius * 0.46, x + radius * 0.46, y + radius * 0.46, fill="#1a1a1a", outline="")
        bullseye = self.canvas.create_oval(x - radius * 0.2, y - radius * 0.2, x + radius * 0.2, y + radius * 0.2, fill="#f6f6f6", outline="")

        self.targets[outer] = {
            "inner": inner,
            "bullseye": bullseye,
            "spawn_time": time.perf_counter(),
            "radius": radius,
            "lifetime": config["target_lifetime"],
        }

    def _expire_targets(self) -> None:
        now = time.perf_counter()
        expired = [
            item_id
            for item_id, data in self.targets.items()
            if now - data["spawn_time"] >= data["lifetime"]
        ]
        for item_id in expired:
            self._remove_target(item_id)
            self.shots += 1
            self.misses += 1
            self.streak = 0
            self.score = max(0, self.score - 5)
            self.status_var.set("Missed target! Keep tracking faster.")

    def handle_click(self, event: tk.Event) -> None:
        if not self.round_active:
            self.status_var.set("Press Start Round to begin.")
            return

        self.shots += 1
        hit_target = None

        for item_id, data in self.targets.items():
            x1, y1, x2, y2 = self.canvas.coords(item_id)
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2
            r = data["radius"]
            if (event.x - center_x) ** 2 + (event.y - center_y) ** 2 <= r ** 2:
                hit_target = item_id
                break

        if hit_target is None:
            self.misses += 1
            self.streak = 0
            self.score = max(0, self.score - 2)
            self.status_var.set("Miss! Control the crosshair.")
        else:
            data = self.targets[hit_target]
            reaction = time.perf_counter() - data["spawn_time"]
            self.reaction_times.append(reaction)
            self.hits += 1
            self.streak += 1
            self.best_streak = max(self.best_streak, self.streak)

            difficulty_mult = DIFFICULTIES[self.difficulty.get()]["score_mult"]
            speed_bonus = max(0.0, 1.15 - reaction)
            streak_bonus = 1 + min(0.8, self.streak * 0.05)
            gain = int((50 + speed_bonus * 90) * difficulty_mult * streak_bonus)
            self.score += gain

            self._remove_target(hit_target)
            self.status_var.set(f"Hit! +{gain} points ({reaction*1000:.0f} ms)")

        self._refresh_metrics()

    def _remove_target(self, item_id: int) -> None:
        data = self.targets.pop(item_id, None)
        if not data:
            return
        self.canvas.delete(item_id)
        self.canvas.delete(data["inner"])
        self.canvas.delete(data["bullseye"])

    def clear_targets(self) -> None:
        for item_id in list(self.targets):
            self._remove_target(item_id)

    def end_round(self) -> None:
        if not self.round_active:
            return

        self.round_active = False
        self._cancel_jobs()
        self.clear_targets()

        accuracy = (self.hits / self.shots * 100) if self.shots else 0.0
        avg_ms = statistics.mean(self.reaction_times) * 1000 if self.reaction_times else 0.0

        grade = "S" if accuracy > 90 and avg_ms < 420 else "A" if accuracy > 82 else "B" if accuracy > 70 else "C"
        self.status_var.set(
            f"Round over — Grade {grade} | Acc {accuracy:.1f}% | Avg {avg_ms:.0f} ms. Press Start for another run."
        )
        self._refresh_metrics()

    def _cancel_jobs(self) -> None:
        if self.spawn_job:
            self.root.after_cancel(self.spawn_job)
            self.spawn_job = None
        if self.tick_job:
            self.root.after_cancel(self.tick_job)
            self.tick_job = None

    def _refresh_metrics(self) -> None:
        remaining = max(0.0, self.round_end_time - time.perf_counter()) if self.round_active else 0.0
        accuracy = (self.hits / self.shots * 100) if self.shots else 0.0
        avg_reaction = statistics.mean(self.reaction_times) * 1000 if self.reaction_times else 0.0
        best_reaction = min(self.reaction_times) * 1000 if self.reaction_times else 0.0

        self.labels["Score"].config(text=f"{self.score}", fg=SUCCESS if self.score > 0 else TEXT)
        self.labels["Time Left"].config(text=f"{remaining:04.1f}s", fg=WARNING if remaining < 10 and self.round_active else TEXT)
        self.labels["Accuracy"].config(text=f"{accuracy:.1f}%")
        self.labels["Avg Reaction"].config(text=f"{avg_reaction:.0f} ms" if self.reaction_times else "-")
        self.labels["Best Reaction"].config(text=f"{best_reaction:.0f} ms" if self.reaction_times else "-")
        self.labels["Current Streak"].config(text=f"{self.streak}")
        self.labels["Best Streak"].config(text=f"{self.best_streak}")
        self.labels["Shots / Hits / Misses"].config(text=f"{self.shots} / {self.hits} / {self.misses}")


def main() -> None:
    root = tk.Tk()
    AimTrainerGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
