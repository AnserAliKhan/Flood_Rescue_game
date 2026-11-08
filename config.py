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

# Directions for grid traversal (Up, Down, Left, Right)
# Diagonals are intentionally absent per connectivity rules
DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]

# Game Phases
PHASE_PLANNING = "planning"
PHASE_CONFIRMING = "confirming"
PHASE_FLOODING = "flooding"       # Added in F07: visual flood sweep
PHASE_RESULTS = "results"
PHASE_SUMMARY = "summary"         # Added in F10: final multi-level campaign summary

# Transition Table: map of current phase to allowed next phases
# F10: Results can transition to planning (retry) or summary (after Level 3).
# Exiting summary is done by starting a fresh campaign/state (Play Again).
ALLOWED_TRANSITIONS = {
    PHASE_PLANNING:   [PHASE_CONFIRMING],
    PHASE_CONFIRMING: [PHASE_PLANNING, PHASE_FLOODING],
    PHASE_FLOODING:   [PHASE_RESULTS],
    PHASE_RESULTS:    [PHASE_PLANNING, PHASE_SUMMARY],
    PHASE_SUMMARY:    [],
}

CURRENT_LEVEL = 1  # Legacy constant for earlier unit tests; campaign dictionary manages active level in F10+

# Human-readable level titles
LEVEL_NAMES = {1: "Easy", 2: "Medium", 3: "Hard"}

# Developer debug hotkeys flag (keys 1/2/3 in planning)
DEBUG_LEVEL_KEYS = False

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

# Result Highlights
COLOR_SAFE = (50, 205, 50)      # Green for connected
COLOR_UNSAFE = (200, 50, 50)    # Red for not connected

# Flood Animation Colours (F07)
COLOR_WATER = (30, 100, 200, 120)        # Semi-transparent blue (RGBA)
COLOR_WATER_FRONT = (60, 140, 240, 160)  # Brighter blue for the leading wave edge

# Dialog Colors
COLOR_DIALOG_BG = (60, 60, 90)
COLOR_DIMMER = (0, 0, 0, 150)  # RGBA for transparent overlay

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
BTN_CONFIRM_RECT = (550, 600, 250, 50)
BTN_RETRY_RECT = (400, 650, 200, 50)
BTN_CONTINUE_RECT = (650, 650, 200, 50)

# Dialog Layout
DIALOG_RECT = (400, 250, 400, 250)
DIALOG_YES_RECT = (450, 420, 120, 50)
DIALOG_CANCEL_RECT = (580, 420, 120, 50)

BTN_SANDBAG_LABEL = "SANDBAG TOOL"
BTN_RESET_LABEL = "RESET"
BTN_CONFIRM_LABEL = "CONFIRM ROUTES / START FLOOD"
BTN_RETRY_LABEL = "RETRY LEVEL"
BTN_CONTINUE_LABEL = "CONTINUE TO NEXT LEVEL"
BTN_SUMMARY_LABEL = "VIEW FINAL SUMMARY"
BTN_PLAY_AGAIN_LABEL = "PLAY AGAIN"
DIALOG_TITLE = "Confirm Routes?"
DIALOG_YES_LABEL = "START FLOOD"
DIALOG_CANCEL_LABEL = "KEEP PLANNING"

# Summary Screen Layout & Typography (Window: 1200 x 750)
SUMMARY_TITLE = "MISSION COMPLETE - FINAL SUMMARY"
SUMMARY_SUBTITLE = "All areas secured! Evacuation successful."
SUMMARY_COL_HEADINGS = ["Level", "Saved / Total", "Sandbags Used", "Pop Score", "Bonus", "Score"]
SUMMARY_TABLE_X = 150
SUMMARY_TABLE_Y = 160
SUMMARY_ROW_HEIGHT = 45
SUMMARY_COL_WIDTHS = [120, 180, 180, 140, 120, 160]  # Sum = 900px, 150px left/right margins
BTN_PLAY_AGAIN_RECT = (475, 630, 250, 55)

