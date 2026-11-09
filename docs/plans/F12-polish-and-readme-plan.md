# Implementation Plan - Feature F12: Polish, Full Test Pass and README

## 1. Dead Constants, Imports, Functions, and Variables

An audit of all Python files in the project reveals the following dead or tests-only items and our planned actions:

| File | Item | Status | Action |
| :--- | :--- | :--- | :--- |
| `config.py` | `MSG_CONTINUE_PLACEHOLDER` | Dead (legacy F06 placeholder) | Delete. |
| `config.py` | `CURRENT_LEVEL` | Dead (campaign dict manages level in F10+) | Delete. |
| `config.py` | `TEST_LAYOUT` | Used only in legacy unit tests | Keep with explicit comment: `# Kept for unit tests only`. |
| `config.py` | `TEST_SANDBAG_BUDGET` | Used only in legacy unit tests | Keep with explicit comment: `# Kept for unit tests only`. |
| `flood.py` | `from config import ROWS` | Unused import (`COLS` is used, `ROWS` is not) | Remove `ROWS` from `config` import. |
| `interface.py` | `COLOR_HOVER`, `COLOR_SELECTED`, `BTN_SANDBAG_RECT`, `BTN_RESET_RECT`, `BTN_CONFIRM_RECT`, `BTN_SANDBAG_LABEL`, `BTN_RESET_LABEL`, `BTN_CONFIRM_LABEL`, `BTN_SUMMARY_LABEL`, `BTN_PLAY_AGAIN_RECT` | Unused imports from `config` | Remove from import tuple in `interface.py`. |
| `main.py` | `DIALOG_RECT` | Unused import from `config` | Remove from import tuple in `main.py`. |
| `screens.py` | `SCREEN_INSTRUCTIONS`, `SCREEN_GAME` | Unused imports from `config` | Remove from import tuple in `screens.py`. |
| `main.py` | Terminal prints `print(f"Level {level_num}...")` | Debug print | Gate behind `DEBUG_PRINT = False` in `config.py`. |

---

## 2. Literal Numbers and Inline Strings to Move to `config.py`

### A. Inline Strings
- `"Flood Rescue"` (window title) $\rightarrow$ `WINDOW_TITLE = "Flood Rescue"`
- `"Grid reset."` $\rightarrow$ `MSG_GRID_RESET = "Grid reset."`
- `"New campaign started!"` $\rightarrow$ `MSG_NEW_CAMPAIGN = "New campaign started!"`
- `"FLOOD RESCUE"` (header in panels) $\rightarrow$ `HEADER_TITLE = "FLOOD RESCUE"`

### B. Literal Layout, Geometry & Visual Coordinates
- Top panel width literal `1200` $\rightarrow$ `WINDOW_WIDTH`
- Top panel element coordinates:
  - Title position: `(20, 20)` $\rightarrow$ `PANEL_TITLE_POS = (20, 20)`
  - Level progress position: `(430, 20)` $\rightarrow$ `PANEL_LEVEL_POS = (430, 20)`
  - Campaign score position: `(430, 55)` $\rightarrow$ `PANEL_SCORE_POS = (430, 55)`
  - Phase status position: `(1000, 20)` $\rightarrow$ `PANEL_PHASE_POS = (1000, 20)`
  - Population/buildings stats: `(20, 60)` $\rightarrow$ `PANEL_STATS_POS = (20, 60)`
  - Sandbag count: `(1000, 60)` $\rightarrow$ `PANEL_SANDBAG_POS = (1000, 60)`
  - Hover info: `(20, 120)` $\rightarrow$ `PANEL_HOVER_POS = (20, 120)`
  - Selected info: `(430, 120)` $\rightarrow$ `PANEL_SELECTED_POS = (430, 120)`
- Legend layout:
  - Box size: `20` $\rightarrow$ `LEGEND_BOX_SIZE = 20`
  - Origin: `(50, 670)` $\rightarrow$ `LEGEND_START_X = 50`, `LEGEND_START_Y = 670`
  - Horizontal spacing: `150` $\rightarrow$ `LEGEND_SPACING = 150`
- Indicator dots:
  - Radius: `6` $\rightarrow$ `STATUS_INDICATOR_RADIUS = 6`
