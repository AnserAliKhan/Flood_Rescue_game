# F07: Flood Animation (Driven by the Already-Computed Result)

## Goal
After the player confirms, show a flood sweeping across the grid. Water covers every cell
that is NOT part of the shelter's connected network. Safe buildings and their sandbag
routes stay dry. Unconnected buildings turn red when the water reaches them. When the
animation ends (or the player skips it), the results panel from F06 appears. The student
must be able to explain why the animation cannot change the score: the backend result is
stored first, and the animation only reads it.

## Context
F00 to F06 are done. Read CLAUDE.md, docs/DECISIONS.md and the existing files (config.py,
grid.py, entities.py, sandbags.py, pathfinding.py, scoring.py, game.py, interface.py,
main.py) first. Rules that apply here:
- Pure logic must not import pygame. `flood.py` and `game.py` are pure logic.
- SPEC 8.2: the backend determines the result first. The animation displays it. The
  animation must never alter the grid, the entities, the breakdown or the connectivity.
- F04: `evaluate_connectivity` returns the set of reached cells. That set is the "safe
  set". A cell is safe if it is in that set.
- F06 transition table has a comment saying F07 adds a "flooding" phase by editing it.
- The budget is still the temporary `TEST_SANDBAG_BUDGET`. Level is still `CURRENT_LEVEL`.

## Definition: flooded cells
A cell is FLOODED if it is NOT in the safe set. That includes:
- empty cells
- unconnected buildings
- sandbags that are not linked to the shelter's network (they protect nobody)
The shelter, connected buildings and connected sandbags are never flooded.

## Scope: files to create / change
- CREATE `flood.py`: pure logic, NO pygame import
- CREATE `tests/test_flood.py`: pytest tests
- CHANGE `config.py`: new phase constant, updated transition table, timing and colour
  constants, new message text
- CHANGE `game.py`: store the safe set, route `confirm_routes` into the new phase, add
  `finish_flood`, reset the safe set on retry
- CHANGE `tests/test_game.py`: update the tests affected by the new phase (listed below)
- CHANGE `interface.py`: draw water, red tint on flooded unconnected buildings, flooding
  banner and skip hint
- CHANGE `main.py`: start the timer, run the animation each frame, skip handling

Do NOT create other modules. No levels, menu, sound or particle effects.

## Requirements

### State changes (game.py and config.py)
- New phase constant `PHASE_FLOODING = "flooding"`.
- `ALLOWED_TRANSITIONS` becomes:
  ```
  "planning":   ["confirming"],
  "confirming": ["planning", "flooding"],
  "flooding":   ["results"],
  "results":    ["planning"],
  ```
  Update the explanatory comment (F07 has now added the phase).
- The state dictionary gets a third key. Its keys are exactly `"phase"`, `"breakdown"`,
  `"safe_cells"`. `safe_cells` is `None` until confirm, then the set returned by
  `evaluate_connectivity`.
- `confirm_routes(state, grid, entities, total_budget)` keeps its order (validate, evaluate,
  score) and now: stores the breakdown, stores the safe set in `state["safe_cells"]`, then
  changes the phase to **flooding** (not results). It still returns the breakdown. If any
  step raises, the phase stays "confirming" and BOTH `breakdown` and `safe_cells` stay None.
- NEW `finish_flood(state)`: only valid in the flooding phase (else `ValueError`). Changes
  the phase to results. Changes nothing else. Used both when the animation ends and when
  the player skips it.
- `retry_level` additionally resets `state["safe_cells"]` to None.
- `can_continue` is unchanged (results phase only).

### flood.py (pure logic, no pygame)
Keep names simple; the plan may adjust them. Each function gets a docstring with a
one-line example.
- `get_flooded_cells(grid, safe_cells)`: returns the set of `(row, col)` positions of every
  cell not in `safe_cells`. Uses nested loops over the grid. Does not modify anything.
- `compute_flood_steps(grid, safe_cells)`: returns a list with exactly `COLS` items.
  Item `i` is the list of flooded cells in column `i` (the wave reaches column 0 first,
  column `COLS - 1` last). A column can have an empty list. Together the lists contain
  every flooded cell exactly once and no safe cell.
