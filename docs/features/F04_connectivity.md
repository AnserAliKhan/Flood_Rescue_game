# F04: Recursive DFS Connectivity from the Shelter

## Goal
Write the algorithm that decides which buildings are connected to the shelter, using a
recursive depth-first search (DFS). It is pure logic with unit tests and no GUI. One
traversal starting at the shelter must identify every connected building. The student
must be able to explain recursion here: the base cases, the recursive case, and why a
"visited" set prevents infinite loops.

## Context
F00 to F03 are done. Read CLAUDE.md, docs/DECISIONS.md and the existing files
(config.py, grid.py, entities.py, sandbags.py) first. Rules that apply here:
- Pure logic must not import pygame.
- Connectivity is 4-direction only (up, down, left, right). Never diagonal.
- The backend decides the result; the animation (F07) only displays it later.
- D3 overrides SPEC 8.1: adjacent buildings link directly, and connected buildings relay
  the network to other buildings.

## Connectivity rule (the precise definition used in this feature)
A cell is TRAVERSABLE if it holds a sandbag, a house, a school, a hospital or the
shelter. An EMPTY cell is never traversable. The search starts at the shelter and moves
only up, down, left or right between traversable cells. A building is connected if the
search reaches its cell.
Consequences, all intended by D3:
- A building directly next to the shelter is connected with 0 sandbags.
- Two adjacent buildings are linked directly, so a connected building can relay the
  network onward to the next building.
- A diagonal neighbour never counts, even if it is a sandbag.
- Sandbags that are not linked to the shelter's network stay unvisited and save no one.

## Scope: files to create / change
- CREATE `pathfinding.py`: pure logic, NO pygame import
- CREATE `tests/test_pathfinding.py`: pytest tests
- CHANGE `config.py`: only if a shared constant is needed (see DIRECTIONS below)

Do NOT change main.py or interface.py. There is no visual change in this feature. Do NOT
touch scoring, flood animation, game states, the baseline calculator or levels.

## Requirements

### Direction constant
`DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]` meaning up, down, left, right, defined
once (in config.py or at the top of pathfinding.py, the plan decides) with a comment
that diagonals are intentionally absent. Every neighbour calculation uses it. Do not
write four separate hard-coded neighbour blocks.

### pathfinding.py (pure logic, no pygame)
Keep names simple; the plan may adjust them. Each function gets a docstring with a
one-line example and comments explaining the recursion.

- `is_traversable(grid, row, col)`: True if the position is in bounds (reuse
  `grid.in_bounds`, so negative indexes never wrap) and the cell is not `"empty"`.
- `dfs_visit(grid, row, col, visited)`: the RECURSIVE function.
  - Base case 1: not traversable (out of bounds or empty) -> return.
  - Base case 2: `(row, col)` already in `visited` -> return.
  - Recursive case: add `(row, col)` to `visited`, then loop over `DIRECTIONS` and call
    `dfs_visit` on each neighbour.
  `visited` is a Python `set` of `(row, col)` tuples that is modified in place.
- `find_shelter(entities)`: returns the shelter entity dictionary, or raises
  `ValueError` if there is none (reuse `entities.get_entities_by_type`).
- `find_connected_cells(grid, start_row, start_col)`: creates an empty set, calls
  `dfs_visit` once from the start cell, and returns the set of all reached cells.
- `find_connected_cells_iterative(grid, start_row, start_col)`: the same result using a
  loop and an explicit stack (a list) instead of recursion. Used for the comparison in
  the report and as a cross-check in the tests. Keep it short.
- `evaluate_connectivity(grid, entities)`: finds the shelter, runs ONE traversal from it,
  then loops over all entities except the shelter and sets
  `entity["connected"] = True` if its `(row, col)` is in the visited set, otherwise
  `False`. The shelter's own flag is left unchanged. Returns the visited set (the flood
  animation in F07 will need it). Calling it again after the grid changes must give
  fresh, correct flags (no stale values).

### What this feature does NOT decide
No people counting, no score, no per-type totals (F05). No search for "the best route" or
minimum sandbags (F09). Only: which buildings are reachable.

