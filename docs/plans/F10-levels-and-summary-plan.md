# F10 Levels and Summary — Implementation Plan

## 1. Files to Create or Change

| File | Action | Purpose |
|---|---|---|
| `campaign.py` | CREATE | Pure-logic module (no pygame). Manages multi-level campaign progression, level preparation, result recording, level completion routing, and final summary aggregation. |
| `tests/test_campaign.py` | CREATE | Pure-logic pytest suite covering all 17 campaign test cases (state, progression, determinism, copying, validation, summary totals, full playthrough). |
| `tests/test_interface_smoke.py` | CREATE | Headless Pygame smoke tests using `SDL_VIDEODRIVER="dummy"` exercising all rendering routines (planning, dialog, flood, results, summary). |
| `config.py` | CHANGE | Add `PHASE_SUMMARY`, `NUM_LEVELS`, updated `ALLOWED_TRANSITIONS`, `LEVEL_NAMES`, `DEBUG_LEVEL_KEYS = False`, summary layout constants (button rects, table positions, text captions, colors). Mark `CURRENT_LEVEL` as legacy. |
| `game.py` | CHANGE | Add `show_summary(state)`, update `is_editing_allowed` and `can_continue` to handle `PHASE_SUMMARY`. |
| `tests/test_game.py` | CHANGE | Update transition tests for `PHASE_SUMMARY` and add tests for `show_summary` and summary phase restrictions. |
| `interface.py` | CHANGE | Update `draw_panels` (level name, progress, running score), update `draw_results_panel` (dynamic Continue caption), and implement `draw_final_summary` for the full-window end-game summary screen. |
| `main.py` | CHANGE | Integrate `campaign` dictionary, unify level loading into `load_level(level_num)`, handle Continue/Summary routing, implement summary screen event loop and `PLAY AGAIN` restart, guard debug keys behind `DEBUG_LEVEL_KEYS`. |

---

## 2. Every Constant and Function (Names and Signatures)

### A. `config.py` Additions

```python
# Game Phases (F10 adds final summary screen)
PHASE_SUMMARY = "summary"

# Total number of levels in campaign (derived from LEVEL_BUILDINGS)
NUM_LEVELS = len(LEVEL_BUILDINGS)  # 3

# Transition Table: map of current phase to allowed next phases
# Results can either retry (planning) or progress to final summary on Level 3
ALLOWED_TRANSITIONS = {
    PHASE_PLANNING:   [PHASE_CONFIRMING],
    PHASE_CONFIRMING: [PHASE_PLANNING, PHASE_FLOODING],
    PHASE_FLOODING:   [PHASE_RESULTS],
    PHASE_RESULTS:    [PHASE_PLANNING, PHASE_SUMMARY],
    PHASE_SUMMARY:    [],  # Exiting summary creates a brand new campaign/state
}

# Human-readable level titles
LEVEL_NAMES = {1: "Easy", 2: "Medium", 3: "Hard"}

# Developer debug hotkeys flag (keys 1/2/3 in planning)
DEBUG_LEVEL_KEYS = False

# Button captions & text constants
BTN_CONTINUE_LABEL = "CONTINUE TO NEXT LEVEL"
BTN_SUMMARY_LABEL = "VIEW FINAL SUMMARY"
BTN_PLAY_AGAIN_LABEL = "PLAY AGAIN"

SUMMARY_TITLE = "MISSION COMPLETE - FINAL SUMMARY"
SUMMARY_SUBTITLE = "All areas secured! Evacuation successful."
SUMMARY_COL_HEADINGS = ["Level", "Saved / Total", "Sandbags Used", "Pop Score", "Bonus", "Score"]

# Summary screen layout coordinates (Window: 1200 x 750)
SUMMARY_TABLE_X = 150
SUMMARY_TABLE_Y = 160
SUMMARY_ROW_HEIGHT = 45
SUMMARY_COL_WIDTHS = [120, 180, 180, 140, 120, 160]  # Sum = 900px, margins = 150px each side

BTN_PLAY_AGAIN_RECT = (475, 630, 250, 55)

# Summary colors
COLOR_SUMMARY_TITLE = (255, 215, 0)      # Gold
COLOR_SUMMARY_SUBTITLE = (180, 220, 255) # Light cyan
COLOR_SUMMARY_LINE = (80, 80, 120)       # Divider line
COLOR_SUMMARY_HEADER = (200, 200, 240)   # Light lavender
COLOR_TOTAL_SCORE = (50, 205, 50)        # Vibrant green
```

