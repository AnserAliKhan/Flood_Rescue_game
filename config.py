# Game Configuration Constants

# Grid dimensions
ROWS = 10  # Number of rows in the grid
COLS = 30  # Number of columns in the grid

# Window settings
WINDOW_WIDTH = 1200  # Width of the game window in pixels
WINDOW_HEIGHT = 750  # Height of the game window in pixels
FPS = 60  # Frames per second for the main loop

# Grid visual settings
CELL_SIZE = 36  # Size of one grid cell in pixels (1080x360 total grid size)

# Scoring constants
POINTS_PER_PERSON = 5  # Points awarded for each saved person
EFFICIENCY_BONUS_PER_SANDBAG = 5  # Points awarded for each unused sandbag (Decision D5)

# Sandbag settings
SANDBAG_MARGIN = 5  # Extra sandbags given above the minimum for all levels (Decision D2)

# Building population values
POPULATION = {
    "house": 2,
    "school": 5,
    "hospital": 8
}

# Building counts per level (Decision D1)
LEVEL_BUILDINGS = {
    1: {"house": 5, "school": 2, "hospital": 0},
    2: {"house": 6, "school": 2, "hospital": 1},
    3: {"house": 7, "school": 2, "hospital": 2}
}

# Total target population per level
LEVEL_POPULATION = {
    1: 20,
    2: 30,
    3: 40
}
