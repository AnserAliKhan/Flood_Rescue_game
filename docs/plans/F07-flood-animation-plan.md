# F07 Flood Animation — Implementation Plan

## 1. Files to create or change

| File | Action | Purpose |
|---|---|---|
| `flood.py` | CREATE | Pure-logic module (no pygame). Computes which cells are flooded, builds the column-by-column step list, converts elapsed time to a step count, and checks whether the animation is finished. |
| `tests/test_flood.py` | CREATE | Pytest suite for every function in flood.py. |
| `config.py` | CHANGE | Add `PHASE_FLOODING`, update `ALLOWED_TRANSITIONS`, add timing constants (`FLOOD_STEP_MS`, `FLOOD_END_HOLD_MS`), add colour constants for water, add message-text constants for the flooding banner and skip hint. |
| `game.py` | CHANGE | Add `"safe_cells"` key to state, route `confirm_routes` into flooding instead of results, add `finish_flood()`, reset `safe_cells` on retry. Import `PHASE_FLOODING`. |
| `tests/test_game.py` | CHANGE | Update existing F06 tests for the new phase flow and add new tests for `finish_flood` and `safe_cells`. |
| `interface.py` | CHANGE | Add `draw_flood()` and `draw_flooded_buildings()`. Add a flooding-phase banner and skip-hint draw. Import new colour/text constants. |
| `main.py` | CHANGE | Record `flood_start_ms` on confirm, compute `steps` once, run per-frame flood logic, handle skip input (SPACE / click), draw water in results phase too. |

---

## 2. Every constant and function

### config.py — new constants

```
PHASE_FLOODING = "flooding"

ALLOWED_TRANSITIONS = {
    PHASE_PLANNING:   [PHASE_CONFIRMING],
    PHASE_CONFIRMING: [PHASE_PLANNING, PHASE_FLOODING],
    PHASE_FLOODING:   [PHASE_RESULTS],
    PHASE_RESULTS:    [PHASE_PLANNING],
}
# The "flooding" phase was added in F07.

FLOOD_STEP_MS    = 60    # ms per column; 30 × 60 = 1.8 s sweep
FLOOD_END_HOLD_MS = 800  # pause after last column before results

COLOR_WATER       = (30, 100, 200, 120)   # semi-transparent blue (RGBA)
COLOR_WATER_FRONT = (60, 140, 240, 160)   # brighter blue for the leading edge
# COLOR_UNSAFE already exists and is reused for flooded buildings

MSG_FLOODING_BANNER = "THE FLOOD IS COMING..."
MSG_FLOODING_SKIP   = "Press SPACE or click to skip"
```

### flood.py — new module (pure logic, no pygame)

```
get_flooded_cells(grid, safe_cells) -> set
    Returns set of (row, col) for every cell NOT in safe_cells.
    Nested loops over grid dimensions.

compute_flood_steps(grid, safe_cells) -> list[list[tuple]]
    Returns a list of COLS items. Item i is a list of (row, col)
    of flooded cells in column i (left-to-right sweep).
    Built with a loop over columns, inner loop over rows.

current_step(elapsed_ms, step_ms) -> int
    Integer division elapsed_ms // step_ms, clamped to >= 0.

cells_flooded_at(steps, step_count) -> set
    Union of the first step_count items in steps.
    step_count clamped to [0, len(steps)].

is_flood_finished(elapsed_ms, step_ms, total_steps, hold_ms) -> bool
    True when elapsed_ms >= total_steps * step_ms + hold_ms.
```

### game.py — changes

```
create_game_state() -> dict
    Returns {"phase": PHASE_PLANNING, "breakdown": None, "safe_cells": None}

confirm_routes(state, grid, entities, total_budget) -> dict
    Steps unchanged: validate shelter, evaluate_connectivity, build_score_breakdown.
    NEW: stores safe set from evaluate_connectivity in state["safe_cells"].
    NEW: transitions to PHASE_FLOODING (not PHASE_RESULTS).
    On failure: phase stays "confirming", breakdown stays None, safe_cells stays None.

finish_flood(state) -> None
    Only valid in PHASE_FLOODING (else ValueError).
    Changes phase to PHASE_RESULTS. Touches nothing else.

retry_level(state, grid, entities) -> None
    Existing behaviour plus: sets state["safe_cells"] = None.
```

