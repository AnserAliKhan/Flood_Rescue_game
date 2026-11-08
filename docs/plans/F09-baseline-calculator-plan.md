# F09 Baseline Sandbag Calculator — Implementation Plan

## 1. Files to Create or Change

| File | Action | Purpose |
|---|---|---|
| `baseline.py` | CREATE | Pure-logic module (no pygame). Implements multi-source BFS (`bfs_to_nearest_target`), the greedy shortest-path heuristic loop (`calculate_baseline_route`), baseline counting (`calculate_baseline_sandbags`), budget formula (`calculate_sandbag_budget`), and verification helper (`route_connects_everything`). |
| `tests/test_baseline.py` | CREATE | Pytest test suite covering all 18 test cases (unit BFS, hand-calculated topologies, shared trunks, relay, purity, determinism, upper-bound check, error conditions, end-to-end scoring, and 200-seed stress test). |
| `main.py` | CHANGE | Replace all runtime uses of `TEST_SANDBAG_BUDGET` with dynamically computed `total_budget`. Compute `baseline` and `total_budget` upon initial generation and upon pressing debug keys 1, 2, 3. Print terminal debug line (`Level X: baseline Y, budget Z`). |
| `config.py` | CHANGE | Update comments for `TEST_SANDBAG_BUDGET` (used only for legacy tests, not main.py) and `SANDBAG_MARGIN` (noting formula is in `baseline.py`). |

---

## 2. Every Function (Names and Signatures)

All functions live in `baseline.py` (pure logic, zero pygame imports):

```python
def bfs_to_nearest_target(grid: list[list[str]],
                          sources: set[tuple[int, int]],
                          targets: set[tuple[int, int]]) -> tuple[list[tuple[int, int]], tuple[int, int]] | None:
    """
    Runs a deterministic multi-source BFS starting from all source cells simultaneously.
    Expands through CELL_EMPTY cells in DIRECTIONS order to locate the nearest target.
    Returns (sandbag_cells, reached_target) where sandbag_cells is the list of empty cells
    to pave from the network outward to reached_target. Returns ([], target) if target already
    touches sources (cost 0). Returns None if targets is empty or unreachable.
    Example: bfs_to_nearest_target(grid, {(5, 10)}, {(5, 15)}) -> ([(5, 11), (5, 12), (5, 13), (5, 14)], (5, 15))
    """

def calculate_baseline_route(grid: list[list[str]],
                             entities: list[dict]) -> list[tuple[int, int]]:
    """
    Executes the greedy shortest-path heuristic:
    Starts with network = {shelter_cell} and unconnected = {all building cells}.
    Repeatedly connects the nearest unconnected building to the expanding network.
    Returns the ordered list of all newly paved sandbag cells (shared sections counted once).
    Raises ValueError if no shelter exists or if grid already contains any sandbag cells.
    Raises RuntimeError if any building remains unreachable.
    Example: calculate_baseline_route(grid, entities) -> [(5, 11), (5, 12), (5, 13), (5, 14)]
    """

def calculate_baseline_sandbags(grid: list[list[str]], entities: list[dict]) -> int:
    """
    Returns the total number of sandbags in the baseline route.
    Equivalent to len(calculate_baseline_route(grid, entities)).
    Example: calculate_baseline_sandbags(grid, entities) -> 4
    """

def calculate_sandbag_budget(baseline: int) -> int:
    """
    Calculates the total level sandbag budget using Decision D2: baseline + SANDBAG_MARGIN.
    Raises ValueError if baseline is negative.
    Example: calculate_sandbag_budget(4) -> 9  (since SANDBAG_MARGIN is 5)
    """

def route_connects_everything(grid: list[list[str]],
                             entities: list[dict],
                             route: list[tuple[int, int]]) -> bool:
    """
    Verification helper: creates copies of grid and entities, places sandbags on route cells,
    evaluates connectivity via pathfinding.evaluate_connectivity, and checks if all non-shelter
    buildings are connected. Leaves the original grid and entities completely unchanged.
    Example: route_connects_everything(grid, entities, route) -> True
    """
```