### B. `campaign.py` (Pure Logic, Zero Pygame Imports)

```python
def create_campaign(start_level: int = 1) -> dict:
    """
    Initializes a new campaign state dictionary.
    Returns {'level': start_level, 'level_results': {}}.
    Raises ValueError if start_level not in 1..NUM_LEVELS.
    Example: create_campaign() -> {'level': 1, 'level_results': {}}
    """

def prepare_level(level: int) -> tuple[list[list[str]], list[dict], int, int]:
    """
    Generates level layout and calculates baseline sandbags and total budget.
    Returns (grid, entities, baseline_sandbags, total_budget).
    Raises ValueError if level not in 1..NUM_LEVELS.
    Example: prepare_level(1) -> (grid, entities, 24, 29)
    """

def is_last_level(campaign: dict) -> bool:
    """
    Returns True if the campaign is currently on the final level (NUM_LEVELS).
    Example: is_last_level({'level': 3, ...}) -> True
    """

def is_campaign_complete(campaign: dict) -> bool:
    """
    Returns True if every level 1..NUM_LEVELS has a stored result in level_results.
    Example: is_campaign_complete(campaign) -> True
    """

def record_level_result(campaign: dict, breakdown: dict) -> None:
    """
    Stores a deep copy of breakdown under the current campaign level.
    Raises ValueError if breakdown['passed'] is not True or level was already recorded.
    Example: record_level_result(campaign, breakdown)
    """

def complete_level(campaign: dict, state: dict) -> str:
    """
    Called when player clicks Continue.
    Validates game.can_continue(state), records the level result.
    If on final level, returns 'summary'.
    Otherwise advances campaign['level'] by 1 and returns 'next_level'.
    Leaves campaign unchanged on error.
    Example: complete_level(campaign, state) -> 'next_level'
    """

def build_final_summary(campaign: dict) -> dict:
    """
    Aggregates campaign results into a summary dictionary:
    - 'rows': list of dicts per recorded level in level order.
    - 'total_score': sum of final scores.
    - 'total_people_saved', 'total_population': summed population stats.
    - 'sandbags_allocated', 'sandbags_used', 'sandbags_remaining': summed sandbag stats.
    - 'efficiency_percent': 100 * sandbags_remaining / sandbags_allocated rounded to 1 decimal (0.0 if empty).
    - 'levels_completed': count of recorded levels.
    Example: build_final_summary(campaign) -> {'total_score': 525, ...}
    """
```

### C. `game.py` Changes

```python
def show_summary(state: dict) -> None:
    """
    Transitions the game state from results to summary phase.
    Only valid in results phase and when state['breakdown']['passed'] is True.
    Raises ValueError otherwise, leaving state unchanged.
    Example: show_summary(state)
    """
```

### D. `interface.py` Changes

```python
def draw_panels(screen, hover_info, selected_info, pop_info, build_info,
                sandbag_info, phase_name, current_level=1, campaign_score=0):
    # Renders "Level X / 3 - Name" and "Score so far: N" in the top panel.

def draw_results_panel(screen, breakdown, can_continue, font,
                       current_level=1, continue_label=BTN_CONTINUE_LABEL):
    # Renders results with dynamic Continue button label (Next Level vs Final Summary).

def draw_final_summary(screen, summary, font_title, font_table, font_large,
                       play_again_hovered=False):
    # Renders the full-screen campaign summary table, aggregate scores, and PLAY AGAIN button.
```

---

## 3. Transition Table and Campaign / State Mechanics

### Transition Table

```
planning   -> [confirming]
confirming -> [planning, flooding]
flooding   -> [results]
results    -> [planning, summary]
summary    -> []
```

### Mechanics Breakdown

1. **Continue Action (in `PHASE_RESULTS`)**:
   - Guarded by `game.can_continue(state)` (must be in results, `breakdown["passed"] == True`).
   - Calls `outcome = campaign.complete_level(campaign, state)`.
   - `complete_level` records a copy of `state["breakdown"]` into `campaign["level_results"][current_level]`.
   - If `current_level < NUM_LEVELS`:
     - Increments `campaign["level"] += 1`.
     - Returns `"next_level"`.
     - `main.py` invokes `load_level(campaign["level"])`, regenerating the board for the new level and resetting `state` to a fresh `PHASE_PLANNING` dictionary.
   - If `current_level == NUM_LEVELS`:
     - Keeps `campaign["level"] = 3`.
     - Returns `"summary"`.
     - `main.py` invokes `game.show_summary(state)`, changing `state["phase"] = PHASE_SUMMARY`.