### interface.py — new functions

```
draw_flood(screen, flooded_cells, front_col)
    Draws semi-transparent water over every cell in flooded_cells.
    Uses ONE cell-sized RGBA surface, blitted repeatedly (efficient).
    Cells in front_col use COLOR_WATER_FRONT; others use COLOR_WATER.

draw_flooded_buildings(screen, entities, flooded_cells)
    Red outline (COLOR_UNSAFE, width 4) on every non-shelter building
    whose (row, col) is in flooded_cells.

draw_flood_banner(screen, font)
    Draws MSG_FLOODING_BANNER centred in the bottom panel area,
    and MSG_FLOODING_SKIP below it.
```

---

## 3. Transition table and state changes

### New transition table

```
planning   → [confirming]
confirming → [planning, flooding]
flooding   → [results]
results    → [planning]
```

### confirm_routes (success path)

```
confirming
  → validate (1 shelter)
  → visited = evaluate_connectivity(grid, entities)
  → breakdown = build_score_breakdown(grid, entities, budget)
  → state["breakdown"] = breakdown
  → state["safe_cells"] = visited       ← NEW
  → change_phase(state, PHASE_FLOODING) ← CHANGED (was PHASE_RESULTS)
  → return breakdown
```

### confirm_routes (failure path — no shelter or other error)

```
confirming
  → raises ValueError
  → phase stays "confirming"
  → state["breakdown"] stays None
  → state["safe_cells"] stays None      ← NEW guarantee
```

### finish_flood

```
flooding
  → change_phase(state, PHASE_RESULTS)
  → breakdown and safe_cells are NOT touched
```

If called outside flooding: `ValueError`, state unchanged.

### retry_level

```
results
  → clear_sandbags(grid)
  → reset entity "connected" flags to None
  → state["breakdown"] = None
  → state["safe_cells"] = None          ← NEW
  → change_phase(state, PHASE_PLANNING)
```

---

## 4. Existing F06 tests that must change

| Test function | What changes | Why |
|---|---|---|
| `test_initial_state` | Assert `state["safe_cells"] is None` | New key in state dict |
| `test_transitions` | `Confirm → Results` becomes `Confirm → Flooding → Results`. Old `Confirm → Results` directly must raise `ValueError`. Add `Planning → Flooding` as illegal. | Transition table changed |
| `test_editing_allowed` | Add assertion that `is_editing_allowed` is `False` in `PHASE_FLOODING` | New phase |
| `test_confirm_routes_success` | Assert `state["phase"] == PHASE_FLOODING` (not `PHASE_RESULTS`). Assert `state["safe_cells"]` is a set containing the shelter cell `(0,0)`. | confirm_routes now goes to flooding |
| `test_confirm_routes_failure` | Additionally assert `state["safe_cells"] is None` | New key must stay None on failure |
| `test_can_continue` | Add check: `can_continue` is `False` when phase is `PHASE_FLOODING` | New phase |
| `test_retry_level` | Assert `state["safe_cells"] is None` after retry | New key reset |
| `test_full_cycle` | Insert `finish_flood(state)` between `confirm_routes` and the results assertions, for both runs. Import `finish_flood` and `PHASE_FLOODING`. | Flow now requires the flooding→results step |

---

## 5. Per-frame logic in main.py (flooding phase)

### Variables in main.py (not in game state)

```python
flood_start_ms = 0       # set when confirm_routes succeeds
flood_steps = []         # computed once from compute_flood_steps
```

### When confirm_routes succeeds (in the confirming click handler)

```
breakdown = game.confirm_routes(state, game_grid, entities_list, budget)
flood_start_ms = pygame.time.get_ticks()
flood_steps = flood.compute_flood_steps(game_grid, state["safe_cells"])
```