---

## 3. Step-by-Step Description of `bfs_to_nearest_target` and the Greedy Loop

### A. `bfs_to_nearest_target(grid, sources, targets)`
1. **Early Exit**: If `targets` is empty, return `None`.
2. **Deterministic Queue Initialization**:
   - Sort `sources` so starting order is fully deterministic across Python runs.
   - Use `collections.deque(sorted(sources))` for $O(1)$ popleft and append.
   - Maintain `visited = set(sources)`.
   - Maintain `parent = {}` mapping `(r, c) -> predecessor (r, c)`.
3. **Queue Processing**:
   - While `queue` is not empty:
     - Pop `curr = queue.popleft()`.
     - For `(dr, dc)` in `DIRECTIONS` (Up, Down, Left, Right in fixed config order):
       - `nr, nc = curr[0] + dr, curr[1] + dc`
       - If not `in_bounds(nr, nc, len(grid), len(grid[0]))`: continue
       - **Target Found**: If `(nr, nc) in targets`:
         - Stop immediately (nearest building discovered).
         - Reconstruct the path backwards:
           - If `curr in sources`: `curr` is already part of the network, meaning the target directly touches the network. Path is `[]` (Cost-0 building).
           - Otherwise, trace from `curr` backwards using `parent` until reaching a cell that is in `sources`:
             ```python
             path = []
             node = curr
             while node not in sources:
                 path.append(node)
                 node = parent[node]
             path.reverse()  # Order from network outward to target
             ```
         - Return `(path, (nr, nc))`.
       - **Corridor Expansion**: If `grid[nr][nc] == CELL_EMPTY` and `(nr, nc) not in visited`:
         - `visited.add((nr, nc))`
         - `parent[(nr, nc)] = curr`
         - `queue.append((nr, nc))`
4. **Unreachable Exit**: If queue exhausts without finding any target, return `None`.

### B. The Greedy Loop (`calculate_baseline_route`)
1. **Validation**:
   - Find shelter entity. If none or >1, raise `ValueError`.
   - Verify `grid` contains no `"sandbag"` cells (baseline must be calculated on an unpaved board).
2. **State Setup**:
   - `network = {(shelter["row"], shelter["col"])}`
   - `unconnected = {(e["row"], e["col"]) for e in entities if e["type"] != CELL_SHELTER}`
   - `route = []`
3. **Loop while `unconnected` is not empty**:
   - Call `result = bfs_to_nearest_target(grid, network, unconnected)`.
   - If `result is None`: raise `RuntimeError("Unreachable building encountered during baseline calculation.")`.
   - Unpack `new_sandbags, reached_target = result`.
   - For `cell` in `new_sandbags`:
     - If `cell not in network`:
       - `route.append(cell)`
       - `network.add(cell)`
   - Add `reached_target` to `network` (it can now serve as a relay for subsequent buildings per Decision D3).
   - Remove `reached_target` from `unconnected`.
4. Return `route`.

---

## 4. Every Place in `main.py` Using `TEST_SANDBAG_BUDGET` and Its Replacement

Currently, `TEST_SANDBAG_BUDGET` appears in 6 places in `main.py`:

