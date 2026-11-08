# F08 Level Generator — Implementation Plan

## 1. Files to Create or Change

| File | Action | Purpose |
|---|---|---|
| `level_generator.py` | CREATE | Pure logic module (no pygame). Computes level composition, enforces neighbor spacing, selects random coordinates within regions, verifies reachability/solvability, and generates reproducible levels using `random.Random(seed)`. |
| `tests/test_level_generator.py` | CREATE | Pytest suite covering all 17 specified test cases (composition, bounds, spacing, determinism, solvability, stress test, purity, failure paths). |
| `config.py` | CHANGE | Add level seeds (`LEVEL_SEEDS`), column/row region definitions (`LEVEL_REGIONS`), spacing constraint (`MIN_BUILDING_GAP`), and retry limit constants (`MAX_PLACEMENT_TRIES`, `MAX_LEVEL_RESTARTS`). Mark `TEST_LAYOUT` as legacy/not used by `main.py`. |
| `interface.py` | CHANGE | Update `draw_panels` and `draw_results_panel` to accept and render `current_level` in the top panel and results panel, tracking the active level. |
| `main.py` | CHANGE | Replace `TEST_LAYOUT` initialization with `generate_level(current_level)`. Add debug keys (`1`, `2`, `3`) in `PHASE_PLANNING` to switch levels on the fly. Pass `current_level` to panel rendering. |

---

## 2. Every Constant and Function

### `config.py` — Additions

```python
# Level Generation Seeds (Decision D4: fixed seeds per level for reproducibility)
LEVEL_SEEDS = {
    1: 101,
    2: 202,
    3: 303
}

# Level Placement Regions (col_min, col_max inclusive, row_min, row_max inclusive)
LEVEL_REGIONS = {
    1: {"buildings_cols": (6, 23), "shelter_cols": (12, 17), "rows": (0, 9)},
    2: {"buildings_cols": (2, 27), "shelter_cols": (10, 19), "rows": (0, 9)},
    3: {"buildings_cols": (0, 29), "shelter_cols": (8, 21),  "rows": (0, 9)},
}

# Spacing rule: orthogonal gap between any two entities (Decision D3 / F08)
MIN_BUILDING_GAP = 1  # Orthogonal touching not allowed; diagonal touching is allowed

# Generator Retry Limits
MAX_PLACEMENT_TRIES = 200   # Max random cell attempts per building before restarting layout
MAX_LEVEL_RESTARTS = 50     # Max full-grid restarts before raising RuntimeError
```

### `level_generator.py` — Pure Logic Functions (No Pygame)

```python
def get_level_composition(level: int) -> dict:
    """
    Returns the building count dict for the level from LEVEL_BUILDINGS.
    Validates level exists and total population matches LEVEL_POPULATION[level].
    Raises ValueError on unknown level or population mismatch.
    Example: get_level_composition(1) -> {'house': 5, 'school': 2, 'hospital': 0}
    """

def build_placement_order(composition: dict) -> list[str]:
    """
    Returns an ordered list of building type names from the composition dict
    (e.g., houses, then schools, then hospitals) so scarce buildings are placed reliably.
    Example: build_placement_order({'house': 2, 'school': 1, 'hospital': 0}) -> ['house', 'house', 'school']
    """

def neighbors_are_free(grid: list[list[str]], row: int, col: int) -> bool:
    """
    Checks if all 4 orthogonal neighbors (DIRECTIONS) are either empty or out of bounds.
    Returns True if no adjacent cell contains an entity. Diagonal touching is allowed.
    Example: neighbors_are_free(grid, 5, 5) -> True
    """

def is_valid_spot(grid: list[list[str]], row: int, col: int,
                  col_range: tuple[int, int], row_range: tuple[int, int]) -> bool:
    """
    Returns True if (row, col) is within grid bounds and region ranges,
    is currently CELL_EMPTY, and neighbors_are_free.
    Example: is_valid_spot(grid, 2, 10, (0, 29), (0, 9)) -> True
    """

def pick_random_spot(grid: list[list[str]], rng: random.Random,
                     col_range: tuple[int, int], row_range: tuple[int, int]) -> tuple[int, int] | None:
    """
    Tries up to MAX_PLACEMENT_TRIES times to pick random (row, col) within ranges using rng.randint.
    Returns the first valid (row, col) spot found, or None if all tries fail.
    Example: pick_random_spot(grid, rng, (12, 17), (0, 9)) -> (5, 14)
    """

def is_level_solvable(grid: list[list[str]], entities: list[dict]) -> bool:
    """
    Verifies that sandbag paths can connect the shelter to every building without passing through buildings:
    1. Shelter has at least one empty orthogonal neighbor.
    2. Every building has at least one empty orthogonal neighbor.
    3. Flood-fill / BFS across empty cells starting from shelter's empty neighbors reaches
       at least one empty neighbor of every building.
    Returns True if all hold, False otherwise. Does not modify grid or entities.
    Example: is_level_solvable(grid, entities) -> True
    """

def generate_level(level: int, seed: int | None = None) -> tuple[list[list[str]], list[dict]]:
    """
    Generates a reproducible, solvable level grid and entities list for the given level.
    Uses LEVEL_SEEDS[level] if seed is None. Uses an isolated random.Random(seed) instance.
    Retries up to MAX_LEVEL_RESTARTS times if placement or solvability fails.
    Raises RuntimeError if all restarts fail.
    Validates population, building counts, and shelter presence before returning.
    Example: grid, entities = generate_level(1)
    """
```