### Each frame while state["phase"] == PHASE_FLOODING

```
1.  elapsed = pygame.time.get_ticks() - flood_start_ms
2.  steps_done = flood.current_step(elapsed, FLOOD_STEP_MS)
3.  flooded_now = flood.cells_flooded_at(flood_steps, steps_done)
4.  front_col = steps_done - 1   (for the brighter leading edge, or -1 if 0)
5.  if flood.is_flood_finished(elapsed, FLOOD_STEP_MS, COLS, FLOOD_END_HOLD_MS):
        game.finish_flood(state)
```

### Input during flooding

- **SPACE** or **any mouse click**: call `game.finish_flood(state)` immediately (skip).
- **ESC**: `running = False` (exit).
- **Everything else** (S key, grid clicks, buttons): ignored.

### Final draw order (all phases)

```
1. screen.fill(COLOR_BG)
2. draw_grid(screen, game_grid)              — cell backgrounds
3. draw_cell_labels(screen, game_grid)       — H, S, +, SH, B letters

4. IF flooding phase:
       draw_flood(screen, flooded_now, front_col)
       draw_flooded_buildings(screen, entities_list, flooded_now)
   IF results phase:
       all_flooded = flood.get_flooded_cells(game_grid, state["safe_cells"])
       draw_flood(screen, all_flooded, -1)   — no front highlight
       draw_safe_unsafe(screen, entities_list)  — green/red outlines (F06)

5. draw_coordinates(screen)                  — row/col numbers
6. draw_highlights (hover, selected)         — only in planning

7. draw_panels(...)                          — top panel (shows phase name)

8. IF planning:  draw buttons (Sandbag, Reset, Confirm) + legend
   IF confirming: draw_confirm_dialog(...)
   IF flooding:  draw_flood_banner(screen, font)
   IF results:   draw_results_panel(...) + Retry/Continue buttons

9. draw_message(screen, message_text, font)
10. pygame.display.flip()
```

---

## 6. How water is drawn efficiently

The spec warns against creating 300 surfaces per frame.

**Approach: one reusable cell-sized RGBA surface.**

```
water_cell = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
```

