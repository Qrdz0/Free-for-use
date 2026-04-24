import math
import random
import tkinter as tk
from dataclasses import dataclass, field


WIDTH = 1100
HEIGHT = 760
WORLD_SIZE = 680
PANEL_X = WORLD_SIZE + 20
BACKGROUND = "#10131a"
WORLD_BG = "#0f1724"
GRID_COLOR = "#1d2a3f"
TEXT_PRIMARY = "#d5e0ff"
TEXT_MUTED = "#8ea3d1"
FOOD_COLOR = "#5fe06e"

INITIAL_CREATURES = 26
INITIAL_FOOD = 90
MAX_CREATURES = 180
MAX_FOOD = 240


@dataclass
class Genome:
    speed: float
    perception: float
    fertility: float
    greed: float
    metabolism: float
    wander: float

    @staticmethod
    def random_genome() -> "Genome":
        return Genome(
            speed=random.uniform(1.0, 2.8),
            perception=random.uniform(35, 120),
            fertility=random.uniform(80, 150),
            greed=random.uniform(0.7, 1.4),
            metabolism=random.uniform(0.6, 1.4),
            wander=random.uniform(0.2, 1.3),
        )

    def mutated(self, rate: float = 0.18) -> "Genome":
        def mutate(value: float, lo: float, hi: float, scale: float = 1.0) -> float:
            value += random.gauss(0, rate * scale)
            return min(hi, max(lo, value))

        return Genome(
            speed=mutate(self.speed, 0.7, 3.5),
            perception=mutate(self.perception, 20, 160, scale=10),
            fertility=mutate(self.fertility, 55, 180, scale=12),
            greed=mutate(self.greed, 0.4, 2.0, scale=0.4),
            metabolism=mutate(self.metabolism, 0.5, 2.3, scale=0.3),
            wander=mutate(self.wander, 0.1, 1.8, scale=0.25),
        )


@dataclass
class Food:
    x: float
    y: float
    energy: float = 28.0


@dataclass
class Creature:
    x: float
    y: float
    genome: Genome
    energy: float = 105.0
    age: int = 0
    direction: float = field(default_factory=lambda: random.uniform(0, math.tau))
    color: str = ""

    def __post_init__(self) -> None:
        if not self.color:
            self.color = self.genome_to_color()

    def genome_to_color(self) -> str:
        r = int(80 + 120 * min(1.0, self.genome.speed / 3.5))
        g = int(80 + 110 * min(1.0, self.genome.perception / 160))
        b = int(90 + 95 * min(1.0, self.genome.fertility / 180))
        return f"#{r:02x}{g:02x}{b:02x}"

    def radius(self) -> float:
        return 4 + self.genome.speed * 1.2


