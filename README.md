# Evolution Simulator (Python GUI)

A visually polished **evolution simulator** built with Python + Tkinter.

## What it does
- Spawns little creatures that move with randomized behavior.
- Creatures follow simple survival rules:
  - search for food,
  - spend energy to move,
  - die if they run out of energy,
  - reproduce when they have enough energy.
- Offspring inherit parent traits with mutation, so average behavior evolves over time.

## Evolution concepts included
- Randomness (movement jitter, mutation noise)
- Natural selection (survivors reproduce more)
- Emergent adaptation of traits such as speed, perception, fertility, and metabolism

## Run it
```bash
python3 evolution_simulator.py
```

## Controls
- `SPACE` → pause/resume simulation
- `R` → reset world

## Requirements
- Python 3.10+
- Tkinter (usually included with standard Python installations)
