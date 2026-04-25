# Virus Spread Simulator (Python GUI)

A visually polished **virus spread simulator** built with Python + Tkinter.

## What it does
- Simulates a moving population where infection can spread by close contact.
- Uses an SIR-style model with three health states:
  - Susceptible (blue),
  - Infected (red),
  - Recovered (green).
- Lets you adjust:
  - infection rate,
  - recovery rate.
- Helps you watch outbreak patterns emerge in real time.

## Run it
```bash
python3 evolution_simulator.py
```

## Controls
- `SPACE` → pause/resume simulation
- `R` → reset world
- Sliders on the right panel adjust infection and recovery rates live.

## Requirements
- Python 3.10+
- Tkinter (usually included with standard Python installations)
- also has a few other thing but this is the " main " thing.


## Bonus: Aim Trainer Game (Advanced)
A fast-paced click trainer with random targets, reaction-time analytics, combo scoring, and multiple difficulty levels.

### Features
- Random target spawning with timed despawn penalties.
- Real-time reaction tracking (average and best in ms).
- Accuracy, streaks, score multipliers, and post-round grading.
- Difficulty presets: Easy, Medium, Hard, Insane.

### Run
```bash
python3 aim_trainer_game.py
```