| Location in `main.py` | Current Code | Replacement |
|---|---|---|
| **Import statement (line 5)** | `TEST_SANDBAG_BUDGET` | Remove from import; import `baseline` module instead. |
| **Level initialization (line 39)** | (implicit test budget) | Compute `level_baseline = baseline.calculate_baseline_sandbags(game_grid, entities_list)`<br>`total_budget = baseline.calculate_sandbag_budget(level_baseline)`<br>`print(f"Level {current_level}: baseline {level_baseline}, budget {total_budget}")` |
| **Sandbag placement (line 130)** | `sandbags.place_sandbag(..., TEST_SANDBAG_BUDGET)` | `sandbags.place_sandbag(..., total_budget)` |
| **Route confirmation (line 141)** | `game.confirm_routes(..., TEST_SANDBAG_BUDGET)` | `game.confirm_routes(..., total_budget)` |
| **Top panel readout (lines 204-205)** | `sb_remaining = sandbags.remaining_sandbags(game_grid, TEST_SANDBAG_BUDGET)`<br>`sb_info = f"Sandbags: {sb_remaining} / {TEST_SANDBAG_BUDGET}"` | `sb_remaining = sandbags.remaining_sandbags(game_grid, total_budget)`<br>`sb_info = f"Sandbags: {sb_remaining} / {total_budget}"` |
| **Confirmation dialog (line 297)** | `sb_rem = sandbags.remaining_sandbags(game_grid, TEST_SANDBAG_BUDGET)` | `sb_rem = sandbags.remaining_sandbags(game_grid, total_budget)` |
| **Debug keys 1, 2, 3 (lines 100-110)** | (did not recompute budget) | Recompute `level_baseline`, update `total_budget`, and print `print(f"Level {current_level}: baseline {level_baseline}, budget {total_budget}")`. |

---

## 5. Grid and Pathfinding Size Assumptions

- **`grid.py`**:
  - `create_grid(rows, cols)` takes dimensions as parameters.
  - `get_cell` and `set_cell` determine dimensions via `rows = len(grid)`, `cols = len(grid[0])`.
  - `in_bounds(row, col, rows, cols)` takes dimensions as explicit arguments.
  - Does **not** import or assume global `ROWS` and `COLS`.
- **`pathfinding.py`**:
  - `is_traversable(grid, row, col)` calls `grid_module.in_bounds(row, col, len(grid), len(grid[0]))`.
  - Does **not** import or assume global `ROWS` and `COLS`.
- **`baseline.py`**:
  - `bfs_to_nearest_target` will explicitly use `len(grid)` and `len(grid[0])` with `in_bounds`, ensuring negative indices never wrap and arbitrary test grid sizes work seamlessly.

---

## 6. Tests and Hand-Computed Numbers

All 18 tests will be placed in `tests/test_baseline.py`:

