# Implementation Plan - Feature F11: Main Menu and Instructions Screen

## 1. Files to Create or Change

| File | Status | Purpose |
| :--- | :--- | :--- |
| `screens.py` | **Create** | Pure logic module (no Pygame imports) managing application screen states (`menu`, `instructions`, `game`), screen transitions, button hit-testing, and dynamic instruction text generation from config values. |
| `tests/test_screens.py` | **Create** | Pytest unit test suite verifying `screens.py` logic, state transitions, hit-testing, and template generation. |
| `config.py` | **Change** | Add screen identifiers, screen transition table, menu and instruction button rectangles/captions, summary button layout, instruction section templates, and visual layout constants. |
| `interface.py` | **Change** | Add `draw_menu` and `draw_instructions` rendering functions; update `draw_final_summary` to render both `PLAY AGAIN` and `MAIN MENU` buttons. |
| `main.py` | **Change** | Initialize `app_state` on menu without loading a level upfront. Route event handling and rendering by `app["screen"]`. Support `START GAME`, `INSTRUCTIONS`, `EXIT`, `BACK`, and summary screen navigation. |
| `tests/test_interface_smoke.py` | **Change** | Add headless Pygame smoke tests for `draw_menu`, `draw_instructions`, instruction text line-width verification, and dual summary buttons. |

---

## 2. Constants and Functions (Names and Signatures)

### A. `config.py`
```python
# Screen identifiers
SCREEN_MENU = "menu"
SCREEN_INSTRUCTIONS = "instructions"
SCREEN_GAME = "game"

# Screen Transition Table
# Main menu can open instructions or game. Instructions return to menu.
# Game can return to menu (allowed only from summary phase, verified by logic).
ALLOWED_SCREEN_TRANSITIONS = {
    SCREEN_MENU:         [SCREEN_INSTRUCTIONS, SCREEN_GAME],
    SCREEN_INSTRUCTIONS: [SCREEN_MENU],
    SCREEN_GAME:         [SCREEN_MENU],
}

# Main Menu Layout & Captions
MENU_TITLE = "FLOOD RESCUE"
MENU_TAGLINE = "Build routes. Save everyone."
MENU_BUTTON_START = "start"
MENU_BUTTON_INSTRUCTIONS = "instructions"
MENU_BUTTON_EXIT = "exit"

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

# Instructions Screen Layout & Captions
INSTRUCTIONS_TITLE = "HOW TO PLAY & RULES"
INSTRUCTIONS_BACK_RECT = (500, 650, 200, 50)
INSTRUCTIONS_BACK_LABEL = "BACK"

# Instruction Column Layout
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
            "Connect every building to the green shelter with sandbags before the flood."
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

# Summary Screen Dual Buttons (Replaces single centered button)
SUMMARY_PLAY_AGAIN_RECT = (340, 620, 240, 50)
SUMMARY_MENU_RECT = (620, 620, 240, 50)
BTN_PLAY_AGAIN_RECT = SUMMARY_PLAY_AGAIN_RECT  # Backwards compatibility alias
BTN_PLAY_AGAIN_LABEL = "PLAY AGAIN"
BTN_MENU_LABEL = "MAIN MENU"
```

### B. `screens.py` (Pure Logic, NO pygame import)
```python
def create_app_state() -> dict:
    """
    Creates and returns the initial application state.
    Returns:
        dict: {"screen": SCREEN_MENU}
    """

def change_screen(app: dict, new_screen: str) -> None:
    """
    Transitions the application to new_screen if allowed by ALLOWED_SCREEN_TRANSITIONS.
    Raises ValueError if transition is illegal or unknown, leaving app unchanged.
    """

def can_return_to_menu(game_state: dict | None) -> bool:
    """
    Returns True only if game_state exists and game_state["phase"] == PHASE_SUMMARY.
    Returns False during planning, confirming, flooding, results, or if state is None.
    """

def button_at(buttons: dict[str, tuple[int, int, int, int]], x: int, y: int) -> str | None:
    """
    Hit-tests a point (x, y) against a dictionary of name -> (bx, by, bw, bh).
    Returns the matching button name, or None if no button contains the point.
    Rule: Left and top edges are inside; right and bottom edges are outside:
          bx <= x < bx + bw and by <= y < by + bh.
    """

def build_instruction_sections() -> list[tuple[str, list[str]]]:
    """
    Reads templates from config.INSTRUCTION_SECTIONS_TEMPLATES and substitutes
    placeholders dynamically from config at call time:
      {points}       -> config.POINTS_PER_PERSON
      {bonus}        -> config.EFFICIENCY_BONUS_PER_SANDBAG
      {margin}       -> config.SANDBAG_MARGIN
      {house_pop}    -> config.POPULATION[config.CELL_HOUSE]
      {school_pop}   -> config.POPULATION[config.CELL_SCHOOL]
      {hospital_pop} -> config.POPULATION[config.CELL_HOSPITAL]
    Raises ValueError if any unfilled placeholder remains or key is invalid.
    """
```