### `interface.py` — Modifications

```python
def draw_panels(screen, hover_info, selected_info, pop_info, build_info,
                sandbag_info, phase_name, current_level=1):
    # Renders "Level: {current_level}" in the top panel alongside title and phase.

def draw_results_panel(screen, breakdown, can_continue, font, current_level=1):
    # Renders "Level: {current_level}" based on the active level instead of fixed constant.
```

---

## 3. Step-by-Step Level Generation and Retries

1. **Composition & RNG Setup**:
   - Call `get_level_composition(level)`.
   - Pick `effective_seed = seed if seed is not None else LEVEL_SEEDS[level]`.
   - Instantiate `rng = random.Random(effective_seed)` (never touching global `random`).
2. **Whole-Layout Attempt Loop** (up to `MAX_LEVEL_RESTARTS` times):
   - Create a clean 10×30 grid: `grid = create_grid(ROWS, COLS)` and `entities = []`.
   - Retrieve `regions = LEVEL_REGIONS[level]`.
   - **Place Shelter**:
     - Call `pick_random_spot(grid, rng, regions["shelter_cols"], regions["rows"])`.
     - If `None` is returned: restart the layout attempt.
     - Call `place_entity(grid, entities, CELL_SHELTER, row, col)`.
   - **Place Buildings**:
     - Get list from `build_placement_order(composition)`.
     - For each building type:
       - Call `pick_random_spot(grid, rng, regions["buildings_cols"], regions["rows"])`.
       - If `None` is returned: restart the layout attempt.
       - Call `place_entity(grid, entities, b_type, row, col)`.
   - **Solvability Check**:
     - Call `is_level_solvable(grid, entities)`.
     - If `False`: restart the layout attempt.
   - **Validation & Return**:
     - If solvable: verify building counts, total population against `LEVEL_POPULATION[level]`, and exactly 1 shelter.
     - Return `(grid, entities)`.
3. **Failure Exit**:
   - If loop exhausts `MAX_LEVEL_RESTARTS` without finding a valid, solvable layout, raise `RuntimeError(f"Failed to generate solvable level {level} after {MAX_LEVEL_RESTARTS} restarts.")`.

---

## 4. How `is_level_solvable` Works and What it Guarantees

The algorithm verifies that buildings are not trapped and that a connected sandbag network from the shelter is theoretically possible:

1. **Local Neighbor Check**:
   - Find the shelter entity in `entities`. Inspect its 4 orthogonal neighbors. If 0 are `CELL_EMPTY` (e.g. boxed in by grid edges and entities), return `False`.
   - For every non-shelter building in `entities`: inspect its 4 orthogonal neighbors. If 0 are `CELL_EMPTY`, return `False`.
2. **Empty-Cell Flood-Fill (BFS)**:
   - Initialize a `queue` containing all `(r, c)` empty orthogonal neighbors of the shelter.
   - Maintain a `reachable_empty` set. Add the starting neighbors to both.
   - While `queue` is not empty:
     - Pop `(curr_r, curr_c)`.
     - For each `(dr, dc)` in `DIRECTIONS`:
       - Check neighbor `(nr, nc)`.
       - If `in_bounds(nr, nc)` and `grid[nr][nc] == CELL_EMPTY` and `(nr, nc) not in reachable_empty`:
         - Add `(nr, nc)` to `reachable_empty` and append to `queue`.
3. **Building Reachability Verification**:
   - For every building in `entities` (except shelter):
     - Check if at least one of its orthogonal neighbors is in `reachable_empty`.
     - If any building has zero neighbors in `reachable_empty`, return `False`.
4. **Guarantee**:
   - Guarantees that there exists a continuous corridor of empty cells connecting the shelter perimeter to every building perimeter.
   - Since routes cannot pass through buildings (Decision D3), this guarantees no building is completely partitioned behind a wall of other buildings.

---

## 5. Main.py Integration & Debug Key Handling

1. **Replaces `TEST_LAYOUT`**:
   - At startup: `current_level = CURRENT_LEVEL`.
   - `game_grid, entities_list = level_generator.generate_level(current_level)`.
   - Remove `TEST_LAYOUT` usage from `main.py` (leave constant in `config.py` with explanatory comment).
2. **Debug Key Switching (Keys 1, 2, 3)**:
   - In event handling, when `event.type == pygame.KEYDOWN`:
     - Only active when `state["phase"] == PHASE_PLANNING` (`is_editing_allowed(state)`):
       - If `event.key in (pygame.K_1, pygame.K_2, pygame.K_3)`:
         - Set `current_level = 1, 2, or 3` accordingly.
         - Call `game_grid, entities_list = level_generator.generate_level(current_level)`.
         - Reset game state: `state = game.create_game_state()`.
         - Reset UI variables: `selected_cell = None`, `tool_active = False`.
         - Reset flood animation variables: `flood_start_ms = 0`, `flood_steps = []`.
         - Display temporary message: `f"Loaded Level {current_level}"`.
