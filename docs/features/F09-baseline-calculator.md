# F09: Baseline Sandbag Calculator (Greedy Shortest-Path Heuristic)

## Goal
Calculate `baseline_sandbags`, a number of sandbags that is guaranteed to connect every
building to the shelter, and set each level's budget to `baseline + SANDBAG_MARGIN` (D2).
Shared route sections must be counted once, not once per building. The student must be able
to explain: why summing every building's own distance would be wrong, how the greedy
nearest-building loop works, why the result is an upper bound and not always the true
minimum, and why that still guarantees the level is solvable.

## Context
F00 to F08 are done. Read CLAUDE.md, docs/DECISIONS.md and the existing files (config.py,
grid.py, entities.py, sandbags.py, pathfinding.py, scoring.py, level_generator.py,
game.py, interface.py, main.py) first. Rules that apply here:
- Pure logic must not import pygame. `baseline.py` is pure logic.
- D2: baseline comes from a greedy shortest-path heuristic (NOT an exact Steiner tree).
  `total_sandbags = baseline_sandbags + SANDBAG_MARGIN` for ALL levels, no per-level change.
- D3: adjacent buildings link directly, and connected buildings relay the network. A
  building next to the network needs 0 sandbags.
- Connectivity is 4-direction only, using `DIRECTIONS`.
- SPEC 6.1: shared route sections must not be counted twice.
- The grid is the single source of truth. The baseline calculation must not modify the grid
  or the entities.

## Scope: files to create / change
- CREATE `baseline.py`: pure logic, NO pygame import
- CREATE `tests/test_baseline.py`: pytest tests
- CHANGE `main.py`: compute the budget when a level is generated and use it instead of
  `TEST_SANDBAG_BUDGET`; print the baseline and budget to the terminal
- CHANGE `config.py`: comment updates only (see below)

Do NOT change game.py, scoring.py, pathfinding.py, flood.py, level_generator.py, sandbags.py
or interface.py. Do NOT add a route overlay, menu or level progression.

## The algorithm (greedy shortest-path heuristic)
1. `network` = a set holding the shelter's cell. `unconnected` = the set of all building
   cells. `route` = an empty list of sandbag cells.
2. Repeat while `unconnected` is not empty:
   a. Run a BFS that starts from ALL cells in `network` at once and expands only through
      EMPTY grid cells that are not already in the network.
   b. Stop at the first time the search is next to a cell in `unconnected`. That building
      is the nearest one.
   c. Walk back through the parent links to the network. The empty cells on that walk are
      the new sandbags, in order from the network outward. (If the building is already
      touching the network, this list is empty: cost 0.)
   d. Add the new sandbag cells to `route` and to `network`. Add the reached building to
      `network` and remove it from `unconnected`.
3. `baseline_sandbags = len(route)`.
Because the network keeps growing, later buildings can attach to earlier sandbags and
earlier buildings. That is how shared sections are counted once.

## Requirements

### baseline.py (pure logic, no pygame)
Keep names simple; the plan may adjust them. Each function gets a docstring with a
one-line example, and the BFS gets step-by-step comments.
- `bfs_to_nearest_target(grid, sources, targets)`: the BFS described in step 2.
  - `sources` and `targets` are sets of `(row, col)`.
  - Initialise the queue from `sorted(sources)` so the result is deterministic.
  - Expand neighbours in `DIRECTIONS` order and use a parent dictionary.
  - Returns `(sandbag_cells, reached_target)`, where `sandbag_cells` is the list of empty
    cells to fill (possibly empty) and `reached_target` is the `(row, col)` of the building
    found. Returns `None` if no target can be reached.
  - Use `collections.deque` or a list with an index pointer (the plan decides and explains).
  - Uses `grid.in_bounds` with the grid's own size, so negative indexes never wrap.
- `calculate_baseline_route(grid, entities)`: runs the loop above and returns the `route`
  list. Raises `ValueError` if there is no shelter, or if the grid already contains any
  sandbag cell (the baseline is defined for a fresh level). If the BFS ever returns `None`
  while buildings remain, raise `RuntimeError` with a clear message (a safety net that
  should be impossible).
- `calculate_baseline_sandbags(grid, entities)`: `len(calculate_baseline_route(...))`.
- `calculate_sandbag_budget(baseline)`: `baseline + SANDBAG_MARGIN`, read from config (so a
  test can change it). Raises `ValueError` if `baseline` is negative.
- `route_connects_everything(grid, entities, route)`: a verification helper. Works on COPIES
  (a copied grid and `copy.deepcopy` of the entities), sets every route cell to
  `"sandbag"`, calls `evaluate_connectivity`, and returns True only if every non-shelter
  building is connected. The original grid and entities must stay exactly as they were
  (including the `"connected"` flags).

### main.py behaviour
- Each time a level is generated (at start and in the temporary debug keys 1, 2, 3), compute
  `baseline = calculate_baseline_sandbags(grid, entities)` and
  `total_budget = calculate_sandbag_budget(baseline)`. Keep `total_budget` in a variable in
  main.py (NOT in the game state).
- Everything that used `TEST_SANDBAG_BUDGET` in main.py now uses `total_budget`: the counter
  in the top panel, placement, the dialog's "Sandbags left", and `confirm_routes`. The plan
  must list every place.