2. **Retry Action (in `PHASE_RESULTS`)**:
   - Calls `game.retry_level(state, game_grid, entities_list)`.
   - **Campaign is untouched**: `campaign["level"]` stays the same; `campaign["level_results"]` has no result recorded for this level.
   - **Board is preserved**: sandbags cleared, connectivity flags reset to None, exact building positions and seed preserved (Decision D4).
   - `state["phase"]` returns to `PHASE_PLANNING`.

3. **Play Again Action (in `PHASE_SUMMARY`)**:
   - Triggered by clicking `BTN_PLAY_AGAIN_RECT` on the summary screen.
   - Reinitializes campaign: `campaign = create_campaign(start_level=1)`.
   - Invokes `load_level(1)`: resets grid, loads Level 1 layout with seed 101, resets budget to Level 1 baseline + 5, resets `state` to `PHASE_PLANNING`.

---

## 4. Exact List of Existing Tests That Must Change

### In `tests/test_game.py`:
1. `test_transitions`:
   - Change legal transitions: `Results -> Summary` is legal.
   - Add illegal transitions: `Summary -> Planning` (or any other phase) raises `ValueError`.
   - Add illegal transitions: `Planning -> Summary`, `Confirming -> Summary`, `Flooding -> Summary` raise `ValueError`.
2. `test_editing_allowed`:
   - Add assertion: `is_editing_allowed(state)` is `False` when `state["phase"] == PHASE_SUMMARY`.
3. `test_can_continue`:
   - Add assertion: `can_continue(state)` is `False` when `state["phase"] == PHASE_SUMMARY`.
4. `test_all_transition_phases_defined`:
   - Add `PHASE_SUMMARY` to the set of defined phase constants.

*Note: All existing tests in `test_config.py`, `test_entities.py`, `test_grid.py`, `test_sandbags.py`, `test_pathfinding.py`, `test_scoring.py`, `test_flood.py`, `test_level_generator.py`, and `test_baseline.py` remain valid and unchanged.*

---

## 5. Summary-Screen Layout Numbers & Overlap Proof

**Window Dimensions**: $1200 \times 750$ pixels.

### Vertical Budget ($Y$-Coordinates)
| Element | $Y$-Range | Height | Description |
|---|---|---|---|
| Window Top Margin | $0 - 39$ | 40px | Empty spacing |
| Title | $40 - 80$ | 40px | `MISSION COMPLETE - FINAL SUMMARY` (42pt font) |
| Subtitle | $95 - 125$ | 30px | `All areas secured! Evacuation successful.` (24pt font) |
| Header Divider | $145 - 147$ | 2px | Horizontal rule above table |
| Table Header | $155 - 190$ | 35px | Column headers |
| Level 1 Row | $200 - 240$ | 40px | Level 1 metrics |
| Level 2 Row | $245 - 285$ | 40px | Level 2 metrics |
| Level 3 Row | $290 - 330$ | 40px | Level 3 metrics |
| Table Bottom Divider | $340 - 342$ | 2px | Horizontal rule below table |
| Total Score Heading & Value | $365 - 425$ | 60px | `TOTAL SCORE: 525` (56pt font, gold/green) |
| Total People Saved Readout | $440 - 475$ | 35px | `People Saved: 90 / 90` (30pt font) |
| Sandbag Efficiency Readout | $490 - 525$ | 35px | `Sandbag Efficiency: 15 / 105 (14.3% saved)` (28pt font) |
| Efficiency Note / Feedback | $540 - 565$ | 25px | Strategic rating commentary (22pt font) |
| Play Again Button | $630 - 685$ | 55px | Rect `(475, 630, 250, 55)` |
| Window Bottom Margin | $686 - 750$ | 65px | Empty spacing |