3. **Safety Outside Planning**:
   - If `state["phase"]` is `confirming`, `flooding`, or `results`, pressing 1, 2, or 3 does nothing.
4. **Retry Behavior Preserved (Decision D4)**:
   - In `PHASE_RESULTS`, clicking **RETRY LEVEL** calls `game.retry_level(state, game_grid, entities_list)`.
   - It resets sandbags and connectivity flags on the existing grid and entities, strictly preserving the exact layout.

---

## 6. Tests in `tests/test_level_generator.py`

| # | Test Name | Verification Focus |
|---|---|---|
| 1 | `test_level_composition_valid_and_invalid` | Returns D1 counts for levels 1, 2, 3; raises `ValueError` for level 0 and 4. |
| 2 | `test_level_composition_population_mismatch` | Monkeypatching `LEVEL_POPULATION` raises `ValueError`. |
| 3 | `test_generate_level_counts_and_populations` | For levels 1, 2, 3: 300 cells, counts match `LEVEL_BUILDINGS`, pop is 20/30/40, exactly 1 shelter. |
| 4 | `test_grid_entity_consistency` | Non-empty cell count matches entity count; grid cell contains entity type. |
| 5 | `test_no_overlaps_and_in_bounds` | Every entity coordinate is unique and within (0..9, 0..29). |
| 6 | `test_spacing_rule` | No entity has an orthogonal neighbor that is another entity (min gap = 1). |
| 7 | `test_region_constraints` | All buildings within level's `buildings_cols`; shelter within `shelter_cols`. |
| 8 | `test_determinism_same_and_different_seeds` | Same seed yields identical entity list; different seeds produce different layouts. |
| 9 | `test_default_seed_uses_config` | `seed=None` produces the exact same layout as `seed=LEVEL_SEEDS[level]`. |
| 10 | `test_global_random_unmodified` | Generator uses isolated `random.Random`; global `random.random()` sequence is untouched. |
| 11 | `test_stress_200_seeds` | Generate levels 1, 2, 3 across seeds 0..199. All pass bounds, spacing, solvability without error. |
| 12 | `test_neighbors_are_free_behavior` | Isolated cell is True, adjacent to building is False, grid corners/edges are handled correctly. |
| 13 | `test_is_level_solvable_cases` | True for valid layout; False when shelter or building has 0 empty neighbors; False when building is ringed/isolated. |
| 14 | `test_generator_purity` | `is_level_solvable` and helpers do not modify input grid/entities (deep-copy check). |
| 15 | `test_runtime_error_on_impossible_constraints` | Monkeypatching `MAX_LEVEL_RESTARTS = 1` and impossible region raises `RuntimeError`. |
| 16 | `test_difficulty_progression_metrics` | Buildings: 7 < 9 < 11; population: 20 < 30 < 40; hospital counts strictly increase (0 -> 1 -> 2). |
| 17 | `test_generated_level_integration_zero_sandbags` | With no sandbags, `evaluate_connectivity` marks 0 buildings connected (due to spacing gap), score is 0. |

---

## 7. Ambiguities and Conflicts

1. **Overlap Between Shelter Region and Building Region**:
   In `LEVEL_REGIONS`, shelter columns (e.g. 12-17 for Level 1) are a sub-range of building columns (6-23). This is intended: the shelter is placed first in the center, and buildings are placed subsequently anywhere in the building region with the 1-cell orthogonal gap constraint.
2. **Fixed Sandbag Budget in F08**:
   The sandbag budget is still `TEST_SANDBAG_BUDGET = 40`. Some Level 3 layouts might require more or fewer sandbags than 40. This is documented and accepted: the dynamic sandbag baseline calculation is scheduled for **Feature F09**.
3. **Debug Keys vs. Future Level Flow**:
   Keys 1, 2, 3 in `main.py` are explicitly temporary for development and testing of F08, to be replaced by full level progression in **Feature F10**.

---

## 8. Risks and Mitigations

| Risk | Mitigation |
|---|---|
| **Placement deadlocks / slow generation** if grid becomes congested. | 10×30 grid has 300 cells for at most 12 entities (11 buildings + 1 shelter). Congestion is low. `MAX_PLACEMENT_TRIES` (200) and `MAX_LEVEL_RESTARTS` (50) protect against infinite loops. |
| **Global random corruption** affecting other modules or tests. | Explicitly instantiate `rng = random.Random(seed)` inside `generate_level`. Never call `random.seed()` or module-level `random` functions. Tested in Test 10. |
| **Stress test execution time** (200 seeds × 3 levels = 600 generations). | Generation of 7-11 buildings on a 10×30 grid takes < 1 ms per level. 600 runs take ~0.5s total. |
| **Breaking F01–F07 tests** that rely on `TEST_LAYOUT`. | Keep `TEST_LAYOUT` in `config.py` untouched so existing unit tests continue to pass without modification. |