- Print one line to the terminal per generated level, for example
  `Level 2: baseline 17, budget 22`. Add a comment: temporary debug output.
- Retry does not recompute anything (same layout, same budget). Starting the game twice
  gives the same budgets (same seeds).
- The player is NOT shown the baseline anywhere in the interface.

### config.py comment updates
- `TEST_SANDBAG_BUDGET`: comment says it is now used only by tests, not by main.py.
- `SANDBAG_MARGIN`: comment says the budget formula lives in
  `baseline.calculate_sandbag_budget`.

## Acceptance criteria
- [ ] `baseline.py` has no pygame import. It never changes the grid or entities.
- [ ] Starting the game prints the baseline and budget for Level 1. Pressing 2 and 3 prints
      them for Levels 2 and 3. The numbers are the same on every run.
- [ ] The top panel shows `Sandbags: <budget> / <budget>` and the budget equals baseline + 5.
- [ ] Shared route sections are counted once (the shared-trunk tests below pass).
- [ ] Placing exactly the baseline route (see tests) and confirming saves everyone, passes
      the level and leaves exactly 5 sandbags.
- [ ] Retry keeps the same budget and layout.
- [ ] `TEST_SANDBAG_BUDGET` is no longer used in main.py.
- [ ] `pytest` passes, including all earlier tests.

## Tests (tests/test_baseline.py, no pygame window)
Use full-size grids from `create_grid(ROWS, COLS)` and `place_entity`, with a few buildings
each. All expected numbers below are worked out by hand.
1. Shelter only, no buildings: baseline 0, route `[]`.
2. A building directly next to the shelter: baseline 0 (D3).
3. Shelter (5,10), house (5,15): baseline 4, and the route cells are exactly (5,11) to (5,14).
4. Diagonal: shelter (5,10), house (6,11): baseline 1, and the route cell is (5,11) or (6,10).
5. Collinear chain: shelter (5,10), houses (5,15) and (5,20): baseline 8, not 13 (the sum of
   independent distances).
6. Shared trunk: shelter (5,5), houses (5,15) and (5,17): baseline 10, not 20.
7. Branch: shelter (5,10), houses (5,15) and (2,13): baseline 6, and the route contains
   (4,13) and (3,13).
8. Relay (D3): shelter (5,10), houses (5,15) and (5,16) next to each other: baseline 4.
9. `bfs_to_nearest_target` on its own: returns the nearest of two targets, an empty list when
   the target touches a source, and `None` when targets is empty.
10. Route properties on several layouts: no duplicate cells, every cell was empty in the
    original grid, none is a building or the shelter, `len(route) == baseline`.
11. `route_connects_everything` is True for the baseline route on every test layout, False
    for an empty route when no building touches the shelter, and leaves the grid and the
    entities (including every `"connected"` flag, still None) unchanged. Compare copies.
12. Upper-bound check: for the TEST_LAYOUT and for generated levels, the baseline is less than
    or equal to the sum, over all buildings, of the direct cost from the shelter alone
    (`bfs_to_nearest_target` with only the shelter as source and only that building as
    target). Add a comment explaining why this must hold for the greedy method.
13. Determinism: the same grid twice gives the same route. Reversing the order of the entities
    list gives the same route.
14. Errors: a grid with no shelter raises `ValueError`; a grid that already contains a sandbag
    cell raises `ValueError`. After a failure, the grid is unchanged.
15. `calculate_sandbag_budget(10) == 10 + SANDBAG_MARGIN`; `monkeypatch` changes the margin
    and the budget follows; a negative baseline raises `ValueError`.
16. End to end for each level 1, 2, 3 using `generate_level` with the default seed: compute
    the route and budget, place every route cell with `place_sandbag` using that budget
    (all placements succeed), run `evaluate_connectivity` and `build_score_breakdown`:
    `passed` is True, saved equals total population, `sandbags_remaining == SANDBAG_MARGIN`,
    and `efficiency_bonus == SANDBAG_MARGIN * EFFICIENCY_BONUS_PER_SANDBAG`.
17. Stress: for each level and seeds 0 to 199, `generate_level` then the route: it connects
    everything (`route_connects_everything`), `len(route)` equals the baseline, and no
    `RuntimeError` or `ValueError` occurs.
18. Budget never blocks the baseline: with the budget from test 16, placing one more sandbag
    than the budget still raises `ValueError` (the F03 rule still holds).

## Python concepts demonstrated
Breadth-first search with a queue, multi-source search, parent dictionaries and path
reconstruction, sets and sorting for deterministic behaviour, greedy algorithms,
upper-bound reasoning, deep copies to avoid changing data, end-to-end testing.

## Out of scope
Exact minimum (Steiner tree) solving, showing the baseline route to the player, any
interface change, changing the margin per level (D6), level progression and the final
summary (F10), menu (F11), changes to the generator, scoring or flood.

## End-of-feature report (required)
What was built, important code sections (especially `bfs_to_nearest_target` and the greedy
loop, explained with a small worked example showing how a shared section is counted once),
why the result is an upper bound and not the exact minimum, a table of baseline and budget
for Levels 1, 2 and 3 over seeds 0 to 199 (smallest, average and largest baseline per level),
Python concepts used, how to run and test it, known limitations (the heuristic can
overestimate by up to about 2x, so a skilled player may beat the baseline and the Level 3
budget may feel generous), then STOP.