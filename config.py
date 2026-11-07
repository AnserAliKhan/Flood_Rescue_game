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
COLOR_LABEL_TEXT = (255, 255, 255) # White text for building labels

# Button Colours
COLOR_BTN_NORMAL = (70, 70, 100)
COLOR_BTN_HOVER = (90, 90, 130)
COLOR_BTN_ACTIVE = (120, 120, 160)
COLOR_BTN_TEXT = (255, 255, 255)
COLOR_MSG_TEXT = (255, 100, 100) # Light red for errors

# Cell type to colour mapping (SPEC.md 3.3)
CELL_COLORS = {
    CELL_EMPTY: (220, 220, 220),    # Light grey
    CELL_HOUSE: (160, 82, 45),      # Brown/orange
    CELL_SCHOOL: (255, 255, 100),   # Yellow
    CELL_HOSPITAL: (100, 149, 237), # Blue
    CELL_SHELTER: (50, 205, 50),    # Green
    CELL_SANDBAG: (105, 105, 105)   # Dark grey
}

# Labels for cell types
CELL_LABELS = {
    CELL_HOUSE: "H",
    CELL_SCHOOL: "S",
    CELL_HOSPITAL: "+",
    CELL_SHELTER: "SH",
    CELL_SANDBAG: "B",
    CELL_EMPTY: ""
}

LABEL_FONT_SIZE = 24

# Button Layouts (x, y, w, h)
BTN_SANDBAG_RECT = (50, 600, 200, 50)
BTN_RESET_RECT = (300, 600, 200, 50)
BTN_SANDBAG_LABEL = "SANDBAG TOOL"
BTN_RESET_LABEL = "RESET"

# Message Timeout
MESSAGE_TIMEOUT = 2000 # ms

# Test Layout (Level 2 match: 6 houses, 2 schools, 1 hospital, 1 shelter)
# Temporary layout, replaced by generator in F08
TEST_LAYOUT = [
    (CELL_SHELTER, 5, 15),
    (CELL_HOUSE, 1, 3), (CELL_HOUSE, 2, 10), (CELL_HOUSE, 7, 5),
    (CELL_HOUSE, 8, 14), (CELL_HOUSE, 3, 22), (CELL_HOUSE, 7, 25),
    (CELL_SCHOOL, 1, 18), (CELL_SCHOOL, 8, 22),
    (CELL_HOSPITAL, 5, 4)
]

# Scoring constants
POINTS_PER_PERSON = 5  # Points awarded for each saved person
EFFICIENCY_BONUS_PER_SANDBAG = 5  # Points awarded for each unused sandbag (Decision D5)

# Sandbag settings
SANDBAG_MARGIN = 5  # Extra sandbags given above the minimum for all levels (Decision D2)
TEST_SANDBAG_BUDGET = 40 # Temporary value for testing

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
