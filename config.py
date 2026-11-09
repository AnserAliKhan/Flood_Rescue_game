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

# Screen names (F11: App-level screens, separate from game phases)
SCREEN_MENU = "menu"
SCREEN_INSTRUCTIONS = "instructions"
SCREEN_GAME = "game"

# Allowed screen transitions (SPEC section 11 / F11)
# Note: Exit is not a screen (it quits the app).
# "game to menu" is only allowed from the summary phase (enforced by screens.can_return_to_menu).
ALLOWED_SCREEN_TRANSITIONS = {
    SCREEN_MENU:         [SCREEN_INSTRUCTIONS, SCREEN_GAME],
    SCREEN_INSTRUCTIONS: [SCREEN_MENU],
    SCREEN_GAME:         [SCREEN_MENU],
}

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

# Human-readable level titles
LEVEL_NAMES = {1: "Easy", 2: "Medium", 3: "Hard"}

# Developer debug flags
DEBUG_LEVEL_KEYS = False  # Keys 1/2/3 jump to levels during planning phase (debug only)
DEBUG_PRINT = False       # Print baseline and budget info to terminal when loading levels

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
BTN_MENU_LABEL = "MAIN MENU"
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

# Dual summary buttons (F11): side by side, centered as a pair with 40px gap
# Total pair width = 240 + 40 + 240 = 520; (1200 - 520) // 2 = 340
SUMMARY_PLAY_AGAIN_RECT = (340, 620, 240, 50)
SUMMARY_MENU_RECT = (620, 620, 240, 50)
BTN_PLAY_AGAIN_RECT = SUMMARY_PLAY_AGAIN_RECT  # Backwards compatibility alias for tests

# Main Menu Layout & Typography (Window: 1200 x 750)
MENU_TITLE = "FLOOD RESCUE"
MENU_TAGLINE = "Build routes. Save everyone."
MENU_BUTTON_START = "start"
MENU_BUTTON_INSTRUCTIONS = "instructions"
MENU_BUTTON_EXIT = "exit"

# Three menu buttons: 360 x 64 px, centered horizontally at (1200 - 360)//2 = 420, 24 px gaps
MENU_BUTTONS = {
    MENU_BUTTON_START:        (420, 340, 360, 64),
    MENU_BUTTON_INSTRUCTIONS: (420, 428, 360, 64),
    MENU_BUTTON_EXIT:         (420, 516, 360, 64),
}

MENU_CAPTIONS = {
    MENU_BUTTON_START:        "START GAME",
    MENU_BUTTON_INSTRUCTIONS: "INSTRUCTIONS",
    MENU_BUTTON_EXIT:         "EXIT",
}

# Instructions Screen Layout & Typography (Window: 1200 x 750)
INSTRUCTIONS_TITLE = "HOW TO PLAY & RULES"
INSTRUCTIONS_BACK_RECT = (500, 650, 200, 50)  # Centered: (1200 - 200)//2 = 500
INSTRUCTIONS_BACK_LABEL = "BACK"

# Instruction columns layout (two columns, 500px wide each, 40px center gutter)
INSTRUCTIONS_COL1_X = 80
INSTRUCTIONS_COL2_X = 620
INSTRUCTIONS_COL_WIDTH = 500
INSTRUCTIONS_START_Y = 110
INSTRUCTIONS_LINE_HEIGHT = 22
INSTRUCTIONS_SECTION_GAP = 14

# Instruction Section Templates (titles and lines with placeholders)
INSTRUCTION_SECTIONS_TEMPLATES = [
    (
        "Goal",
        [
            "Connect every building to the green shelter",
            "with sandbags before the flood."
        ]
    ),
    (
        "How to Play",
        [
            "1. Press S or click SANDBAG TOOL to toggle placement mode.",
            "2. Left-click an empty cell to place a sandbag.",
            "3. Click or right-click an existing sandbag to remove it.",
            "4. RESET clears all placed sandbags.",
            "5. CONFIRM starts the flood simulation once routes are ready."
        ]
    ),
    (
        "Rules",
        [
            "• Sandbags connect up, down, left, and right only (no diagonals).",
            "• Adjacent buildings link directly to each other and the shelter.",
            "• A building touching the safe network needs no extra sandbags.",
            "• Sandbags cannot be placed on buildings or the shelter."
        ]
    ),
    (
        "People",
        [
            "• House (H): {house_pop} people",
            "• School (S): {school_pop} people",
            "• Hospital (+): {hospital_pop} people"
        ]
    ),
    (
        "Scoring",
        [
            "• {points} points awarded per person safely evacuated.",
            "• Leftover sandbags earn {bonus} points bonus each,",
            "  but ONLY if everyone in the level is saved."
        ]
    ),
    (
        "Levels",
        [
            "• Three levels with increasing civilian populations.",
            "• Sandbag budget equals minimum baseline + {margin} margin.",
            "• CONTINUE appears only when all civilians are saved;",
            "  otherwise, you must retry the level."
        ]
    )
]