| # | Test Name | Hand-Computed Derivation & Verification |
|---|---|---|
| 1 | `test_shelter_only_no_buildings` | Shelter at (5, 10), 0 buildings: `unconnected` is empty -> baseline 0, route `[]`. |
| 2 | `test_building_adjacent_to_shelter` | Shelter at (5, 10), house at (5, 11). Distance is 0 (directly adjacent per D3) -> baseline 0. |
| 3 | `test_single_building_straight_line` | Shelter (5, 10), house (5, 15). Columns between them on row 5: 11, 12, 13, 14 = 4 empty cells -> baseline 4, route exactly `[(5, 11), (5, 12), (5, 13), (5, 14)]`. |
| 4 | `test_diagonal_building` | Shelter (5, 10), house (6, 11). Manhattan distance is 2. Touching orthogonal neighbors requires exactly 1 sandbag at either (5, 11) or (6, 10) -> baseline 1. |
| 5 | `test_collinear_chain_shared_path` | Shelter (5, 10), house1 (5, 15), house2 (5, 20). Independent sum = 4 + 9 = 13. Greedy connects to house1 (4 bags: cols 11-14). House1 is now in network; house2 connects from house1 with 4 bags (cols 16-19). Baseline = 4 + 4 = 8 (not 13). |
| 6 | `test_shared_trunk` | Shelter (5, 5), house1 (5, 15), house2 (5, 17). Shelter to house1 takes 9 bags (cols 6-14). House1 enters network. House2 is at col 17, needing only col 16 (1 bag) from house1. Baseline = 9 + 1 = 10 (not 9 + 11 = 20). |
| 7 | `test_branching_route` | Shelter (5, 10), house1 (5, 15), house2 (2, 13). Nearest is house1 (cost 4: cols 11-14). Network now contains (5, 13). From (5, 13) to house2 (2, 13) requires (4, 13) and (3, 13) (cost 2). Baseline = 4 + 2 = 6, and route contains (4, 13), (3, 13). |
| 8 | `test_relay_building` | Shelter (5, 10), house1 (5, 15), house2 (5, 16). Shelter to house1 takes 4 bags. House2 is directly adjacent to house1 (D3 relay), costing 0 bags. Baseline = 4. |
| 9 | `test_bfs_unit_behavior` | Tests `bfs_to_nearest_target` directly: returns nearest of two targets, returns `([], target)` when target touches source, returns `None` when targets set is empty. |
| 10 | `test_route_properties` | Across several topologies: route has no duplicates, all cells were `CELL_EMPTY`, none is entity, `len(route) == baseline`. |
| 11 | `test_route_connects_everything` | Verifies `route_connects_everything` returns True on baseline routes, False on empty route, and leaves grid/entities untouched (deep copy comparison). |
| 12 | `test_upper_bound_invariant` | Baseline is always <= sum of independent shelter-to-building distances on `TEST_LAYOUT` and generated levels. (Greedy can never cost more than independent routes because network only expands). |
| 13 | `test_determinism_and_entity_order_independence` | Same layout produces identical route regardless of entity order in the list (reversing entities gives same result). |
| 14 | `test_error_handling` | Grid with no shelter raises `ValueError`; grid already containing sandbag raises `ValueError`. Grid remains unchanged after error. |
| 15 | `test_sandbag_budget_formula` | `calculate_sandbag_budget(10) == 10 + SANDBAG_MARGIN`; monkeypatching margin scales budget; negative baseline raises `ValueError`. |
| 16 | `test_end_to_end_default_seed_levels` | Levels 1, 2, 3 with default seeds: place all route cells with `place_sandbag(..., budget)`: all succeed, `passed` is True, `saved == total_pop`, `sandbags_remaining == SANDBAG_MARGIN`, `efficiency_bonus == SANDBAG_MARGIN * 5`. |
| 17 | `test_stress_200_seeds` | Levels 1, 2, 3 across seeds 0..199: `route_connects_everything` is True, `len(route) == baseline`, no crashes. |
| 18 | `test_budget_enforces_limit` | With budget from test 16, attempting to place `budget + 1` sandbags raises `ValueError` (F03 invariant maintained). |

---

## 7. Ambiguities and Conflicts

1. **Greedy Heuristic vs. True Minimum (Steiner Tree)**:
   Decision D2 explicitly states that baseline is calculated via greedy shortest-path heuristic, NOT an exact Steiner tree. The result is an upper bound on the true minimum. A skilled player can occasionally find a shorter route that saves more sandbags. This is an intentional design choice, fully aligned with D2.
2. **Terminal Output in Main.py**:
   The spec asks to print `Level X: baseline Y, budget Z` upon generation. This terminal output is for evaluation/debugging; the baseline is never shown in the graphical UI.

---

## 8. Risks and Mitigations

| Risk | Mitigation |
|---|---|
| **Non-deterministic tie-breaking in BFS** if `sources` are iterated in set order. | Initialize the queue from `sorted(sources)` and expand neighbors in fixed `DIRECTIONS` order. Tested in Test 13. |
| **Accidental grid mutation during verification**. | `route_connects_everything` strictly operates on deep copies of grid and entities. Tested in Test 11. |
| **Performance in 200-seed stress test** (200 seeds × 3 levels = 600 routes). | BFS on a 10×30 grid with 7–11 buildings runs in < 0.5 ms per level. 600 runs take under 0.5 seconds total. |
| **Negative coordinate wrapping**. | Always guard neighbors with `in_bounds(nr, nc, len(grid), len(grid[0]))` before accessing `grid[nr][nc]`. |