- `current_step(elapsed_ms, step_ms)`: how many steps have been revealed. Integer division,
  never negative (a negative elapsed time gives 0).
- `cells_flooded_at(steps, step_count)`: returns the set of cells in the first `step_count`
  items of `steps`. `step_count` larger than the list length is allowed and returns all
  flooded cells. 0 returns an empty set.
- `is_flood_finished(elapsed_ms, step_ms, total_steps, hold_ms)`: True once the whole
  sweep plus the end hold time has passed.
Timing values are parameters, so the tests do not depend on config. No clock is read
inside flood.py. main.py reads the time and passes it in.

### config.py additions (each with a comment)
- `PHASE_FLOODING`, updated `ALLOWED_TRANSITIONS`
- `FLOOD_STEP_MS = 60` (time between columns; the sweep takes 30 x 60 ms = 1.8 s)
- `FLOOD_END_HOLD_MS = 800` (pause after the last column before results appear)
- Colours: water (semi-transparent blue, with an alpha value), water front highlight,
  unconnected-building flooded tint (red, may reuse the F06 unsafe colour)
- Message texts: flooding banner (for example "THE FLOOD IS COMING..."), skip hint
  ("Press SPACE or click to skip")

### interface.py additions (Pygame only, never modifies game data)
- `draw_flood(screen, flooded_cells, ...)`: draws a semi-transparent water layer over every
  cell in `flooded_cells`. Efficient: draw onto one transparent surface or reuse one small
  cell-sized surface, not 300 new surfaces each frame. Water is drawn ABOVE empty cells,
  sandbags and buildings, so flooded sandbags and unconnected buildings visibly sink.
- The wave front (the most recently revealed column) may be drawn slightly brighter.
- `draw_flooded_buildings(screen, entities, flooded_cells, ...)`: red tint or outline on
  every non-shelter building whose cell is in `flooded_cells`. Connected buildings get no
  highlight during the flooding phase (green appears in the results phase, as in F06).
- Flooding phase UI: top panel shows `Phase: Flooding`; the bottom panel replaces the
  buttons and legend with the flooding banner and the skip hint. No clickable game buttons.
- In the results phase the water stays visible on all flooded cells (the final picture),
  together with the F06 green/red building highlights.
- Draw order: grid cells, labels, water, building highlights, coordinates, panels. The plan
  must state the final order.

### main.py behaviour
- When `confirm_routes` succeeds, record the start time in a variable in main.py (for
  example `flood_start_ms = pygame.time.get_ticks()`). This variable is NOT stored in the
  game state.
- Each frame in the flooding phase:
  1. `elapsed = now - flood_start_ms`
  2. `steps_done = current_step(elapsed, FLOOD_STEP_MS)`
  3. `flooded_now = cells_flooded_at(steps, steps_done)`
  4. draw the grid with `flooded_now`
  5. if `is_flood_finished(...)`, call `finish_flood(state)`
- `steps` is computed ONCE when the flooding phase starts (not every frame) from
  `compute_flood_steps(grid, state["safe_cells"])`.
- Input during flooding: SPACE or any mouse click calls `finish_flood` immediately (skip).
  ESC exits the program (as in planning and results). Sandbag placement, tool, Reset,
  confirm and retry are all ignored. Closing the window exits cleanly.
- In results: flooded cells = `get_flooded_cells(grid, state["safe_cells"])`, drawn
  instantly (no animation). Retry clears all water (the safe set is None again).
- Wrap game.py and flood.py calls in try/except for `ValueError` and show the message
  instead of crashing.
- F01 to F06 behaviour outside flooding is unchanged.

## Acceptance criteria
- [ ] Clicking YES in the dialog starts a visible water sweep from the left edge to the
      right edge, about 2 seconds long, then the results panel appears.
- [ ] Cells in the connected network (shelter, connected buildings, connected sandbags)
      never get water. Every other cell does.
- [ ] A sandbag that is not linked to the shelter gets flooded. An unconnected building
      turns red when the water reaches it.
- [ ] SPACE or a click during the flood skips straight to the results. The numbers are
      identical to a run without skipping.