### Horizontal Budget ($X$-Coordinates)
Table width = $900$px, centered with $150$px margins:
- Table Start: $X = 150$, Table End: $X = 1050$.
- Column 1 (`Level`): $X \in [150, 270]$ ($120$px)
- Column 2 (`Saved / Total`): $X \in [270, 450]$ ($180$px)
- Column 3 (`Sandbags Used`): $X \in [450, 630]$ ($180$px)
- Column 4 (`Pop Score`): $X \in [630, 770]$ ($140$px)
- Column 5 (`Bonus`): $X \in [770, 890]$ ($120$px)
- Column 6 (`Score`): $X \in [890, 1050]$ ($160$px)

**Overlap Proof**: Every vertical band has a positive gap ($> 10$px) from the preceding band. All horizontal column intervals partition $[150, 1050]$ with zero overlap. Everything fits comfortably inside $1200 \times 750$.

---

## 6. Main.py Unified Level Loading & Refactoring

### The Single Loading Function: `load_level(level_num)`
Replaces all scattered calls to `generate_level`, `calculate_baseline_sandbags`, `calculate_sandbag_budget`, and state initialization:
```python
def load_level(level_num):
    grid_data, entities_data, baseline_val, budget = campaign.prepare_level(level_num)
    new_state = game.create_game_state()
    print(f"Level {level_num}: baseline {baseline_val}, budget {budget}")
    return grid_data, entities_data, budget, new_state
```

### Replaced Locations in `main.py`:
1. **Startup**:
   - Remove `from config import CURRENT_LEVEL`.
   - Initialize `camp = campaign.create_campaign(start_level=1)`.
   - Call `game_grid, entities_list, total_budget, state = load_level(camp["level"])`.
2. **Continue Button in Results Phase**:
   - Replace placeholder string with:
     ```python
     outcome = campaign.complete_level(camp, state)
     if outcome == "next_level":
         game_grid, entities_list, total_budget, state = load_level(camp["level"])
         selected_cell = None
         tool_active = False
         flood_start_ms = 0
         flood_steps = []
         message_text = f"Loaded Level {camp['level']} - {LEVEL_NAMES[camp['level']]}"
         message_start_time = pygame.time.get_ticks()
     elif outcome == "summary":
         game.show_summary(state)
     ```
3. **Summary Phase & Play Again**:
   - In `MOUSEBUTTONDOWN`: If `state["phase"] == PHASE_SUMMARY` and `play_again_btn_hovered`:
     ```python
     camp = campaign.create_campaign(start_level=1)
     game_grid, entities_list, total_budget, state = load_level(camp["level"])
     selected_cell = None
     tool_active = False
     flood_start_ms = 0
     flood_steps = []
     message_text = "New campaign started!"
     message_start_time = pygame.time.get_ticks()
     ```
4. **Debug Keys 1, 2, 3**:
   - Guard with `if config.DEBUG_LEVEL_KEYS:`.
   - When True, starts a fresh campaign at chosen level and loads it via `load_level`. When False, keys do nothing.
5. **Top Panel & Results Panel Calls**:
   - Pass running score `sum(r["final_score"] for r in camp["level_results"].values())` and `camp["level"]` to `interface.draw_panels`.
   - Pass dynamic continue label (`BTN_SUMMARY_LABEL` if `is_last_level(camp)` else `BTN_CONTINUE_LABEL`) to `draw_results_panel`.

---

## 7. Headless Smoke Test Setup (`tests/test_interface_smoke.py`)

Headless tests will run under pytest with dummy video driver:
```python
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"
import pygame
pygame.init()
```
- A dummy surface `screen = pygame.Surface((1200, 750))` is initialized once.
- Fonts are instantiated with `pygame.font.Font(None, size)`.
- Tests invoke:
  1. `test_smoke_planning_phase`: `draw_grid`, `draw_cell_labels`, `draw_coordinates`, `draw_panels`, `draw_legend`, `draw_button`.
  2. `test_smoke_confirm_dialog`: `draw_confirm_dialog`.
  3. `test_smoke_flood_animation`: `draw_flood` (steps 0, 15, 30), `draw_flooded_buildings`, `draw_flood_banner`.
  4. `test_smoke_results_panel`: `draw_results_panel` with passed and failed breakdowns, with continue button labeled for next level and final summary.
  5. `test_smoke_final_summary`: `draw_final_summary` with a 3-level summary, 1-level summary, and empty summary.
  6. `test_smoke_config_symbols_exist`: audits that all symbols imported in `interface.py` and `main.py` exist in `config.py`.

---

