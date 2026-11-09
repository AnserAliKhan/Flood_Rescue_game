# Flood Rescue - Demonstration & Viva Notes

This document provides a concise reference and cheat sheet for demonstrating "Flood Rescue" in an oral exam, project viva, or walkthrough.

---

## 1. Two-Minute Demonstration Script

1. **Launch the Game**:
   - Run `python main.py`.
   - **Show**: Point out the clean Main Menu (`START GAME`, `INSTRUCTIONS`, `EXIT`). Highlight button hover feedback.
2. **Review Instructions Screen**:
   - Click **INSTRUCTIONS**.
   - **Show**: Point out the two-column rules layout, dynamic population values (`house: 2`, `school: 5`, `hospital: 8`), and scoring rules (Decision D5). Press **ESC** or click **BACK** to return to the menu.
3. **Start Game & Level 1 Planning**:
   - Click **START GAME**. Level 1 loads deterministically (Seed 101: 7 buildings, population 20, budget 29).
   - Press **S** (or click **SANDBAG TOOL**) to activate placement mode.
   - Left-click empty cells between the green shelter (`SH`) and the houses/schools to pave sandbag corridors.
   - Intentionally right-click or click an existing sandbag to demonstrate sandbag removal and budget restoration.
   - Click **RESET** to demonstrate clearing all sandbags, then quickly reconnect all buildings.
4. **Flood Animation & Confirmation**:
   - Click **CONFIRM ROUTES / START FLOOD**. The confirmation modal dims the background and reports remaining sandbags.
   - Click **START FLOOD**. The water animation sweeps across the 30 columns. Note that pressing **SPACE** or clicking can skip the animation directly to the results.
5. **Results & Progression**:
   - The results panel outlines all connected buildings in green and displays the score breakdown.
   - Point out that because all 20 civilians were saved, an efficiency bonus was awarded for unused sandbags.
   - Click **CONTINUE TO NEXT LEVEL** to advance to Level 2 (Seed 202: 9 buildings, 30 civilians, budget 39).
6. **Summary Screen & Replay**:
   - Fast-forward to Level 3 completion: the continue button changes to **VIEW FINAL SUMMARY**.
   - The Final Summary table displays the 3-level campaign breakdown, aggregate metrics (Total Saved, Total Score, Sandbag Efficiency %), and the **PLAY AGAIN** and **MAIN MENU** buttons.
   - Click **PLAY AGAIN** or **MAIN MENU** to show a 100% clean reset.

---

## 2. Explanation of Core Programming Concepts (SPEC 13)

### 1. Variables and Data Types
- **Location**: `config.py`
- **Explanation**: The project organizes primitive data types (integers for grid dimensions, strings for identifiers, and tuples for RGB color vectors and screen coordinates). Using uppercase immutable constants prevents hard-coded magic numbers and ensures global consistency.

### 2. Conditional Statements
- **Location**: `sandbags.py` (`can_place_sandbag`), `screens.py` (`change_screen`)
- **Explanation**: `if/elif/else` ladders enforce strict placement rules: ensuring target coordinates lie within the 10x30 boundaries, preventing sandbags from overwriting buildings, and disallowing placement when the budget is zero.

### 3. Loops and Nested Loops
- **Location**: `grid.py` (`create_grid`), `interface.py` (`draw_grid`)
- **Explanation**: Nested `for` loops iterate over rows (`0..9`) and columns (`0..29`) to generate and render the 300 cells. Nested iteration guarantees that the 2D visual representation precisely matches the internal data structure.

### 4. 2D Nested Lists
- **Location**: `grid.py` (`get_cell`, `set_cell`)
- **Explanation**: The game board is represented as a list of 10 row lists, each containing 30 string values (`grid[row][col]`). This provides instant $O(1)$ coordinate lookup and intuitive spatial mapping.

### 5. Dictionaries
- **Location**: `entities.py` (`create_entity`), `campaign.py` (`create_campaign`)
- **Explanation**: Dictionaries represent heterogeneous data structures with descriptive string keys (`id`, `type`, `row`, `col`, `population`, `connected`). This avoids rigid classes and allows pure functional manipulation.

### 6. Functions & Modularity
- **Location**: All 13 `.py` modules
- **Explanation**: Code is decomposed into single-responsibility functions that receive arguments and return new values. Pure logic modules are strictly separated from Pygame rendering code.

### 7. Recursion
- **Location**: `pathfinding.py` (`dfs_visit`)
- **Explanation**: Depth-First Search is implemented recursively to explore 4-directional connected neighbors. Recursion stops at base cases (out-of-bounds, empty cells, or already visited cells), naturally traversing branching paths.