- Banner positions:
  - Flood banner: `(600, 25)` $\rightarrow$ `BANNER_FLOOD_POS = (WINDOW_WIDTH // 2, 25)`
  - Flood skip hint: `(600, 65)` $\rightarrow$ `BANNER_SKIP_POS = (WINDOW_WIDTH // 2, 65)`
- Results panel layout:
  - Columns: `RESULTS_COL1_X = 80`, `RESULTS_COL2_X = 400`, `RESULTS_COL3_X = 720`
  - Title Y: `620` $\rightarrow$ `RESULTS_TITLE_Y = 620`
  - Bonus message: `(600, 715)` $\rightarrow$ `RESULTS_BONUS_MSG_POS = (WINDOW_WIDTH // 2, 715)`
- Confirmation dialog:
  - Title center: `(600, 290)` $\rightarrow$ `DIALOG_TITLE_POS = (WINDOW_WIDTH // 2, 290)`
  - Subtitle center: `(600, 340)` $\rightarrow$ `DIALOG_SUBTITLE_POS = (WINDOW_WIDTH // 2, 340)`
  - Info center: `(600, 375)` $\rightarrow$ `DIALOG_INFO_POS = (WINDOW_WIDTH // 2, 375)`
- Main menu positions:
  - Title center: `(600, 150)` $\rightarrow$ `MENU_TITLE_POS = (WINDOW_WIDTH // 2, 150)`
  - Tagline center: `(600, 230)` $\rightarrow$ `MENU_TAGLINE_POS = (WINDOW_WIDTH // 2, 230)`
- Instructions positions:
  - Title center: `(600, 50)` $\rightarrow$ `INSTRUCTIONS_TITLE_POS = (WINDOW_WIDTH // 2, 50)`
- Summary screen positions:
  - Title: `(600, 55)` $\rightarrow$ `SUMMARY_TITLE_POS = (WINDOW_WIDTH // 2, 55)`
  - Subtitle: `(600, 105)` $\rightarrow$ `SUMMARY_SUBTITLE_POS = (WINDOW_WIDTH // 2, 105)`
  - Total score: `(600, 395)` $\rightarrow$ `SUMMARY_TOTAL_SCORE_POS = (WINDOW_WIDTH // 2, 395)`
  - People: `(600, 455)` $\rightarrow$ `SUMMARY_PEOPLE_POS = (WINDOW_WIDTH // 2, 455)`
  - Efficiency: `(600, 500)` $\rightarrow$ `SUMMARY_EFFICIENCY_POS = (WINDOW_WIDTH // 2, 500)`
  - Commentary: `(600, 545)` $\rightarrow$ `SUMMARY_COMMENTARY_POS = (WINDOW_WIDTH // 2, 545)`
- Mouse buttons:
  - `MOUSE_BTN_LEFT = 1`, `MOUSE_BTN_RIGHT = 3`

---

## 3. Font Creation Strategy

### Current Issue
Currently, `pygame.font.Font(None, ...)` is called every single frame in multiple branches of `main.py` and `interface.py` (e.g., `Font(None, 64)`, `Font(None, 36)`, `Font(None, 30)`, etc.). This causes needless garbage collection churn.

### Solution
1. Define font size constants in `config.py`:
   ```python
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
   LABEL_FONT_SIZE = 24  # Existing
   ```
2. In `interface.py`, provide a single initialization function `init_fonts()`:
   ```python
   def init_fonts():
       """Creates and returns all application fonts in a dictionary once."""
       return {
           "title_large": pygame.font.Font(None, FONT_SIZE_TITLE_LARGE),
           "title_main": pygame.font.Font(None, FONT_SIZE_TITLE_MAIN),
           "section": pygame.font.Font(None, FONT_SIZE_SECTION),
           "large": pygame.font.Font(None, FONT_SIZE_LARGE),
           "button": pygame.font.Font(None, FONT_SIZE_BUTTON),
           "button_large": pygame.font.Font(None, FONT_SIZE_BUTTON_LARGE),
           "body": pygame.font.Font(None, FONT_SIZE_BODY),
           "heading": pygame.font.Font(None, FONT_SIZE_HEADING),
           "small": pygame.font.Font(None, FONT_SIZE_SMALL),
           "instructions": pygame.font.Font(None, FONT_SIZE_INSTRUCTIONS),
           "coord": pygame.font.Font(None, FONT_SIZE_COORD),
           "cell": pygame.font.Font(None, LABEL_FONT_SIZE),
       }
   ```