## 8. Each New Test and What It Checks

### `tests/test_campaign.py` (17 tests)
1. `test_create_campaign`: Dict has exact keys `level` and `level_results`, starts at 1, empty results; levels 0 and 4 raise `ValueError`.
2. `test_prepare_level`: Returns 4-tuple, `budget == baseline + SANDBAG_MARGIN`, counts match `LEVEL_BUILDINGS`, population matches; levels 0 and 4 raise `ValueError`.
3. `test_prepare_level_determinism`: Same level called twice produces identical entities, baseline, and budget.
4. `test_prepare_level_difficulty`: Confirms building counts 7 < 9 < 11 and population 20 < 30 < 40 across levels 1..3.
5. `test_record_level_result_copy`: Stored breakdown is a deep copy; modifying input dict does not alter campaign storage.
6. `test_record_level_result_validation`: Raises `ValueError` if `passed` is False or if level was already recorded; campaign unchanged on error.
7. `test_complete_level_next_level`: Passed Level 1 increments level to 2, stores result, returns `"next_level"`.
8. `test_complete_level_summary`: Passed Level 3 keeps level at 3, stores result, returns `"summary"`.
9. `test_complete_level_invalid_states`: Raises `ValueError` (campaign untouched) if phase is planning, confirming, flooding, summary, or if not passed.
10. `test_is_last_level_and_complete`: Verifies boolean helpers return correct values at each stage.
11. `test_build_final_summary_full`: 3-level summary sums match hand-calculated numbers; rows in order; efficiency percentage rounded to 1 decimal.
12. `test_build_final_summary_partial_and_empty`: 1-level summary and 0-level summary work without division-by-zero (`efficiency_percent == 0.0`).
13. `test_full_headless_playthrough`: End-to-end simulation of 3 levels using baseline routes; verifies final score equals $450 + 3 \times \text{SANDBAG\_MARGIN} \times \text{EFFICIENCY\_BONUS\_PER\_SANDBAG} = 525$.
14. `test_fail_then_retry`: Failed confirmation raises on `complete_level`; retry preserves layout and budget; campaign untouched.
15. `test_pass_then_retry_then_fail`: Passing without clicking Continue records nothing.
16. `test_restart_independence`: New campaign is independent of old one; Level 1 seed gives identical layout.
17. `test_sandbag_margin_monkeypatch`: Monkeypatching `SANDBAG_MARGIN` dynamically adjusts prepared budgets.

### `tests/test_game.py` Additions (3 tests)
18. `test_show_summary_valid`: In results phase with passed breakdown, transitions phase to `PHASE_SUMMARY`.
19. `test_show_summary_invalid`: Outside results phase or with unpassed breakdown, raises `ValueError` and leaves state unchanged.
20. `test_summary_phase_restrictions`: In summary phase, `is_editing_allowed` and `can_continue` are False; `retry_level` raises `ValueError`.

---

## 9. Ambiguities and Conflicts

1. **D7 vs. Level 3 Continue Action**:
   Decision D7 states: *"Continue to Next Level appears ONLY if ALL people in the level were saved."*
   On Level 3, there is no next level; continuing leads to the Final Summary. The spec resolves this cleanly by displaying "VIEW FINAL SUMMARY" on Level 3 while strictly retaining the D7 rule (only available if all people were saved).
2. **`CURRENT_LEVEL` Constant**:
   Previously, `config.CURRENT_LEVEL = 1` was imported by `interface.py` and `main.py`. In F10, active level is driven dynamically by `campaign["level"]`. `CURRENT_LEVEL` is retained in `config.py` as a legacy constant to prevent breaking any early external references.

---

## 10. Risks and Mitigations

| Risk | Mitigation |
|---|---|
| **Zero-division in summary efficiency calculation** on empty or 0-budget campaigns. | Explicitly guard: `100.0 * remaining / allocated if allocated > 0 else 0.0`. |
| **State pollution across levels** (e.g. leftover tool toggle, hover/selected cells, message timers). | Unified `load_level()` explicitly resets all ephemeral UI and tool state upon loading any level. |
| **Accidental mutation of campaign results**. | `record_level_result` explicitly stores `copy.deepcopy(breakdown)`. |
| **Window layout crowding in final summary**. | Complete layout coordinate audit (§5) proves all table rows and summary widgets fit cleanly within 1200 x 750 with comfortable margins. |