### 8. Basic Algorithms & Pathfinding
- **Location**: `baseline.py` (`bfs_to_nearest_target`, `calculate_baseline_route`)
- **Explanation**: A multi-source Breadth-First Search (BFS) using a FIFO queue (`collections.deque`) calculates shortest paths through empty cells, greedily growing the network from the shelter to all civilians.

### 9. Random Number Generation
- **Location**: `level_generator.py` (`generate_level`)
- **Explanation**: Uses `random.Random(seed)` instances to generate procedurally placed buildings. Using explicit seed integers ensures that level layouts are reproducible on retries and restarts.

### 10. Data Validation & Defensive Programming
- **Location**: `campaign.py` (`record_level_result`), `scoring.py` (`check_evaluated`)
- **Explanation**: Functions validate state preconditions and raise descriptive `ValueError` exceptions before processing. Dictionaries are copied using `copy.deepcopy` to prevent accidental state mutation.

---

## 3. Step-by-Step Trace of `dfs_visit` (Walking Through the Code)

Let's trace `dfs_visit` on a small 6-cell network:
- Shelter at `(0, 0)`
- Sandbags placed at `(0, 1)`, `(0, 2)`, `(1, 2)`
- House at `(1, 3)`
- Empty cell at `(1, 1)`

```
  Col:    0       1       2       3
Row 0: [Shelter] [Sandbag] [Sandbag] [ Empty ]
Row 1: [ Empty ] [ Empty ] [Sandbag] [ House ]
```

### Verbal Trace Steps:
1. **Call `dfs_visit(grid, 0, 0, visited)`**:
   - Cell `(0, 0)` is traversable (`CELL_SHELTER != 'empty'`) and not in `visited`.
   - Add `(0, 0)` to `visited`. `visited = {(0, 0)}`.
   - Iterate directions: Up `(-1, 0)` out of bounds; Down `(1, 0)` is empty; Left `(0, -1)` out of bounds; Right `(0, 1)` is traversable sandbag!
2. **Recursive Call `dfs_visit(grid, 0, 1, visited)`**:
   - Cell `(0, 1)` is traversable and not in `visited`.
   - Add `(0, 1)` to `visited`. `visited = {(0, 0), (0, 1)}`.
   - Explores Left `(0, 0)`: already in `visited` $\rightarrow$ **Base Case 2 fires, returns immediately**. This prevents an infinite loop between `(0, 0)` and `(0, 1)`!
   - Explores Right `(0, 2)`: traversable sandbag!
3. **Recursive Call `dfs_visit(grid, 0, 2, visited)`**:
   - Add `(0, 2)` to `visited`.
   - Explores Down `(1, 2)`: traversable sandbag!
4. **Recursive Call `dfs_visit(grid, 1, 2, visited)`**:
   - Add `(1, 2)` to `visited`.
   - Explores Right `(1, 3)`: traversable house!
5. **Recursive Call `dfs_visit(grid, 1, 3, visited)`**:
   - Add `(1, 3)` to `visited`. All neighbors of `(1, 3)` are either empty or visited. Returns up the call stack.
6. **Result**: `(1, 3)` is in `visited`, so `e["connected"] = True`.

---

## 4. Worked Example: Multi-Source BFS Baseline & Shared Trunk

Consider two houses: House A at `(0, 3)` and House B at `(2, 3)`, with Shelter at `(0, 0)`.

```
  Col:    0       1       2       3
Row 0: [Shelter] [ . . ]  [ . . ]  [House A]
Row 1: [ . . ]   [ . . ]  [ . . ]  [ . . ]
Row 2: [ . . ]   [ . . ]  [ . . ]  [House B]
```

### Step-by-Step Execution:
1. **Initial Network**: `network = {(0, 0)}`, `unconnected = {(0, 3), (2, 3)}`.
2. **First Search**:
   - BFS from `(0, 0)` finds House A at `(0, 3)`.
   - Shortest path requires sandbags at `(0, 1)` and `(0, 2)` (2 sandbags).
   - Newly paved cells are added to the network: `network = {(0, 0), (0, 1), (0, 2), (0, 3)}`.
3. **Second Search (Shared Trunk Reuse)**:
   - BFS now starts from ALL cells in `network` simultaneously.
   - Cell `(0, 2)` is already part of the network!
   - Expanding from `(0, 2)` reaches House B via `(1, 2)` and `(2, 2)` (2 sandbags).
   - If we had paved directly from the shelter, House B would have cost 4 sandbags.
   - Because the path `(0, 0) -> (0, 2)` is shared as a trunk, it is **counted only once**. Total baseline = $2 + 2 = 4$ sandbags.