- [ ] The score breakdown shown in the results is identical whether the animation was
      watched, skipped, or (in a test) never ran.
- [ ] During flooding, no sandbag can be placed or removed and no button works.
- [ ] After the animation, the results show water on flooded cells plus green/red buildings.
- [ ] Retry returns to planning with a clean board: no water, no red or green, same
      buildings in the same places, same layout (D4).
- [ ] `flood.py` and `game.py` have no pygame import. The timer value is not stored in the
      game state.
- [ ] The frame rate stays smooth during the animation (no 300 surfaces created per frame).
- [ ] `pytest` passes, including all earlier tests (with the updated F06 ones).

## Tests (tests/test_flood.py, no pygame window)
Use small hand-made grids with `create_grid`, `place_entity` and sandbags, and call
`evaluate_connectivity` to get the safe set.
1. `get_flooded_cells` returns all cells except the safe set: sizes add up to
   `ROWS * COLS`, and the two sets do not overlap.
2. With no sandbags, only the shelter is safe, so 299 cells are flooded.
3. A building connected through sandbags is not flooded. An unconnected building is.
4. A disconnected sandbag island IS flooded.
5. `compute_flood_steps` returns exactly `COLS` lists. Every flooded cell appears exactly
   once. No safe cell appears. Every cell in item `i` has column `i`.
6. `current_step`: 0 at 0 ms, 0 just before `step_ms`, 1 at `step_ms`, correct at larger
   times, and 0 for a negative elapsed time.
7. `cells_flooded_at(steps, 0)` is empty. With `COLS` or more it equals
   `get_flooded_cells`. With a middle value, only cells in columns below that value
   appear. The result never shrinks as the step count grows.
8. `is_flood_finished` is False before `COLS * step_ms + hold_ms` and True from that time.
9. Purity: `get_flooded_cells`, `compute_flood_steps` and `cells_flooded_at` leave the grid,
   the entities and the safe set exactly as they were (compare copies).
10. The animation cannot change the result: build a score breakdown, run the full
    functions of flood.py on the same data, then compare with a breakdown built again
    afterwards. They are identical, and every entity `"connected"` flag is unchanged.
11. The shelter cell is never in any flooded set.

## Tests: changes to tests/test_game.py
The plan must list which existing F06 tests change. Expected changes:
- Legal transitions: confirming to flooding and flooding to results are legal. Confirming
  directly to results is now ILLEGAL. Planning to flooding is illegal.
- `confirm_routes` tests that expected phase results now expect phase flooding, with the
  breakdown and the safe set stored.
- `confirm_routes` failure test (no shelter): phase "confirming", breakdown None,
  `safe_cells` None.
- State keys test: exactly `"phase"`, `"breakdown"`, `"safe_cells"`.
- `retry_level` tests and the full-cycle test now go plan, confirm, flooding,
  `finish_flood`, results, retry.
- `can_continue` is False in the flooding phase.
- `is_editing_allowed` is False in the flooding phase.
- Every phase in `ALLOWED_TRANSITIONS` is a defined constant (include flooding).
New tests:
- `finish_flood` outside flooding raises `ValueError`. Inside flooding it sets results and
  changes nothing else (breakdown and safe set unchanged).
- `retry_level` resets `safe_cells` to None.
- `retry_level` from the flooding phase raises `ValueError` (retry only from results).

## Python concepts demonstrated
Extending a state machine by editing a lookup table, sets and set operations (difference),
lists of lists built with loops, integer division for time-to-step conversion, passing time
as a parameter to keep logic testable, separating data from presentation, transparency
and draw order in Pygame, comparing before/after copies to prove nothing changed.

## Out of scope
Level generation and switching, menus, sound effects, particle or wave graphics beyond
simple tinted cells, animating people or sandbags, a flood that starts at different edges,
random flood patterns, the real sandbag budget, the final game summary.

## End-of-feature report (required)
What was built, important code sections (especially `compute_flood_steps`,
`confirm_routes` and why the safe set is stored before the animation, and how the frame
loop turns elapsed time into a step), Python concepts used, how to run and test it, which
F06 tests were changed and why, known limitations (the sweep is a simple left-to-right
column wave, not a physical simulation), then STOP.
