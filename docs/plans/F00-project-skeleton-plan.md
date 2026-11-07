# Plan: F00 Project Skeleton

## Context
This is the first implementation feature for Flood Rescue. The goal is to establish a working toolchain (Python, Pygame, pytest) and create the foundation of the project by setting up a central configuration and a basic game entry point.

## Proposed Implementation

### 1. Files to Create

- `config.py`: Central store for all game constants. This file is a pure logic module and must not import Pygame.
- `main.py`: The game entry point. Handles window initialization, the main loop, and clean exit.
- `tests/test_config.py`: Unit tests to validate that the constants in `config.py` are logically correct and adhere to the project decisions.

### 2. Constants and Functions

#### `config.py`
Constants:
- `ROWS = 10` # Number of rows in the grid
- `COLS = 30` # Number of columns in the grid
- `WINDOW_WIDTH = 1200` # Width of the game window in pixels
- `WINDOW_HEIGHT = 750` # Height of the game window in pixels
- `FPS = 60` # Frames per second for the main loop
- `CELL_SIZE = 36` # Size of one grid cell in pixels
- `POINTS_PER_PERSON = 5` # Points awarded for each saved person
- `EFFICIENCY_BONUS_PER_SANDBAG = 5` # Points awarded for each unused sandbag (D5)
- `SANDBAG_MARGIN = 5` # Extra sandbags given above the minimum (D2)
- `POPULATION = {"house": 2, "school": 5, "hospital": 8}` # People per building type
- `LEVEL_BUILDINGS = { ... }` # Dictionary mapping level (1, 2, 3) to building counts (house, school, hospital) based on D1
- `LEVEL_POPULATION = {1: 20, 2: 30, 3: 40}` # Target population per level

#### `main.py`
Functions:
- `main()`:
    - Initializes Pygame.
    - Sets the window size and title.
    - Creates a screen object.
    - Defines colors (dark background, white/light text).
    - Initializes font.
    - Runs the `while` loop for event handling and rendering.
    - Handles `pygame.QUIT` and `pygame.K_ESCAPE`.
    - Clears screen, draws "FLOOD RESCUE" text, and updates display.
    - Calls `pygame.quit()`.

#### `tests/test_config.py`
Tests (pytest functions):
- `test_grid_size()`: Checks `ROWS * COLS == 300`.
- `test_grid_fits_window()`: Checks if the total grid pixels (`COLS * CELL_SIZE` x `ROWS * CELL_SIZE`) are less than or equal to `WINDOW_WIDTH` and `WINDOW_HEIGHT`.
- `test_level_populations()`: For levels 1, 2, and 3, validates that `sum(count * POPULATION[type])` equals `LEVEL_POPULATION[level]`.
- `test_total_building_counts()`: Validates total buildings are 7, 9, and 11 for levels 1, 2, and 3 respectively.
- `test_hospital_progression()`: Checks that hospital counts strictly increase (L1 < L2 < L3).

### 3. Verification Plan

- **Execution Test:** Run `python main.py`.
    - Expect: A 1200x750 window titled "Flood Rescue" with centered text.
    - Action: Press ESC or close the window.
    - Expect: Clean exit without errors.
- **Logic Test:** Run `pytest`.
    - Expect: All tests in `tests/test_config.py` pass.
- **Constraint Check:** Verify `config.py` does not contain `import pygame`.

### 4. Ambiguities and Conflicts
- None identified. The feature spec aligns perfectly with `DECISIONS.md` (specifically D1, D2, and D5).

### 5. Risks
- Pygame installation: If the environment is not set up correctly, `main.py` will fail to import Pygame.
- Font issues: `pygame.font.Font(None, size)` uses the default system font; on some rare systems, this might behave inconsistently, but it is the standard beginner approach.
