# F00: Project Skeleton

## Goal
Prove the toolchain works end to end: Python, Pygame and pytest all run. Create the
smallest possible game entry point plus a central config file for shared constants.
No game logic yet.

## Context
This is the first feature. Setup (venv, git, docs, CLAUDE.md) is already done by the
student. Read CLAUDE.md, docs/DECISIONS.md and docs/SPEC.md first.

## Scope: files to create
- `config.py`: shared constants, no pygame import
- `main.py`: opens a window, runs the main loop, quits cleanly
- `tests/test_config.py`: pytest tests for the constants

Do NOT create any other module (grid.py, entities.py, etc.). Later features create those.

## Requirements

### config.py
Plain constants with short comments explaining each one:

- Grid: `ROWS = 10`, `COLS = 30`
- Window: `WINDOW_WIDTH = 1200`, `WINDOW_HEIGHT = 750`, `FPS = 60`
- `CELL_SIZE = 36` (so the grid is 1080 x 360 px and fits the window)
- Scoring: `POINTS_PER_PERSON = 5`, `EFFICIENCY_BONUS_PER_SANDBAG = 5` (D5)
- Sandbags: `SANDBAG_MARGIN = 5` (D2, same for all levels)
- Building population, as a dictionary:
  `POPULATION = {"house": 2, "school": 5, "hospital": 8}`
- Level building counts per D1, as a dictionary keyed by level number, e.g.
  `LEVEL_BUILDINGS = {1: {"house": 5, "school": 2, "hospital": 0}, ...}`
- Level target populations: `LEVEL_POPULATION = {1: 20, 2: 30, 3: 40}`

### main.py
- Initialise Pygame and open a `WINDOW_WIDTH x WINDOW_HEIGHT` window titled "Flood Rescue".
- Fill the background with a solid dark colour.
- Draw the text "FLOOD RESCUE" centred on screen using `pygame.font.Font(None, size)`.
- Main loop capped at `FPS`.
- The loop ends when the player closes the window or presses ESC.
- Call `pygame.quit()` on exit.
- Put the game loop inside a `main()` function and use `if __name__ == "__main__":`.
- Import all constants from `config.py`. No magic numbers in main.py.

### tests/test_config.py
Tests (pytest) for:
1. `ROWS * COLS == 300`
2. The grid (`COLS * CELL_SIZE` wide, `ROWS * CELL_SIZE` tall) fits inside the window.
3. For each level 1, 2, 3: the sum of `count * POPULATION[type]` over all building types
   equals `LEVEL_POPULATION[level]` (this checks decision D1).
4. Total building counts are 7, 9 and 11 for levels 1, 2 and 3.
5. Hospital count strictly increases from level 1 to 2 to 3.
Tests must NOT open a Pygame window and `config.py` must NOT import pygame.

## Acceptance criteria
- [ ] `python main.py` opens an 1200x750 window showing "FLOOD RESCUE".
- [ ] Closing the window or pressing ESC exits with no error or traceback.
- [ ] `pytest` runs from the project root and all tests pass.
- [ ] `config.py` has no pygame import.
- [ ] No file other than the three listed above is created (besides the plan file).
- [ ] Every constant in config.py has a comment.

## Python concepts demonstrated
Variables and data types, constants, dictionaries, functions, the `if __name__` entry
point, a loop with conditionals (event handling), modular programming (config separate
from main).

## Out of scope
Grid, cells, mouse input, buildings, sandbags, menus, colours palette beyond the
background and text, sound, images.

## End-of-feature report (required)
What was built, important code sections, Python concepts used, how to run and test it,
known limitations. Then STOP.