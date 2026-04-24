import math
import random
import tkinter as tk
from dataclasses import dataclass


WIDTH = 1100
HEIGHT = 760
WORLD_SIZE = 680
PANEL_X = WORLD_SIZE + 20
BACKGROUND = "#10131a"
WORLD_BG = "#0f1724"
GRID_COLOR = "#1d2a3f"
TEXT_PRIMARY = "#d5e0ff"
TEXT_MUTED = "#8ea3d1"
SUSCEPTIBLE_COLOR = "#78b7ff"
INFECTED_COLOR = "#ff6e7f"
RECOVERED_COLOR = "#7cf38f"

INITIAL_POPULATION = 160
INITIAL_INFECTED = 3
AGENT_RADIUS = 4
BASE_SPEED = 1.7


@dataclass
class Agent:
    x: float
    y: float
    vx: float
    vy: float
    state: str = "S"


class VirusSpreadSimulator:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Virus Spread Simulator")
        self.root.geometry(f"{WIDTH}x{HEIGHT}")
        self.root.configure(bg=BACKGROUND)
        self.root.resizable(False, False)

        self.running = True
        self.tick = 0
        self.agents: list[Agent] = []

        self.infection_rate = tk.DoubleVar(value=0.32)
        self.recovery_rate = tk.DoubleVar(value=0.012)

        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg=BACKGROUND, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self._build_world()
        self._spawn_population()
        self.bind_controls()

        self.update_loop()

    def _build_world(self) -> None:
        self.world_left = 20
        self.world_top = 20
        self.world_right = self.world_left + WORLD_SIZE
        self.world_bottom = self.world_top + WORLD_SIZE

    def _spawn_population(self) -> None:
        self.tick = 0
        self.agents.clear()
        for _ in range(INITIAL_POPULATION):
            angle = random.uniform(0, math.tau)
            speed = BASE_SPEED + random.uniform(-0.45, 0.55)
            self.agents.append(
                Agent(
                    x=random.uniform(self.world_left + AGENT_RADIUS, self.world_right - AGENT_RADIUS),
                    y=random.uniform(self.world_top + AGENT_RADIUS, self.world_bottom - AGENT_RADIUS),
                    vx=math.cos(angle) * speed,
                    vy=math.sin(angle) * speed,
                )
            )

        for agent in random.sample(self.agents, k=min(INITIAL_INFECTED, len(self.agents))):
            agent.state = "I"

    def bind_controls(self) -> None:
        self.root.bind("<space>", lambda _e: self.toggle_running())
        self.root.bind("r", lambda _e: self.reset())
        self.root.bind("R", lambda _e: self.reset())

    def toggle_running(self) -> None:
        self.running = not self.running

    def reset(self) -> None:
        self._spawn_population()

    def _bounce(self, agent: Agent) -> None:
        if agent.x < self.world_left + AGENT_RADIUS or agent.x > self.world_right - AGENT_RADIUS:
            agent.vx *= -1
            agent.x = min(self.world_right - AGENT_RADIUS, max(self.world_left + AGENT_RADIUS, agent.x))

        if agent.y < self.world_top + AGENT_RADIUS or agent.y > self.world_bottom - AGENT_RADIUS:
            agent.vy *= -1
            agent.y = min(self.world_bottom - AGENT_RADIUS, max(self.world_top + AGENT_RADIUS, agent.y))

    def _spread_infections(self) -> None:
        infection_radius = AGENT_RADIUS * 2.8
        chance = self.infection_rate.get()
        infected = [a for a in self.agents if a.state == "I"]
        susceptible = [a for a in self.agents if a.state == "S"]

        for s in susceptible:
            for i in infected:
                if math.hypot(s.x - i.x, s.y - i.y) <= infection_radius and random.random() < chance:
                    s.state = "I"
                    break

    def _recover_agents(self) -> None:
        recover_chance = self.recovery_rate.get()
        for agent in self.agents:
            if agent.state == "I" and random.random() < recover_chance:
                agent.state = "R"

    def simulate_tick(self) -> None:
        self.tick += 1
        for agent in self.agents:
            jitter = random.uniform(-0.25, 0.25)
            angle = math.atan2(agent.vy, agent.vx) + jitter
            speed = math.hypot(agent.vx, agent.vy)
            speed = min(2.5, max(0.9, speed + random.uniform(-0.08, 0.08)))
            agent.vx = math.cos(angle) * speed
            agent.vy = math.sin(angle) * speed

            agent.x += agent.vx
            agent.y += agent.vy
            self._bounce(agent)

        self._spread_infections()
        self._recover_agents()

    def draw_static_ui(self) -> None:
        self.canvas.delete("ui")
        self.canvas.create_rectangle(
            self.world_left,
            self.world_top,
            self.world_right,
            self.world_bottom,
            fill=WORLD_BG,
            outline="#2c3b58",
            width=2,
            tags="ui",
        )

        gap = 40
        for i in range(1, WORLD_SIZE // gap):
            x = self.world_left + i * gap
            y = self.world_top + i * gap
            self.canvas.create_line(x, self.world_top, x, self.world_bottom, fill=GRID_COLOR, tags="ui")
            self.canvas.create_line(self.world_left, y, self.world_right, y, fill=GRID_COLOR, tags="ui")

        self.canvas.create_text(
            PANEL_X,
            35,
            text="Virus Spread Simulator",
            fill=TEXT_PRIMARY,
            font=("Segoe UI", 24, "bold"),
            anchor="w",
            tags="ui",
        )
        self.canvas.create_text(
            PANEL_X,
            64,
            text="Simulate infection spreading and recovery",
            fill=TEXT_MUTED,
            font=("Segoe UI", 11),
            anchor="w",
            tags="ui",
        )

        self.canvas.create_rectangle(PANEL_X - 2, 90, WIDTH - 24, HEIGHT - 24, outline="#2b3a58", width=2, tags="ui")

    def draw_dynamic(self) -> None:
        self.canvas.delete("dynamic")

        for agent in self.agents:
            color = (
                SUSCEPTIBLE_COLOR if agent.state == "S" else INFECTED_COLOR if agent.state == "I" else RECOVERED_COLOR
            )
            self.canvas.create_oval(
                agent.x - AGENT_RADIUS,
                agent.y - AGENT_RADIUS,
                agent.x + AGENT_RADIUS,
                agent.y + AGENT_RADIUS,
                fill=color,
                outline="#0e141f",
                width=1,
                tags="dynamic",
            )

        susceptible_count = sum(1 for a in self.agents if a.state == "S")
        infected_count = sum(1 for a in self.agents if a.state == "I")
        recovered_count = sum(1 for a in self.agents if a.state == "R")

        status = "RUNNING" if self.running else "PAUSED"
        status_color = "#7cf38f" if self.running else "#ffd87b"

        lines = [
            ("Status", status, status_color),
            ("Ticks", f"{self.tick}", TEXT_PRIMARY),
            ("Population", f"{len(self.agents)}", TEXT_PRIMARY),
            ("", "", TEXT_PRIMARY),
            ("Susceptible", f"{susceptible_count}", SUSCEPTIBLE_COLOR),
            ("Infected", f"{infected_count}", INFECTED_COLOR),
            ("Recovered", f"{recovered_count}", RECOVERED_COLOR),
            ("", "", TEXT_PRIMARY),
            ("Infection rate", f"{self.infection_rate.get():.2f}", TEXT_PRIMARY),
            ("Recovery rate", f"{self.recovery_rate.get():.3f}", TEXT_PRIMARY),
        ]

        y = 120
        for label, value, color in lines:
            if not label:
                y += 12
                continue
            self.canvas.create_text(PANEL_X, y, text=label, fill=TEXT_MUTED, font=("Segoe UI", 11), anchor="w", tags="dynamic")
            self.canvas.create_text(WIDTH - 34, y, text=value, fill=color, font=("Consolas", 12, "bold"), anchor="e", tags="dynamic")
            y += 30

        self.canvas.create_text(
            PANEL_X,
            HEIGHT - 110,
            text="Adjust rates with sliders below\nSPACE = pause/resume\nR = reset world",
            fill=TEXT_MUTED,
            font=("Segoe UI", 10),
            anchor="sw",
            tags="dynamic",
            justify="left",
        )

    def draw_controls(self) -> None:
        self.canvas.delete("controls")
        self.canvas.create_text(PANEL_X, HEIGHT - 180, text="Infection rate", fill=TEXT_MUTED, font=("Segoe UI", 10), anchor="w", tags="controls")
        self.canvas.create_text(PANEL_X, HEIGHT - 145, text="Recovery rate", fill=TEXT_MUTED, font=("Segoe UI", 10), anchor="w", tags="controls")

    def build_sliders(self) -> None:
        self.infection_slider = tk.Scale(
            self.root,
            from_=0.0,
            to=1.0,
            orient="horizontal",
            resolution=0.01,
            variable=self.infection_rate,
            bg=BACKGROUND,
            fg=TEXT_PRIMARY,
            troughcolor="#22314d",
            highlightthickness=0,
            length=260,
        )
        self.infection_slider.place(x=PANEL_X, y=HEIGHT - 175)

        self.recovery_slider = tk.Scale(
            self.root,
            from_=0.0,
            to=0.1,
            orient="horizontal",
            resolution=0.001,
            variable=self.recovery_rate,
            bg=BACKGROUND,
            fg=TEXT_PRIMARY,
            troughcolor="#22314d",
            highlightthickness=0,
            length=260,
        )
        self.recovery_slider.place(x=PANEL_X, y=HEIGHT - 140)

    def update_loop(self) -> None:
        if not hasattr(self, "infection_slider"):
            self.build_sliders()

        if self.running:
            self.simulate_tick()

        self.draw_static_ui()
        self.draw_dynamic()
        self.draw_controls()
        self.root.after(30, self.update_loop)


def main() -> None:
    root = tk.Tk()
    VirusSpreadSimulator(root)
    root.mainloop()


if __name__ == "__main__":
    main()