# Summary Colors
COLOR_SUMMARY_TITLE = (255, 215, 0)      # Gold
COLOR_SUMMARY_SUBTITLE = (180, 220, 255) # Light cyan
COLOR_SUMMARY_LINE = (80, 80, 120)       # Divider line
COLOR_SUMMARY_HEADER = (200, 200, 240)   # Light lavender
COLOR_TOTAL_SCORE = (50, 205, 50)        # Vibrant green

# Message texts
MSG_CONTINUE_PLACEHOLDER = "Coming in Feature F10..."
MSG_BONUS_DENIED = "No efficiency bonus: not everyone was saved"
MSG_BONUS_AWARDED = "Efficiency bonus awarded!"
MSG_FLOODING_BANNER = "THE FLOOD IS COMING..."       # Banner during flood animation
MSG_FLOODING_SKIP = "Press SPACE or click to skip"   # Skip hint during flood

# Flood Animation Timing (F07)
FLOOD_STEP_MS = 60       # ms per column; 30 x 60 = 1.8 s for the full sweep
FLOOD_END_HOLD_MS = 800  # pause after the last column before results appear

# Message Timeout
MESSAGE_TIMEOUT = 2000 # ms

# Test Layout (Level 2 match: 6 houses, 2 schools, 1 hospital, 1 shelter)
# Legacy layout kept for earlier tests; no longer used by main.py in F08+
TEST_LAYOUT = [
    (CELL_SHELTER, 5, 15),
    (CELL_HOUSE, 1, 3), (CELL_HOUSE, 2, 10), (CELL_HOUSE, 7, 5),
    (CELL_HOUSE, 8, 14), (CELL_HOUSE, 3, 22), (CELL_HOUSE, 7, 25),
    (CELL_SCHOOL, 1, 18), (CELL_SCHOOL, 8, 22),
    (CELL_HOSPITAL, 5, 4)
]

# Level Generation Configuration (F08)
# Fixed seeds per level for reproducibility (Decision D4)
LEVEL_SEEDS = {
    1: 101,
    2: 202,
    3: 303
}

# Allowed column ranges (inclusive) and row range for buildings and shelter per level
LEVEL_REGIONS = {
    1: {"buildings_cols": (6, 23), "shelter_cols": (12, 17), "rows": (0, 9)},
    2: {"buildings_cols": (2, 27), "shelter_cols": (10, 19), "rows": (0, 9)},
    3: {"buildings_cols": (0, 29), "shelter_cols": (8, 21),  "rows": (0, 9)},
}

# Spacing rule: orthogonal gap between any two entities (Decision D3 / F08)
# Buildings and shelter must not touch orthogonally. Diagonal touching is allowed.
MIN_BUILDING_GAP = 1

# Placement retry limits:
# MAX_PLACEMENT_TRIES is how many random coordinates to sample per building before restarting.
# MAX_LEVEL_RESTARTS is how many whole-layout attempts to make before giving up.
MAX_PLACEMENT_TRIES = 200
MAX_LEVEL_RESTARTS = 50

# Scoring constants
POINTS_PER_PERSON = 5  # Points awarded for each saved person
EFFICIENCY_BONUS_PER_SANDBAG = 5  # Points awarded for each unused sandbag (Decision D5)

# Sandbag settings
SANDBAG_MARGIN = 5  # Extra sandbags given above baseline for all levels (Decision D2; formula in baseline.calculate_sandbag_budget)
TEST_SANDBAG_BUDGET = 40  # Legacy constant kept for earlier unit tests; no longer used by main.py in F09+

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

# Total number of levels in campaign (derived from LEVEL_BUILDINGS)
NUM_LEVELS = len(LEVEL_BUILDINGS)

# Total target population per level
LEVEL_POPULATION = {
    1: 20,
    2: 30,
    3: 40
}
