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

# Panel layout
TOP_PANEL_HEIGHT = 100  # Height of the top information panel
BOTTOM_PANEL_HEIGHT = 150  # Height of the bottom control panel

# Grid position
GRID_ORIGIN_X = (WINDOW_WIDTH - COLS * CELL_SIZE) // 2  # Horizontal center
GRID_ORIGIN_Y = 170  # Vertical offset to leave room for top panel and labels

# Cell types
CELL_EMPTY = "empty"
CELL_HOUSE = "house"
CELL_SCHOOL = "school"
CELL_HOSPITAL = "hospital"
CELL_SHELTER = "shelter"
CELL_SANDBAG = "sandbag"

# Colours (RGB)
COLOR_BG = (30, 30, 50)        # Dark blue-grey background
COLOR_PANEL = (50, 50, 80)    # Slightly lighter panel color
COLOR_GRID_LINE = (80, 80, 110) # Grid borders
COLOR_TEXT = (240, 240, 240)   # Off-white text
COLOR_HOVER = (100, 100, 150)   # Hover highlight
COLOR_SELECTED = (150, 150, 200) # Selected highlight

# Cell type to colour mapping (SPEC.md 3.3)
CELL_COLORS = {
    CELL_EMPTY: (220, 220, 220),    # Light grey
    CELL_HOUSE: (160, 82, 45),      # Brown/orange
    CELL_SCHOOL: (255, 255, 100),   # Yellow
    CELL_HOSPITAL: (100, 149, 237), # Blue
    CELL_SHELTER: (50, 205, 50),    # Green
    CELL_SANDBAG: (105, 105, 105)   # Dark grey
}

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