## Acceptance criteria
- [ ] `pathfinding.py` has no pygame import and `main.py` / `interface.py` are unchanged.
- [ ] `dfs_visit` is genuinely recursive (it calls itself) and has the two base cases.
- [ ] Neighbours are generated from `DIRECTIONS` only, so diagonals can never connect.
- [ ] One traversal from the shelter marks every connected building. No per-building
      path searches.
- [ ] A building adjacent to the shelter is connected with zero sandbags.
- [ ] A building separated from the network by one empty cell is NOT connected.
- [ ] Re-running `evaluate_connectivity` after removing a sandbag updates the flags
      correctly.
- [ ] The recursive and iterative versions return identical sets on every test grid.
- [ ] `pytest` passes, including the F00 to F03 tests.

## Tests (tests/test_pathfinding.py, no pygame window)
Build small grids with `create_grid` and `place_entity` / direct cell assignment, so each
test is easy to read. Use the TEST_LAYOUT grid only where stated.
1. `is_traversable`: False for empty cells and out-of-bounds positions (including -1);
   True for sandbag, house, school, hospital and shelter cells.
2. No sandbags at all: with the shelter alone, only the shelter cell is visited and every
   non-adjacent building is `connected == False`.
3. Straight horizontal chain: shelter, sandbags, house in one row -> house connected.
4. Straight vertical chain -> connected.
5. Diagonal only: a house diagonally next to the shelter, or a sandbag diagonal to the
   shelter -> NOT connected.
6. Gap: the same chain with one sandbag missing -> house NOT connected. Placing the
   missing sandbag makes it connected.
7. Building adjacent to the shelter (no sandbags) -> connected (D3).
8. Relay: shelter, sandbags, house A, then house B directly next to A (no sandbags
   between them) -> both connected (D3).
9. Shared route: two houses served by one shared sandbag path -> both connected, and the
   visited set contains each shared sandbag only once.
10. Disconnected sandbag island: a group of sandbags near a house but not touching the
    shelter network -> house NOT connected, and the island cells are not in the visited
    set.
11. Removing one sandbag from a working network (then calling `evaluate_connectivity`
    again) flips the downstream buildings from True to False.
12. Loop and branches: sandbags forming a square ring or a plus shape do not cause an
    infinite loop or a crash, and every cell is visited exactly once.
13. Deep recursion: a snake-shaped sandbag path that visits most of a 10 x 30 grid
    (about 150 or more cells, built with a loop) is fully traversed without a
    `RecursionError`. Write a comment explaining why depth stays safely below Python's
    default limit of 1000.
14. Recursive and iterative versions return equal sets for: the empty grid, the TEST_LAYOUT
    with no sandbags, the snake path, and at least 20 random grids generated with a
    fixed seed (`random.seed(...)`, random cells chosen from sandbag/empty).
15. `find_shelter` raises `ValueError` when there is no shelter.
16. `evaluate_connectivity` leaves the shelter's `"connected"` unchanged, sets every
    other building to exactly True or False (never None), and does not modify the grid.
17. Flags are refreshed: a building set to True stays correct after the network is
    broken and `evaluate_connectivity` runs again.

## Python concepts demonstrated
Recursion (base cases, recursive case, call stack depth), sets and tuples, a constant
list of direction offsets, loops over neighbours, graph traversal on a 2D list, boolean
flags in dictionaries, comparing a recursive and an iterative solution, tests with a
fixed random seed.

## Out of scope
Any GUI change, scoring or counting saved people, minimum-sandbag calculation, BFS
shortest paths, drawing routes, flood animation, game states, confirm button, levels,
random level generation.

## End-of-feature report (required)
What was built, important code sections (especially `dfs_visit` explained step by step
with a small 3 x 3 trace of the calls), a short comparison of recursive DFS vs iterative
DFS vs BFS for this problem (readability, recursion depth limit, and which one is best
for demonstrating recursion in the course), Python concepts used, how to run and test it,
known limitations. Then STOP.