# Summary Colors
COLOR_SUMMARY_TITLE = (255, 215, 0)      # Gold
COLOR_SUMMARY_SUBTITLE = (180, 220, 255) # Light cyan
COLOR_SUMMARY_LINE = (80, 80, 120)       # Divider line
COLOR_SUMMARY_HEADER = (200, 200, 240)   # Light lavender
COLOR_TOTAL_SCORE = (50, 205, 50)        # Vibrant green

# Window Title and Headers
WINDOW_TITLE = "Flood Rescue"
HEADER_TITLE = "FLOOD RESCUE"

# Message texts
MSG_GRID_RESET = "Grid reset."
MSG_NEW_CAMPAIGN = "New campaign started!"
MSG_BONUS_DENIED = "No efficiency bonus: not everyone was saved"
MSG_BONUS_AWARDED = "Efficiency bonus awarded!"
MSG_FLOODING_BANNER = "THE FLOOD IS COMING..."       # Banner during flood animation
MSG_FLOODING_SKIP = "Press SPACE or click to skip"   # Skip hint during flood

# Font Size Constants (F12)
FONT_SIZE_TITLE_LARGE = 64
FONT_SIZE_TITLE_MAIN = 42
FONT_SIZE_SECTION = 36
FONT_SIZE_LARGE = 56
FONT_SIZE_BUTTON = 30
FONT_SIZE_BUTTON_LARGE = 32
FONT_SIZE_BODY = 28
FONT_SIZE_HEADING = 26
FONT_SIZE_SMALL = 24
FONT_SIZE_INSTRUCTIONS = 22
FONT_SIZE_COORD = 16

# UI Element Coordinates and Layout Positions (F12)
# Top panel positions
PANEL_TITLE_POS = (20, 20)
PANEL_LEVEL_POS = (430, 20)
PANEL_SCORE_POS = (430, 55)
PANEL_PHASE_POS = (1000, 20)
PANEL_STATS_POS = (20, 60)
PANEL_SANDBAG_POS = (1000, 60)
PANEL_HOVER_POS = (20, 120)
PANEL_SELECTED_POS = (430, 120)

# Legend layout
LEGEND_BOX_SIZE = 20
LEGEND_START_X = 50
LEGEND_START_Y = 670
LEGEND_SPACING = 150
STATUS_INDICATOR_RADIUS = 6

# Banners and feedback positions
BANNER_FLOOD_POS = (WINDOW_WIDTH // 2, 25)
BANNER_SKIP_POS = (WINDOW_WIDTH // 2, 65)
MESSAGE_CENTER_POS = (WINDOW_WIDTH // 2, 715)

# Results panel positions
RESULTS_TITLE_Y = 620
RESULTS_COL1_X = 80
RESULTS_COL2_X = 400
RESULTS_COL3_X = 720
RESULTS_BONUS_MSG_POS = (WINDOW_WIDTH // 2, 720)

# Confirmation dialog positions
DIALOG_TITLE_POS = (WINDOW_WIDTH // 2, 290)
DIALOG_SUBTITLE_POS = (WINDOW_WIDTH // 2, 340)
DIALOG_INFO_POS = (WINDOW_WIDTH // 2, 375)

# Menu & Instructions screen positions
MENU_TITLE_POS = (WINDOW_WIDTH // 2, 150)
MENU_TAGLINE_POS = (WINDOW_WIDTH // 2, 230)
INSTRUCTIONS_TITLE_POS = (WINDOW_WIDTH // 2, 50)

# Summary screen positions
SUMMARY_TITLE_POS = (WINDOW_WIDTH // 2, 55)
SUMMARY_SUBTITLE_POS = (WINDOW_WIDTH // 2, 105)
SUMMARY_TOTAL_SCORE_POS = (WINDOW_WIDTH // 2, 395)
SUMMARY_PEOPLE_POS = (WINDOW_WIDTH // 2, 455)
SUMMARY_EFFICIENCY_POS = (WINDOW_WIDTH // 2, 500)
SUMMARY_COMMENTARY_POS = (WINDOW_WIDTH // 2, 545)

# Mouse Button Codes
MOUSE_BTN_LEFT = 1
MOUSE_BTN_RIGHT = 3

# Flood Animation Timing (F07)
FLOOD_STEP_MS = 60       # ms per column; 30 x 60 = 1.8 s for the full sweep
FLOOD_END_HOLD_MS = 800  # pause after the last column before results appear

# Message Timeout
MESSAGE_TIMEOUT = 2000 # ms

# Test Layout (Level 2 match: 6 houses, 2 schools, 1 hospital, 1 shelter)
# Kept for unit tests only; no longer used by main.py in F08+
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
TEST_SANDBAG_BUDGET = 40  # Kept for unit tests only; no longer used by main.py in F09+

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