- Created once (at the top of `draw_flood`, or cached as a module-level variable).
- For each cell in `flooded_now`:
  - Fill the surface with `COLOR_WATER` (or `COLOR_WATER_FRONT` if the cell's column equals `front_col`).
  - Blit it at the cell's pixel position.
- Two fills per frame at most (one for normal water, one for front), not 300 surface creations.

This is the same pattern used in `draw_confirm_dialog` for the dimmer overlay, so it's consistent with existing code.

---

## 7. New tests

### tests/test_flood.py

| # | Test name | What it checks |
|---|---|---|
| 1 | `test_flooded_cells_partition` | `get_flooded_cells` + `safe_cells` together cover all `ROWS*COLS` cells, with zero overlap. |
| 2 | `test_no_sandbags_299_flooded` | With only a shelter, 299 cells are flooded (only shelter cell is safe). |
| 3 | `test_connected_building_not_flooded` | A building connected through sandbags is not in the flooded set. An unconnected building is. |
| 4 | `test_disconnected_sandbag_flooded` | A sandbag island not linked to the shelter IS flooded. |
| 5 | `test_compute_flood_steps_structure` | Returns exactly `COLS` lists. Every flooded cell appears exactly once. No safe cell appears. Every cell in item `i` has column `i`. |
| 6 | `test_current_step_values` | 0 at 0 ms, 0 just before `step_ms`, 1 at `step_ms`, correct at larger times, 0 for negative elapsed. |
| 7 | `test_cells_flooded_at_bounds` | `step_count=0` → empty. `step_count >= COLS` → equals `get_flooded_cells`. Middle value → only cells in columns below that value. Result never shrinks as step_count grows. |
| 8 | `test_is_flood_finished_timing` | False before `COLS * step_ms + hold_ms`, True at that time and after. |
| 9 | `test_purity` | `get_flooded_cells`, `compute_flood_steps`, `cells_flooded_at` leave grid, entities, and safe_cells unchanged (compare deep copies). |
| 10 | `test_animation_cannot_change_result` | Build breakdown before flood functions, run all flood functions, build breakdown again. Both breakdowns are identical; every entity `"connected"` flag is unchanged. |
| 11 | `test_shelter_never_flooded` | The shelter cell never appears in any flooded set. |

### tests/test_game.py — new tests added

| # | Test name | What it checks |
|---|---|---|
| 12 | `test_finish_flood_valid` | In flooding phase: sets phase to results. Breakdown and safe_cells are unchanged. |
| 13 | `test_finish_flood_invalid` | Outside flooding: raises `ValueError`, state unchanged. |
| 14 | `test_retry_resets_safe_cells` | After retry, `state["safe_cells"]` is `None`. |
| 15 | `test_retry_from_flooding_invalid` | `retry_level` from flooding raises `ValueError` (retry only from results). |
| 16 | `test_state_keys` | `create_game_state()` keys are exactly `{"phase", "breakdown", "safe_cells"}`. |
| 17 | `test_all_transition_phases_defined` | Every phase in `ALLOWED_TRANSITIONS` (keys and values) is a defined `PHASE_*` constant. |

---

## 8. Ambiguities / potential conflicts

1. **`evaluate_connectivity` return value**: The spec for F07 (line 18) says "F04: `evaluate_connectivity` returns the set of reached cells". The current code in `pathfinding.py` line 106 does `return visited` — this is the set of *all traversable cells* reachable from the shelter (shelter + connected sandbags + connected buildings). This is correct for defining the safe set. **No conflict, just confirming the interpretation: safe = returned set, flooded = everything else.**

2. **Draw order of water vs building highlights in results**: The F07 spec says results shows "water on flooded cells plus green/red buildings" (line 146) and the draw order list (line 110) says "water, building highlights". F06's `draw_safe_unsafe` draws outlines on ALL non-shelter buildings (both connected and unconnected). In results, water will cover unconnected buildings, and then red outlines are drawn on top of the water — this should be visible. Green outlines on connected buildings have no water beneath them. **No conflict, just noting that the red outline must be drawn AFTER the water layer to be visible.**

3. **`interface.py` line 222 uses `config.CURRENT_LEVEL`** but `config` is not imported at the top of `interface.py`. This is a pre-existing bug in `draw_results_panel` — it would crash if actually reached through a clean call path. I will need to fix this (add `import config` or pass the level as a parameter). **Not an F07 issue, but will break during testing. Will fix minimally.**

4. **`main.py` line 228 has a bug**: `draw_button` is called with a missing `text` argument for the Continue button: `interface.draw_button(screen, BTN_CONTINUE_RECT, btn_font, False, cont_btn_hovered)` — the label `BTN_CONTINUE_LABEL` is missing as the second positional arg. **Pre-existing bug. Will fix minimally while editing main.py.**

---

## 9. Risks

| Risk | Mitigation |
|---|---|
| **Recursion depth** in `dfs_visit` on large grids during `evaluate_connectivity` (called before flood). | Already tested in F04 (`test_deep_recursion`). The 30×10 grid is small enough. No change needed. |
| **Frame rate drop** if water drawing is inefficient (300 surfaces per frame). | Use the single-surface-reuse approach described in §6. Only 2 fills + N blits per frame. |
| **Stale `flood_steps`** if the variable is not cleared on retry. | Reset `flood_steps = []` and `flood_start_ms = 0` whenever `retry_level` is called in main.py. |
| **Skipping the flood before any steps are drawn** (player clicks instantly). | `finish_flood` goes straight to results. The breakdown and safe_cells were already computed before the animation started. Scores are correct regardless. |
| **Existing tests break** because `confirm_routes` now goes to flooding, not results. | Update every affected test (§4 above) in the same commit. Run full `pytest` before marking done. |
| **`config` not imported in `interface.py`** (pre-existing, see §8.3). | Fix the import during this feature. |
| **The `draw_button` bug in main.py** (see §8.4). | Fix the missing argument during this feature. |