### C. `interface.py` (Rendering Functions)
```python
def draw_menu(screen, hovered_btn_name, font_title, font_tagline, font_btn):
    """
    Renders the full-screen Main Menu:
    - Screen background
    - Title and Tagline centered
    - Three buttons: START GAME, INSTRUCTIONS, EXIT from config.MENU_BUTTONS
    """

def draw_instructions(screen, sections, back_hovered, font_title, font_heading, font_body, font_btn):
    """
    Renders the full-screen Instructions screen:
    - Screen background and Title
    - Two columns of sections (Col 1: Goal, How to Play, Rules; Col 2: People, Scoring, Levels)
    - BACK button centered at the bottom
    """

def draw_final_summary(screen, summary, font_title, font_table, font_large, play_again_hovered=False, menu_hovered=False):
    """
    Renders the final summary screen with table, aggregates, and TWO side-by-side buttons:
    - PLAY AGAIN (SUMMARY_PLAY_AGAIN_RECT)
    - MAIN MENU  (SUMMARY_MENU_RECT)
    """
```

---

## 3. Layout Numbers Showing Everything Fits Without Overlap (1200 x 750)

### A. Main Menu Layout
- **Window Dimensions**: 1200 x 750
- **Title**: `y = 150`, font size 64, centered horizontally at `x = 600`.
- **Tagline**: `y = 230`, font size 30, centered horizontally at `x = 600`.
- **Buttons** (Width = 360, Height = 64, Gap = 24):
  - Horizontal Center: `x = (1200 - 360) // 2 = 420` (spans `x: 420` to `780`).
  - Button 1 ("start"): `(420, 340, 360, 64)` $\rightarrow$ spans `y: 340` to `404`.
  - Gap: `404` to `428` (24 px).
  - Button 2 ("instructions"): `(420, 428, 360, 64)` $\rightarrow$ spans `y: 428` to `492`.
  - Gap: `492` to `516` (24 px).
  - Button 3 ("exit"): `(420, 516, 360, 64)` $\rightarrow$ spans `y: 516` to `580`.
- **Bottom margin**: `750 - 580 = 170 px`.
- **Conclusion**: All 3 buttons fit comfortably within screen bounds with 24 px gaps and zero overlap.

### B. Instructions Screen Layout
- **Title**: `y = 50`, font size 42, centered at `(600, 50)`.
- **Two Columns**:
  - Column 1: `x = 80`, width = 500 (spans `x: 80` to `580`). Sections: Goal, How to Play, Rules.
  - Center Gutter: `x: 580` to `620` (40 px).
  - Column 2: `x = 620`, width = 500 (spans `x: 620` to `1120`). Sections: People, Scoring, Levels.
  - Side Margins: 80 px left and right (`80 + 500 + 40 + 500 + 80 = 1200`).
- **Vertical Spacing**:
  - Starting `y = 110`.
  - Section title height: ~26 px. Line height: 22 px. Section gap: 14 px.
  - Col 1 total lines = 10 lines + 3 headers $\rightarrow$ total height $\approx 310\text{ px}$ (reaches `y \approx 420`).
  - Col 2 total lines = 9 lines + 3 headers $\rightarrow$ total height $\approx 290\text{ px}$ (reaches `y \approx 400`).
- **BACK Button**: `(500, 650, 200, 50)`
  - Horizontal Center: `(1200 - 200) // 2 = 500` (spans `x: 500` to `700`).
  - Vertical span: `y: 650` to `700`.
  - Clearance above button: `650 - 420 = 230 px` of free space.
  - Clearance below button: `750 - 700 = 50 px` margin to bottom of window.
- **Conclusion**: Perfect fit, generous padding, zero overlap.