3. In `main.py`, call `fonts = interface.init_fonts()` **once** at startup after `pygame.init()`, and pass `fonts` (or individual fonts from it) to drawing calls. No per-frame font construction.

---

## 4. SPEC Section 15 Traceability Tests (`tests/test_spec_section15.py`)

A dedicated test suite containing exactly 19 tests, each quoting the SPEC item in its docstring and asserting the exact requirement:

| Item | SPEC 15 Requirement | New Test Name | Overlaps With Existing Test |
| :--- | :--- | :--- | :--- |
| **1** | Grid contains exactly 300 cells (10x30). | `test_15_01_grid_cell_count` | `test_grid.py::test_create_grid`, `test_config.py::test_grid_size` |
| **2** | No building overlaps another building (3 default levels + 50 seeds). | `test_15_02_no_building_overlaps` | `test_level_generator.py::test_no_overlaps_and_in_bounds`, `test_stress_200_seeds` |
| **3** | Exactly one shelter is generated per level. | `test_15_03_exactly_one_shelter_per_level` | `test_level_generator.py::test_generate_level_counts_and_populations` |
| **4** | Population totals are correct (20, 30, 40). | `test_15_04_population_totals` | `test_config.py::test_level_populations` |
| **5** | Sandbag budget equals baseline + SANDBAG_MARGIN; hand-made baseline matches. | `test_15_05_sandbag_budget_calculation` | `test_baseline.py::test_sandbag_budget_formula`, `test_single_building_straight_line` |
| **6** | Sandbags cannot be placed outside the grid (including negative). | `test_15_06_sandbag_cannot_be_placed_out_of_bounds` | `test_sandbags.py::test_place_sandbag_failures` |
| **7** | Sandbags cannot overwrite buildings or shelter. | `test_15_07_sandbag_cannot_overwrite_buildings` | `test_sandbags.py::test_place_sandbag_failures` |
| **8** | Sandbag placement decreases remaining count by one. | `test_15_08_placement_decreases_remaining_budget` | `test_sandbags.py::test_place_sandbag_success` |
| **9** | Removing a sandbag restores remaining count by one. | `test_15_09_removal_restores_remaining_budget` | `test_sandbags.py::test_remove_sandbag` |
| **10** | Diagonal connections are not accepted. | `test_15_10_diagonal_connections_not_accepted` | `test_pathfinding.py::test_diagonals_fail` |
| **11** | Valid horizontal connections are accepted. | `test_15_11_horizontal_connections_accepted` | `test_pathfinding.py::test_straight_chains` |
| **12** | Valid vertical connections are accepted. | `test_15_12_vertical_connections_accepted` | `test_pathfinding.py::test_straight_chains` |
| **13** | Buildings connected to shelter are marked safe (connected=True). | `test_15_13_connected_buildings_marked_safe` | `test_pathfinding.py::test_evaluate_connectivity_flags` |
| **14** | Disconnected buildings are marked unsafe (connected=False). | `test_15_14_disconnected_buildings_marked_unsafe` | `test_pathfinding.py::test_evaluate_connectivity_flags` |
| **15** | Population score equals saved people x POINTS_PER_PERSON. | `test_15_15_population_score_calculation` | `test_scoring.py::test_partial_connectivity` |
| **16** | Efficiency bonus equals unused sandbags x weight if all saved; 0 if anyone unsaved (Amended D5). | `test_15_16_efficiency_bonus_calculation_amended_d5` | `test_scoring.py::test_everybody_connected`, `test_build_nothing_exploit` |
| **17** | Three levels increase in difficulty (buildings 7<9<11, pop 20<30<40, hospitals 0<1<2). | `test_15_17_levels_increasing_difficulty` | `test_config.py::test_total_building_counts`, `test_hospital_progression` |
| **18** | Game restarts without retaining old level data (fresh grid, clean campaign). | `test_15_18_restart_retains_no_old_data` | `test_campaign.py::test_restart_independence`, `test_screens.py::test_game_restart_deterministic_clean_state` |
| **19** | Flood animation does not affect underlying score calculation. | `test_15_19_flood_animation_does_not_affect_scoring` | `test_flood.py::test_flooded_cells_partition` |