---

## 5. Ten Common Viva Questions & Model Answers

### Q1: Why did you separate `screens.py` and `game.py`?
**Answer**: They represent two distinct state machines operating at different levels of abstraction. `screens.py` manages application navigation (Main Menu, Instructions, Game), whereas `game.py` manages the tactical puzzle lifecycle (Planning, Confirming, Flooding, Results). Separating them avoids a messy monolithic state enum and allows testing puzzle logic without screen UI dependencies.
- *Open file*: `screens.py` and `game.py`.

### Q2: Why is the BFS baseline an upper bound rather than the true minimum?
**Answer**: Finding the exact minimum number of sandbag tiles to connect multiple terminal vertices on a grid graph is the **Rectilinear Steiner Tree problem**, which is NP-hard. Our greedy heuristic connects the closest building at each step. While it produces efficient routes in polynomial time ($O(V+E)$), certain global optimal topologies (like a central hub) might require slightly fewer sandbags.
- *Open file*: `baseline.py`.

### Q3: What prevents infinite loops in your recursive DFS?
**Answer**: Every time `dfs_visit` enters a cell, it checks `(row, col) in visited`. If true, Base Case 2 returns immediately. Because cells are added to `visited` on entry and never removed, each grid cell is entered at most once, guaranteeing termination in at most 300 steps.
- *Open file*: `pathfinding.py:20`.

### Q4: Could your recursive DFS cause a Python stack overflow?
**Answer**: No. The grid has exactly 10 rows and 30 columns (300 cells total). In the worst-case snake path visiting every cell, the call stack depth reaches 300 frames. Python's default stack recursion limit is 1000 frames (`sys.getrecursionlimit()`), so stack overflow is mathematically impossible.
- *Open file*: `pathfinding.py` and `tests/test_pathfinding.py:test_deep_recursion`.

### Q5: Why don't any logic modules import Pygame?
**Answer**: Strict separation of concerns. Pure logic modules (`grid`, `sandbags`, `pathfinding`, `scoring`, etc.) manipulate standard Python data structures (lists, dicts, sets). This allows our automated test suite (184 tests) to run in headless environments (like CI/CD servers) without requiring audio or video drivers, and prevents GUI code from tangling with game rules.
- *Open file*: Any logic file (e.g., `scoring.py`).

### Q6: How is Decision D5 different from the original SPEC 9.2?
**Answer**: SPEC 9.2 gave an example where a player saved 16 of 20 people and still received an efficiency bonus for unused sandbags. Decision D5 amended this rule so that the efficiency bonus is strictly awarded **only if 100% of civilians are saved**. Rewarding players for saving sandbags when civilians drown was considered poor game design.
- *Open file*: `docs/DECISIONS.md` and `scoring.py:51`.

### Q7: How do you guarantee the level generator never creates an unsolvable map?
**Answer**: After generating the layout with random placement and spacing checks, `level_generator.generate_level` calls `is_level_solvable(grid, entities)`. This function calculates the baseline BFS route. If any building cannot reach the shelter through empty cells, the attempt is discarded and re-sampled.
- *Open file*: `level_generator.py:100`.

### Q8: What prevents font lag and memory leaks during gameplay?
**Answer**: In early prototypes, `pygame.font.Font` was called inside rendering loops every frame (60 FPS), causing memory churn and garbage collection stutter. In Feature F12, we created `interface.init_fonts()`, which loads all font sizes once into a cached dictionary at startup. Rendering functions simply look up pre-compiled font objects.
- *Open file*: `interface.py:init_fonts` and `main.py:48`.

### Q9: How do you test that the flood animation does not alter scores?
**Answer**: In `tests/test_spec_section15.py` (`test_15_19`), we evaluate connectivity and record the score breakdown before starting the animation. We then step through all columns of the flood simulation and verify that the final breakdown dictionary and entity statuses are identical.
- *Open file*: `tests/test_spec_section15.py:test_15_19...`.

### Q10: How does the game maintain layout consistency when retrying?
**Answer**: Per Decision D4, each level has a predetermined seed defined in `config.LEVEL_SEEDS` (Level 1: 101, Level 2: 202, Level 3: 303). Level generation initializes an isolated PRNG `random.Random(seed)`. Because PRNGs are deterministic, retrying a level or replaying the campaign generates the exact same coordinate positions.
- *Open file*: `config.py:LEVEL_SEEDS` and `campaign.py:prepare_level`.