### C. Final Summary Screen Dual Buttons
- **Window Dimensions**: 1200 x 750
- **Summary Table & Text**: Ends at commentary note `y = 545` (spans `y: 535` to `555`).
- **Dual Buttons** (Width = 240 each, Height = 50, Gap = 40):
  - Total width of button pair: `240 + 40 + 240 = 520 px`.
  - Left offset: `(1200 - 520) // 2 = 340`.
  - `SUMMARY_PLAY_AGAIN_RECT`: `(340, 620, 240, 50)` $\rightarrow$ spans `x: 340` to `580`, `y: 620` to `670`.
  - Gap: `x: 580` to `620` (40 px).
  - `SUMMARY_MENU_RECT`: `(620, 620, 240, 50)` $\rightarrow$ spans `x: 620` to `860`, `y: 620` to `670`.
- **Clearance**:
  - Top clearance: `620 - 555 = 65 px` below commentary text.
  - Bottom margin: `750 - 670 = 80 px` above screen bottom.
- **Conclusion**: Side-by-side, 40 px horizontal separation, completely non-overlapping and centered.

---

## 4. Main Loop Routing and Shared Level Loading

### A. Level Loading Function
In `main.py`, the existing `load_level(level_num)` from F10 is preserved as the single point of level creation:
```python
def load_level(level_num):
    grid_data, entities_data, baseline_val, budget = campaign.prepare_level(level_num)
    new_state = game.create_game_state()
    print(f"Level {level_num}: baseline {baseline_val}, budget {budget}")
    return grid_data, entities_data, budget, new_state
```
Both **Start Game** (from Menu) and **Play Again** (from Summary) call this exact function with `level_num=1` and a fresh `campaign.create_campaign(start_level=1)`.

### B. Event Routing by Screen
```python
if app["screen"] == SCREEN_MENU:
    # 1. Mouse movement: hit-test MENU_BUTTONS with screens.button_at
    # 2. Left click:
    #    - "start": camp = campaign.create_campaign(1); game_grid, entities_list, total_budget, state = load_level(1); screens.change_screen(app, SCREEN_GAME)
    #    - "instructions": screens.change_screen(app, SCREEN_INSTRUCTIONS)
    #    - "exit": running = False
    # 3. Keydown ESC: running = False

elif app["screen"] == SCREEN_INSTRUCTIONS:
    # 1. Mouse movement: check hover on INSTRUCTIONS_BACK_RECT
    # 2. Left click on INSTRUCTIONS_BACK_RECT: screens.change_screen(app, SCREEN_MENU)
    # 3. Keydown ESC: screens.change_screen(app, SCREEN_MENU)

elif app["screen"] == SCREEN_GAME:
    # Execute F10 gameplay event handling
    # In PHASE_SUMMARY:
    #   - Hover checks for SUMMARY_PLAY_AGAIN_RECT and SUMMARY_MENU_RECT
    #   - Click PLAY AGAIN: camp = campaign.create_campaign(1); load_level(1)
    #   - Click MAIN MENU:
    #       if screens.can_return_to_menu(state):
    #           screens.change_screen(app, SCREEN_MENU)
    #           camp = None; game_grid = None; entities_list = None; state = None
```

---

## 5. Main Loop Initialization: No Level Exists Before Start Game

At the start of `main()`:
1. `app = screens.create_app_state()` (`app["screen"] == "menu"`).
2. Level variables are initialized to `None`:
   ```python
   camp = None
   game_grid = None
   entities_list = None
   total_budget = 0
   state = None
   ```
3. No level generator, BFS baseline, or grid arrays run at application boot.
4. When `START GAME` is clicked, `camp` and `load_level(1)` are instantiated.
5. When `MAIN MENU` is clicked from summary, `camp`, `game_grid`, `entities_list`, and `state` are reset to `None`, freeing memory and ensuring no stale state or water overlays persist.

---

## 6. How Instruction Lines Are Checked to Fit Their Column

1. **Width Constraint**: Column width is `INSTRUCTIONS_COL_WIDTH = 500 px`. A safe readable text boundary is 480 px (allowing 20 px padding).
2. **Automated Smoke Test Verification**:
   - In `tests/test_interface_smoke.py`, a dedicated test `test_smoke_instruction_lines_fit_column` will instantiate the body font used by `draw_instructions` (`pygame.font.Font(None, 22)`).
   - It calls `screens.build_instruction_sections()` to generate all resolved strings.
   - For every section and every line, it calculates `width, _ = font.size(line)`.
   - It asserts `width < INSTRUCTIONS_COL_WIDTH` (and `< 480 px`), failing explicitly with the line text and measured pixel width if any line overflows.

---

## 7. Each New Test and What It Checks

