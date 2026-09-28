# Sky Hill

A tiny original side-scrolling platformer written in Python with [Pygame](https://www.pygame.org/).
Run, jump, collect coins, dodge the red walkers, and reach the flag on all three hills.

![Sky Hill gameplay](screenshots/level1.png)

## Screenshots

| Start screen | Level 3: Cloud Crest | Victory |
| --- | --- | --- |
| ![Start screen](screenshots/start.png) | ![Cloud Crest level](screenshots/level3.png) | ![Win screen](screenshots/win.png) |

## Features

- Three hand-built levels: **Sunny Slope**, **Breezy Gaps** and **Cloud Crest**
- Smooth side-scrolling camera with a parallax background
- Gold coins worth 10 points each (27 in total, for a max score of 270)
- Patrolling enemies that send you back to the start of the level
- 3 lives, with start, game over and victory screens
- Single file, no assets needed. Everything is drawn with shapes.

## Getting started

You need **Python 3.8+**.

```bash
git clone https://github.com/yugdogra0/sky-hill.git
cd sky-hill
pip install -r requirements.txt
python game.py
```

## Controls

| Action | Keys |
| --- | --- |
| Move | `Left` / `Right` or `A` / `D` |
| Jump | `Space`, `Up` or `W` |
| Start / play again | `Space` or `Enter` |
| Quit | `Esc` |

## How to play

- Reach the **flag pole** at the end of each hill to move on to the next one.
- Collect **gold coins** for points.
- Touching a **red walker** or falling off the map costs a life and restarts the level.
- Lose all 3 lives and it's game over. Clear all three hills to win.

## Tweaking the game

All the game-feel settings are constants at the top of `game.py`:

```python
MOVE_SPEED = 7       # how fast the player runs
GRAVITY = 0.62       # how quickly the player falls
JUMP_VEL = -13.2     # jump strength (more negative = higher)
START_LIVES = 3
```

Levels are plain Python data in `make_levels()`, so you can add platforms, coins and enemies
by editing the lists there.

## Project structure

```
sky-hill/
├── game.py            # the whole game
├── requirements.txt   # pygame dependency
├── screenshots/       # images used in this README
└── README.md
```