class EvolutionSimulator:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Evolution Simulator")
        self.root.geometry(f"{WIDTH}x{HEIGHT}")
        self.root.configure(bg=BACKGROUND)
        self.root.resizable(False, False)

        self.running = True
        self.tick = 0
        self.generation = 1

        self.creatures: list[Creature] = []
        self.food: list[Food] = []

        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg=BACKGROUND, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self._build_world()
        self._spawn_initial()
        self.draw_static_ui()
        self.bind_controls()

        self.update_loop()

    def _build_world(self) -> None:
        self.world_left = 20
        self.world_top = 20
        self.world_right = self.world_left + WORLD_SIZE
        self.world_bottom = self.world_top + WORLD_SIZE

    def _spawn_initial(self) -> None:
        for _ in range(INITIAL_CREATURES):
            self.creatures.append(
                Creature(
                    x=random.uniform(self.world_left + 6, self.world_right - 6),
                    y=random.uniform(self.world_top + 6, self.world_bottom - 6),
                    genome=Genome.random_genome(),
                )
            )
        for _ in range(INITIAL_FOOD):
            self.spawn_food()

    def bind_controls(self) -> None:
        self.root.bind("<space>", lambda _e: self.toggle_running())
        self.root.bind("r", lambda _e: self.reset())
        self.root.bind("R", lambda _e: self.reset())

    def toggle_running(self) -> None:
        self.running = not self.running

    def reset(self) -> None:
        self.tick = 0
        self.generation = 1
        self.creatures.clear()
        self.food.clear()
        self._spawn_initial()

    def spawn_food(self, amount: int = 1) -> None:
        for _ in range(amount):
            if len(self.food) >= MAX_FOOD:
                return
            self.food.append(
                Food(
                    x=random.uniform(self.world_left + 7, self.world_right - 7),
                    y=random.uniform(self.world_top + 7, self.world_bottom - 7),
                    energy=random.uniform(18, 32),
                )
            )

    def nearest_food(self, creature: Creature):
        nearest = None
        nearest_dist = creature.genome.perception
        for food in self.food:
            dx = food.x - creature.x
            dy = food.y - creature.y
            d = math.hypot(dx, dy)
            if d < nearest_dist:
                nearest_dist = d
                nearest = food
        return nearest

    def step_creature(self, creature: Creature) -> tuple[bool, Creature | None]:
        creature.age += 1

        target = self.nearest_food(creature)
        if target is not None:
            desired = math.atan2(target.y - creature.y, target.x - creature.x)
            mix = 0.18 + 0.38 * min(1.0, creature.genome.greed / 2.0)
            creature.direction = (1 - mix) * creature.direction + mix * desired
        else:
            creature.direction += random.uniform(-0.4, 0.4) * creature.genome.wander

        velocity = creature.genome.speed
        creature.x += math.cos(creature.direction) * velocity
        creature.y += math.sin(creature.direction) * velocity

        if creature.x < self.world_left + 5 or creature.x > self.world_right - 5:
            creature.direction = math.pi - creature.direction
            creature.x = min(self.world_right - 5, max(self.world_left + 5, creature.x))
        if creature.y < self.world_top + 5 or creature.y > self.world_bottom - 5:
            creature.direction = -creature.direction
            creature.y = min(self.world_bottom - 5, max(self.world_top + 5, creature.y))

        upkeep = 0.22 + 0.22 * creature.genome.speed + 0.0009 * creature.genome.perception
        upkeep *= creature.genome.metabolism
        creature.energy -= upkeep

        eaten_idx = None
        for idx, food in enumerate(self.food):
            if math.hypot(food.x - creature.x, food.y - creature.y) < creature.radius() + 2:
                creature.energy += food.energy
                eaten_idx = idx
                break

        if eaten_idx is not None:
            del self.food[eaten_idx]

        baby = None
        if (
            creature.energy > creature.genome.fertility
            and creature.age > 60
            and len(self.creatures) < MAX_CREATURES
        ):
            creature.energy *= 0.56
            baby = Creature(
                x=creature.x + random.uniform(-12, 12),
                y=creature.y + random.uniform(-12, 12),
                genome=creature.genome.mutated(),
                energy=68,
            )
            if random.random() < 0.12:
                self.generation += 1

        alive = creature.energy > 0 and creature.age < 2000
        return alive, baby

    def simulate_tick(self) -> None:
        self.tick += 1
        if random.random() < 0.88:
            self.spawn_food()
        if random.random() < 0.06:
            self.spawn_food(amount=4)

        next_population: list[Creature] = []
        babies: list[Creature] = []

        for creature in self.creatures:
            alive, baby = self.step_creature(creature)
            if alive:
                next_population.append(creature)
            if baby:
                babies.append(baby)

        next_population.extend(babies)
        self.creatures = next_population

        if not self.creatures:
            self.generation += 1
            self._spawn_initial()

    def avg(self, field_name: str) -> float:
        if not self.creatures:
            return 0.0
        return sum(getattr(c.genome, field_name) for c in self.creatures) / len(self.creatures)

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
            text="Evolution Simulator",
            fill=TEXT_PRIMARY,
            font=("Segoe UI", 24, "bold"),
            anchor="w",
            tags="ui",
        )
        self.canvas.create_text(
            PANEL_X,
            64,
            text="Random movement + selection + mutation",
            fill=TEXT_MUTED,
            font=("Segoe UI", 11),
            anchor="w",
            tags="ui",
        )

        self.canvas.create_rectangle(PANEL_X - 2, 90, WIDTH - 24, HEIGHT - 24, outline="#2b3a58", width=2, tags="ui")

    def draw_dynamic(self) -> None:
        self.canvas.delete("dynamic")

        for food in self.food:
            self.canvas.create_oval(
                food.x - 2,
                food.y - 2,
                food.x + 2,
                food.y + 2,
                fill=FOOD_COLOR,
                outline="",
                tags="dynamic",
            )

        for creature in self.creatures:
            r = creature.radius()
            self.canvas.create_oval(
                creature.x - r,
                creature.y - r,
                creature.x + r,
                creature.y + r,
                fill=creature.color,
                outline="#0e141f",
                width=1,
                tags="dynamic",
            )
            nose_x = creature.x + math.cos(creature.direction) * (r + 2)
            nose_y = creature.y + math.sin(creature.direction) * (r + 2)
            self.canvas.create_oval(nose_x - 1.4, nose_y - 1.4, nose_x + 1.4, nose_y + 1.4, fill="#ffffff", outline="", tags="dynamic")

        status = "RUNNING" if self.running else "PAUSED"
        status_color = "#7cf38f" if self.running else "#ffd87b"
        avg_speed = self.avg("speed")
        avg_perception = self.avg("perception")
        avg_fertility = self.avg("fertility")
        avg_metabolism = self.avg("metabolism")

        lines = [
            ("Status", status, status_color),
            ("Ticks", f"{self.tick}", TEXT_PRIMARY),
            ("Generation", f"{self.generation}", TEXT_PRIMARY),
            ("Population", f"{len(self.creatures)}", TEXT_PRIMARY),
            ("Food", f"{len(self.food)}", TEXT_PRIMARY),
            ("", "", TEXT_PRIMARY),
            ("Avg speed", f"{avg_speed:.2f}", TEXT_PRIMARY),
            ("Avg vision", f"{avg_perception:.1f}", TEXT_PRIMARY),
            ("Avg fertility", f"{avg_fertility:.1f}", TEXT_PRIMARY),
            ("Avg metabolism", f"{avg_metabolism:.2f}", TEXT_PRIMARY),
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
            HEIGHT - 95,
            text="Controls:\nSPACE = pause/resume\nR = reset world",
            fill=TEXT_MUTED,
            font=("Segoe UI", 10),
            anchor="sw",
            tags="dynamic",
            justify="left",
        )

    def update_loop(self) -> None:
        if self.running:
            self.simulate_tick()
        self.draw_static_ui()
        self.draw_dynamic()
        self.root.after(30, self.update_loop)


def main() -> None:
    root = tk.Tk()
    EvolutionSimulator(root)
    root.mainloop()


if __name__ == "__main__":
    main()