---

## 5. Fuzz Playthrough Test Design (`tests/test_fuzz_playthrough.py`)

### Randomization
- For each of the 3 levels, across seeds 0 to 99 (`random.Random(seed)`):
  - Generate level layout and calculate budget.
  - Choose a random count of sandbag placement attempts (from 0 to `budget + 10`).
  - Sample random grid coordinates `(r, c)`.
  - Attempt placement with `try/except ValueError` (safely ignoring out-of-budget or occupied cells).

### Assertions & Invariants
1. Full flow (`create_game_state` $\rightarrow$ `request_confirmation` $\rightarrow$ `confirm_routes` $\rightarrow$ `finish_flood`) raises no unhandled exception.
2. `saved_people + unsaved_people == total_population`.
3. `sandbags_used + sandbags_remaining == sandbags_allocated`.
4. `final_score == population_score + efficiency_bonus`.
5. If `not passed`: `efficiency_bonus == 0`.
6. `passed == (unsaved_people == 0)`.
7. Grid dimensions stay 10x30; building/shelter cell positions and types remain unchanged.
8. Every non-shelter entity has `connected in (True, False)`.
9. Sets partition correctly: `flooded_cells & safe_cells == set()`, and `len(flooded_cells | safe_cells) == 300`.
10. `retry_level` resets all sandbags, leaves layout identical, and resets entity flags to `None`.
11. Baseline route fuzz check: placing the exact baseline route passes every time with `passed == True` and leaves exactly `SANDBAG_MARGIN` sandbags.

### Execution Time
Breadth-first and depth-first searches on a 10x30 grid execute in ~0.05 ms. 300 test runs will execute in **under 2 seconds**.

---

## 6. Documentation Outline and Real Data Verification

### A. `README.md`
1. **Title & One-Paragraph Description**: Introduction to "Flood Rescue", a 2D grid puzzle and strategy game designed for a university Computational Thinking course.
2. **Requirements & Installation**: Python 3.12+, venv creation, `pip install -r requirements.txt` (Windows, macOS, Linux).
3. **How to Run & Test**: Commands for `python main.py`, `python -m pytest tests/ -v`, and code audit.
4. **How to Play & Scoring Rules**: Controls, objectives, building populations, and scoring equations (incorporating Decision D5).
5. **Project Structure**: ASCII directory tree classifying modules as pure logic vs Pygame GUI.
6. **Architecture Overview**: Decoupled dual state machines (screens vs game phases), grid as single source of truth, "backend-first, animation-second" architecture.
7. **Algorithms**: Recursive DFS connectivity (depth safety, base cases, loop prevention), greedy shortest-path BFS baseline (upper bound, shared trunk reuse), seeded PRNG placement with retry loop.
8. **Course Concept Map**: Detailed table mapping 11+ computational concepts (2D lists, dicts, recursion, etc.) to exact files and functions.
9. **Authoritative Decisions**: Summary of Decisions D1 through D7 and superseded SPEC.md sections.
10. **Testing & Traceability**: Test statistics, test design, and the complete SPEC 15 traceability table.
11. **Known Limitations & Credits**: Links to `docs/KNOWN_ISSUES.md`, Pygame/Python credits.

### B. `docs/DEMO_NOTES.md`
- **2-Minute Presentation Script**: Step-by-step walkthrough for an oral viva / demo.
- **Concept Deep-Dive**: File, function, and clear 3-sentence explanation for each concept in SPEC 13.
- **DFS Walkthrough**: Concrete trace of `dfs_visit` on a 6-cell example, detailing stack frames and visited-set loop prevention.
- **BFS Baseline Walkthrough**: Concrete trace demonstrating how shared trunk cells are counted once.
- **10 Viva / Professor Questions**: Concise answers with file and line references.

### C. `docs/QA_CHECKLIST.md`
- Manual test matrix with checkable boxes `[ ]` and observations column covering:
  - Menu navigation, Instructions screen back/escape navigation.
  - Planning phase interactions, sandbag limits, reset button, coordinate feedback.
  - Confirm dialog, start flood vs keep planning.
  - Flood animation sweep, skip on space/click.
  - Results breakdown, conditional continue button, retry level.
  - Final summary screen metrics, Play Again restart, Main Menu return.
  - Layout determinism check across 3 repeated runs.