### Unit Tests (`tests/test_screens.py` - Pure Logic)
1. `test_create_app_state`: Returns dict with exactly key `"screen"` set to `"menu"`.
2. `test_legal_screen_transitions`: Tests legal transitions: `menu -> instructions`, `instructions -> menu`, `menu -> game`, `game -> menu`.
3. `test_illegal_screen_transitions`: Asserts `ValueError` and unchanged `app` on illegal transitions (`instructions -> game`, `menu -> menu`, `game -> instructions`, unknown screen names).
4. `test_allowed_transitions_constants`: Verifies all keys and values in `ALLOWED_SCREEN_TRANSITIONS` are valid constants.
5. `test_can_return_to_menu`: Returns `True` only when `state["phase"] == PHASE_SUMMARY`; `False` for `planning`, `confirming`, `flooding`, `results`, and `None`.
6. `test_button_at_hit_testing`: Verifies button hit testing: middle of each button, gaps between buttons (`None`), outside window (`None`), top-left corner (inclusive), and bottom-right boundary (exclusive).
7. `test_button_layouts_fit_and_no_overlap`: Verifies menu buttons, instruction back button, and summary buttons are within `(1200, 750)` and non-overlapping.
8. `test_build_instruction_sections_count_and_placeholders`: Returns 6 non-empty sections; no `{` or `}` characters remain.
9. `test_build_instruction_sections_values`: Contains string representations of `POINTS_PER_PERSON`, `SANDBAG_MARGIN`, `EFFICIENCY_BONUS_PER_SANDBAG`, and `POPULATION` values.
10. `test_build_instruction_sections_monkeypatch`: Modifying config values dynamically updates output text when `build_instruction_sections` is called.
11. `test_build_instruction_sections_unknown_placeholder`: Unrecognized placeholder triggers `ValueError`.
12. `test_screen_flow_sequence`: Executes valid sequence `menu -> game -> menu -> instructions -> menu`.
13. `test_game_restart_deterministic_clean_state`: Starting game twice from menu produces identical Level 1 layout with fresh scores.

### Smoke Tests (`tests/test_interface_smoke.py` - Headless Pygame)
1. `test_smoke_menu`: Renders `draw_menu` with no hover and for each button hover (`start`, `instructions`, `exit`).
2. `test_smoke_instructions`: Renders `draw_instructions` with real sections, with and without back hover.
3. `test_smoke_instruction_lines_fit_column`: Verifies every resolved instruction line is narrower than column width.
4. `test_smoke_final_summary_two_buttons`: Renders `draw_final_summary` with `play_again_hovered` and `menu_hovered` on full, partial, and empty campaigns.
5. `test_smoke_config_symbols_exist`: Verifies all symbols imported from `config` across `interface.py`, `main.py`, and `screens.py` exist.

---

## 8. Ambiguities and Conflicts with DECISIONS.md or SPEC.md

1. **Backwards Compatibility of `BTN_PLAY_AGAIN_RECT`**:
   - `SPEC.md` / `F10` defined `BTN_PLAY_AGAIN_RECT = (475, 620, 250, 50)`.
   - `F11` specifies dual buttons: `SUMMARY_PLAY_AGAIN_RECT` and `SUMMARY_MENU_RECT`.
   - *Plan note*: We will define `SUMMARY_PLAY_AGAIN_RECT = (340, 620, 240, 50)` and alias `BTN_PLAY_AGAIN_RECT = SUMMARY_PLAY_AGAIN_RECT` so any previous code or tests looking for `BTN_PLAY_AGAIN_RECT` remain intact.
2. **Instructions Template Population Placeholders**:
   - `SPEC.md` / `F11` specifies displaying population numbers (house 2, school 5, hospital 8) from `POPULATION`.
   - The plan provides explicit named placeholders (`{house_pop}`, `{school_pop}`, `{hospital_pop}`) mapped directly to `config.POPULATION`.

---

## 9. Risks and Mitigations

| Risk | Mitigation |
| :--- | :--- |
| **Instruction text line wrapping / overflow** | Define short, concise bullet points in `config.py` and enforce length programmatically with `test_smoke_instruction_lines_fit_column`. |
| **State leakage when returning to Main Menu** | Fully reset `camp = None`, `state = None`, and grid pointers in `main.py` when transitioning from summary to menu. |
| **Breaking F10 Game Phase Transitions** | F11 does NOT alter `game.py` or `ALLOWED_TRANSITIONS`. The screen state machine is kept strictly separate from the game phase machine. |
| **Undefined config constants during rendering** | Comprehensive AST / symbol table audit test (`test_smoke_config_symbols_exist`) prevents missing imports. |
| **Accidental Pygame import in logic** | `screens.py` will not import `pygame`, verified by architecture and tests. |