### D. `docs/KNOWN_ISSUES.md`
- Documented architectural choices:
  - Linear column flood sweep vs complex 2D hydraulic fluid modeling.
  - Greedy shortest-path BFS baseline is an upper bound rather than NP-hard Steiner tree minimum.
  - Intentional absence of mid-game pause/menu button during active planning phase.
  - No persistent disk save/load of in-progress games.
  - Pygame `pkg_resources` deprecation warning emitted by upstream library.

### Verification of Real Numbers
All numbers in the documentation will be generated from live code execution:
- Python version (`3.12.0`) and Pygame version (`2.6.1`).
- Test count from `pytest -v` (~180 tests).
- Baseline sandbags & budgets:
  - Level 1 (seed 101): baseline = 24, budget = 29
  - Level 2 (seed 202): baseline = 34, budget = 39
  - Level 3 (seed 303): baseline = 35, budget = 40
- Reference maximum campaign score: 125 + 175 + 225 = 525.

---

## 7. Fresh Clone Installation Verification

To guarantee that a fresh clone installs and runs without error:
1. `requirements.txt` will strictly specify:
   ```
   pygame==2.6.1
   pytest==8.3.5
   ```
2. Assets folders: Keep `assets/images/.gitkeep` and `assets/fonts/.gitkeep` so git tracks the directory structure while the README notes procedural vector rendering.
3. Verification procedure:
   - Run a test in an isolated subshell that imports all modules and launches `main.py` headlessly with `SDL_VIDEODRIVER=dummy`.
   - Verify `git status` reports no untracked or missing configuration files.

---

## 8. Existing Tests Impact Analysis

No test logic or game behavior will change.
- In `config.py`, `TEST_LAYOUT` and `TEST_SANDBAG_BUDGET` will be retained and annotated as `# Kept for unit tests only`, preserving 100% compatibility with earlier tests in `test_entities.py`, `test_pathfinding.py`, `test_sandbags.py`, and `test_game.py`.
- The symbol table audit test in `test_interface_smoke.py` will automatically succeed with the cleaned-up imports.

---

## 9. Ambiguities and Conflicts with DECISIONS.md or SPEC.md

1. **Efficiency Bonus Specification**:
   - `SPEC 9.2` awarded efficiency bonuses even when civilians were left unsaved (e.g. 16/20 saved).
   - `DECISIONS.md` (Decision D5) explicitly amended this: bonus is strictly 0 unless 100% of civilians are saved.
   - *Plan*: `test_15_16_efficiency_bonus_calculation_amended_d5` tests the amended D5 rule and cites the override in its docstring.
2. **Relay Buildings Rule**:
   - `SPEC 8.1` suggested buildings relaying to buildings might require sandbags between them.
   - `DECISIONS.md` (Decision D3) clarified that touching buildings connect directly without sandbags on building cells.
   - *Plan*: `test_15_11` and `test_15_12` assert the D3 rule.
3. **Assets Directory**:
   - `SPEC 12` listed `assets/images` and `assets/fonts`.
   - The game renders all graphics procedurally using Pygame vector drawing primitives and system fonts.
   - *Plan*: We retain the directory structure with `.gitkeep` files and document the procedural rendering choice in the README.
4. **Final Results Screen Name**:
   - `SPEC 11` called it "SCREEN 8: FINAL RESULTS"; the implementation calls it "FINAL SUMMARY" (`PHASE_SUMMARY`).

---

## 10. Risks and Mitigations

| Risk | Mitigation |
| :--- | :--- |
| **Missing imports during cleanup** | Run `test_smoke_config_symbols_exist` which audits the AST symbol table of all GUI and screen modules before finishing. |
| **Regression in visual layout** | Every moved coordinate will preserve its exact pixel value in `config.py`. Smoke tests in `tests/test_interface_smoke.py` verify no rendering errors. |
| **Fuzz test performance slowdown** | The fuzz test operates entirely on pure Python data structures without GUI overhead, executing 300 trials in ~1.5 seconds. |
| **Font caching regressions** | `interface.init_fonts()` creates all fonts once and passes them via dictionary, ensuring backwards-compatible defaults if optional parameters are omitted in smoke tests. |

