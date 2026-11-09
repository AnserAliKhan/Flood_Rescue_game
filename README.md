# Flood Rescue

**Flood Rescue** is a 2D grid-based puzzle and strategy game built in Python using Pygame for a university Computational Thinking course. Set in a flood-prone coastal region, players must construct resilient evacuation corridors using a strictly limited supply of sandbags before incoming floodwaters breach the community. The objective is to strategically link houses, schools, and hospitals to a high-ground shelter. The project emphasizes clean software architecture, separation of pure algorithms from graphical interfaces, recursive graph traversal, and deterministic level generation.

---

## 1. Requirements and Installation

### Prerequisites
- **Python**: Version `3.12.0` or higher
- **Pygame**: Version `2.6.1`
- **Pytest**: Version `8.3.5`

### Installation Steps

#### Windows (PowerShell / Command Prompt)
```powershell
# 1. Clone or extract the project repository
git clone <repo-url>
cd CT_project2

# 2. Create and activate a virtual environment
python -m venv venv
.\venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

#### macOS / Linux (Terminal)
```bash
# 1. Clone or extract the project repository
git clone <repo-url>
cd CT_project2

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

---

## 2. Running the Game and Tests

### Launch the Game
```bash
python main.py
```

### Run the Full Automated Test Suite
```bash
python -m pytest tests/ -v
```

---

## 3. How to Play & Scoring Formulas

### Gameplay Objective
Connect every building (House, School, Hospital) to the green Shelter (`SH`) with an unbroken chain of sandbags (`B`) before the flood simulation starts. Sandbags connect orthogonally (up, down, left, right only; diagonals never count). Touching buildings share connectivity directly and need no extra sandbags between them.

### Controls
- **S Key / SANDBAG TOOL Button**: Toggle placement tool on/off.
- **Left-Click (Grid)**: Place sandbag on empty cell (when tool active) or inspect cell coordinate.
- **Click or Right-Click (Sandbag)**: Remove an existing sandbag and restore budget.
- **RESET Button**: Remove all placed sandbags on current level.
- **CONFIRM / START FLOOD Button**: Open confirmation modal and launch flood animation.
- **SPACE / ESC / Left-Click (during flood)**: Fast-forward / skip animation directly to results.
- **CONTINUE TO NEXT LEVEL**: Enabled only when 100% of civilians are saved.
- **RETRY LEVEL**: Restart the current level with an identical layout.

### Scoring Equations (Authoritative Decision D5)
```
population_score = saved_people * 5

efficiency_bonus = remaining_sandbags * 5  (ONLY IF 100% of civilians are saved; 0 otherwise)

final_level_score = population_score + efficiency_bonus
```

---

## 4. Project Structure

```
CT_project2/
├── config.py                 # Core constants, grid geometry, colors, and layout
├── main.py                   # Pygame initialization, event loop, and screen routing (GUI)
├── interface.py              # Pygame graphics, HUD panels, and button rendering (GUI)
├── screens.py                # Pure logic: screen state machine & instruction formatting
├── campaign.py               # Pure logic: 3-level progression & final summary calculation
├── game.py                   # Pure logic: level phase state machine (planning, confirming, etc.)
├── grid.py                   # Pure logic: 2D list grid operations, bounds checking
├── entities.py               # Pure logic: building/shelter dictionary records & population
├── sandbags.py               # Pure logic: sandbag placement, removal, and remaining counter
├── pathfinding.py            # Pure logic: recursive DFS connectivity from shelter
├── flood.py                  # Pure logic: water sweep partitioning & step generator
├── level_generator.py        # Pure logic: seeded PRNG procedural level generation
├── baseline.py               # Pure logic: multi-source BFS greedy baseline solver
├── requirements.txt          # Python package requirements
├── assets/
│   ├── images/               # Directory reserved for visual assets (.gitkeep)
│   └── fonts/                # Directory reserved for custom font files (.gitkeep)
├── docs/
│   ├── SPEC.md               # Original project assignment specification
│   ├── DECISIONS.md          # Authoritative architectural decisions (D1 - D7)
│   ├── DEMO_NOTES.md         # Oral presentation / viva guide & code traces
│   ├── QA_CHECKLIST.md       # Interactive manual testing checklist
│   └── KNOWN_ISSUES.md       # Documented design limitations and architectural choices
└── tests/
    ├── test_config.py        # Unit tests for grid dimensions & level configuration
    ├── test_grid.py          # Unit tests for 2D list grid operations & boundary checks
    ├── test_entities.py      # Unit tests for entity placement & population counts
    ├── test_sandbags.py      # Unit tests for sandbag budget & placement constraints
    ├── test_pathfinding.py   # Unit tests for recursive/iterative DFS connectivity
    ├── test_flood.py         # Unit tests for water cell partitioning & step lists
    ├── test_scoring.py       # Unit tests for population scores & amended D5 bonuses
    ├── test_game.py          # Unit tests for level phase transitions
    ├── test_level_generator.py # Unit tests for seeded PRNG placement & spacing rules
    ├── test_baseline.py      # Unit tests for greedy multi-source BFS baseline routing
    ├── test_campaign.py      # Unit tests for campaign management & summary aggregation
    ├── test_screens.py       # Unit tests for screen transitions & hit testing
    ├── test_spec_section15.py# Comprehensive SPEC 15 requirement traceability (19 tests)
    ├── test_fuzz_playthrough.py # Fuzz test across 300 random games verifying invariants
    └── test_interface_smoke.py  # Headless visual smoke tests & symbol audits
```

*Note: All modules except `main.py` and `interface.py` are strictly **pure logic** with zero Pygame imports, enabling 100% headless testability.*

---

## 5. Architecture Overview

### Decoupled Dual State Machines
1. **Application Screens** (`screens.py`):
   - States: `menu` $\leftrightarrow$ `instructions`, `menu` $\leftrightarrow$ `game`.
   - Regulates top-level application flow. Returning to menu from game is allowed only after the campaign concludes in the `summary` screen.
2. **Gameplay Level Phases** (`game.py`):
   - Transitions: `planning` $\rightarrow$ `confirming` $\rightarrow$ `flooding` $\rightarrow$ `results` $\rightarrow$ `summary` (or retry to `planning`).
   - The game phase transition table is strictly isolated from application screen routing.

### Grid as Single Source of Truth
The underlying game board is represented as a 2D nested list `grid[row][col]`. Visual rendering in `interface.py` is a pure projection of this data structure. Modifying the grid updates the pathfinding graph, cell rendering, and flood boundaries immediately.

### Backend First, Animation Second
Connectivity, population evacuation, and score breakdowns are evaluated instantly upon route confirmation. The flood animation is purely a visual playback of pre-calculated step partitions, allowing players to skip the animation at any time without corrupting the game state.

### Deterministic Seeded Generator
Each level uses a fixed PRNG seed (`101`, `202`, `303`). Retrying a level or replaying the campaign always yields the exact same puzzle layout.

---

## 6. Algorithms

### 1. Recursive Depth-First Search (DFS) Connectivity
- **Location**: `pathfinding.py` (`dfs_visit`)
- **Purpose**: Explores the 4-directional sandbag and building network starting from the shelter.
- **Why Recursion**: Graph connectivity is naturally expressed recursively: a neighbor is safe if there is a traversable path through its neighbors.
- **Base Cases**:
  1. Coordinate out of bounds or empty cell (`CELL_EMPTY`).
  2. Coordinate already in `visited` set (prevents infinite cycles between adjacent sandbags).
- **Recursion Safety**: The grid contains 300 cells. The maximum possible call stack depth is 300, safely below Python's default recursion limit (1000).

### 2. Multi-Source BFS Greedy Baseline Heuristic
- **Location**: `baseline.py` (`calculate_baseline_route`, `bfs_to_nearest_target`)
- **Purpose**: Computes an upper bound on the minimum sandbags required to link all buildings to the shelter, establishing the level sandbag budget (`budget = baseline + 5`).
- **Algorithm**:
  - Treats the shelter (and all subsequently connected buildings and paths) as an expanding `network` source set.
  - Executes a multi-source Breadth-First Search outwards through empty cells simultaneously until reaching the nearest unconnected building.
  - Appends newly paved cells to the network and repeats until all buildings are connected.
  - **Shared Trunk Optimization**: Paved sandbag cells become sources for subsequent searches, naturally counting shared corridors only once.

### 3. Seeded Placement with Spatial Constraints
- **Location**: `level_generator.py` (`generate_level`)
- **Purpose**: Places the shelter in the center zone and buildings across level-specific regions.
- **Spacing Guarantee**: Enforces an orthogonal Manhattan gap ($\ge 1$) between any two entities, preventing accidental pre-connected buildings while allowing diagonal visual variety.
- **Retry Safeguards**: Samples up to 200 coordinates per building and up to 50 whole-layout restarts before verifying solvability via BFS.

---

## 7. Course Concept Map

| Computational Concept | File | Function / Location | Explanation |
| :--- | :--- | :--- | :--- |
| **Variables & Types** | `config.py` | Lines 1–400 | Integer dimensions, string constants, tuples for RGB colors and pixel coordinates. |
| **Conditionals** | `sandbags.py` | `can_place_sandbag` | Multi-branch validation checking bounds, cell occupancy, and remaining budget limits. |
| **Loops & Nested Loops** | `grid.py` | `create_grid` | Nested `for` loops generating rows and columns of the 2D grid list. |
| **2D Nested Lists** | `grid.py` | `get_cell`, `set_cell` | Representation of the 10x30 board accessed as `grid[row][col]`. |
| **Dictionaries** | `entities.py` | `create_entity` | Structured records storing entity attributes: `id`, `type`, `row`, `col`, `population`, `connected`. |
| **Functions** | `scoring.py` | `calculate_level_score` | Pure mathematical operations with inputs and returned dictionary outputs. |
| **Recursion** | `pathfinding.py`| `dfs_visit` | Recursive exploration of 4-way neighbors with visited-set cycle prevention. |
| **Graph Traversal** | `baseline.py` | `bfs_to_nearest_target` | Multi-source Breadth-First Search using `collections.deque` and predecessor back-pointers. |
| **Random Module** | `level_generator.py`| `generate_level` | Isolated PRNG instances (`random.Random(seed)`) ensuring deterministic procedural layouts. |
| **Data Validation** | `campaign.py` | `record_level_result` | Asserting required dictionary keys and deep-copying data to prevent mutable aliasing. |
| **Modular Programming** | Across project | 13 `.py` modules | Strict decoupling of state, rules, pathfinding, and Pygame user interface. |

---

## 8. Authoritative Decisions Overriding SPEC.md

| Decision | Summary | Superseded SPEC Items |
| :--- | :--- | :--- |
| **D1: Fixed Building Counts** | Level 1: 5H, 2S, 0Hosp (20 pop); Level 2: 6H, 2S, 1Hosp (30 pop); Level 3: 7H, 2S, 2Hosp (40 pop). | Overrides ambiguous combinatorial options in SPEC 4.1. |
| **D2: Heuristic Baseline** | Sandbag minimum computed via greedy multi-source BFS heuristic. Total budget is `baseline + 5` for all levels. | Replaces exact Steiner tree requirement in SPEC 5.1 & 16.A. |
| **D3: Direct Building Links** | Touching buildings link directly and form safe network; sandbags cannot be placed on building cells. | Clarifies SPEC 8.1 relay wording. |
| **D4: Deterministic Retries** | Fixed seeds per level (`101`, `202`, `303`). Retrying a level preserves identical layout. | Overrides random re-generation on retry in SPEC 11. |
| **D5: Efficiency Bonus Rule** | Leftover sandbag bonus (5 pts/sandbag) awarded **ONLY if 100% of civilians are saved**; otherwise 0. | Explicitly overrides SPEC 9.2 example where bonus was awarded for partial saves. |
| **D6: Difficulty Progression** | Difficulty stems solely from more buildings, civilians, and wider regions. Sandbag margin remains constant (+5). | Clarifies SPEC 4.2 difficulty scaling. |
| **D7: Continue Progression** | "Continue to Next Level" button appears **only if all people were saved**. Otherwise, player must retry. | Tightens progression rules in SPEC 10 & 11. |

---

## 9. Testing & Traceability

### Test Summary
- **Total Tests**: `184 passed` (0 failures, 0 regressions)
- **Execution Time**: ~13.6 seconds across the entire suite
- **Pyflakes / Syntax**: 100% clean (zero undefined variables or syntax warnings)

### SPEC Section 15 Traceability Matrix

| SPEC 15 Requirement | Test Function Name | Location | Result |
| :--- | :--- | :--- | :--- |
| **1. 300 cells (10x30)** | `test_15_01_grid_cell_count` | `tests/test_spec_section15.py` | PASSED |
| **2. No building overlaps** | `test_15_02_no_building_overlaps` | `tests/test_spec_section15.py` | PASSED |
| **3. One shelter per level** | `test_15_03_exactly_one_shelter_per_level` | `tests/test_spec_section15.py` | PASSED |
| **4. Population totals** | `test_15_04_population_totals` | `tests/test_spec_section15.py` | PASSED |
| **5. Sandbag budget math** | `test_15_05_sandbag_budget_calculation` | `tests/test_spec_section15.py` | PASSED |
| **6. Placement bounds check**| `test_15_06_sandbag_cannot_be_placed_out_of_bounds` | `tests/test_spec_section15.py` | PASSED |
| **7. Cannot overwrite bldgs**| `test_15_07_sandbag_cannot_overwrite_buildings` | `tests/test_spec_section15.py` | PASSED |
| **8. Placement decreases rem**| `test_15_08_placement_decreases_remaining_budget` | `tests/test_spec_section15.py` | PASSED |
| **9. Removal restores rem** | `test_15_09_removal_restores_remaining_budget` | `tests/test_spec_section15.py` | PASSED |
| **10. Diagonal rejected** | `test_15_10_diagonal_connections_not_accepted` | `tests/test_spec_section15.py` | PASSED |
| **11. Horizontal connected** | `test_15_11_horizontal_connections_accepted` | `tests/test_spec_section15.py` | PASSED |
| **12. Vertical connected** | `test_15_12_vertical_connections_accepted` | `tests/test_spec_section15.py` | PASSED |
| **13. Connected marked safe**| `test_15_13_connected_buildings_marked_safe` | `tests/test_spec_section15.py` | PASSED |
| **14. Unconnected unsafe** | `test_15_14_disconnected_buildings_marked_unsafe` | `tests/test_spec_section15.py` | PASSED |
| **15. Population score math**| `test_15_15_population_score_calculation` | `tests/test_spec_section15.py` | PASSED |
| **16. Efficiency bonus (D5)**| `test_15_16_efficiency_bonus_calculation_amended_d5` | `tests/test_spec_section15.py` | PASSED |
| **17. Level difficulty step**| `test_15_17_levels_increasing_difficulty` | `tests/test_spec_section15.py` | PASSED |
| **18. Clean restart (D4)** | `test_15_18_restart_retains_no_old_data` | `tests/test_spec_section15.py` | PASSED |
| **19. Flood isolation** | `test_15_19_flood_animation_does_not_affect_scoring` | `tests/test_spec_section15.py` | PASSED |

### Reference Campaign Data (Verified Live Run)
- **Level 1 (Seed 101)**: 7 buildings, population 20 | Baseline: 24 | Budget: 29 | Max Score: 125
- **Level 2 (Seed 202)**: 9 buildings, population 30 | Baseline: 34 | Budget: 39 | Max Score: 175
- **Level 3 (Seed 303)**: 11 buildings, population 40 | Baseline: 35 | Budget: 40 | Max Score: 225
- **Perfect Campaign Reference Score**: `525 points`

---

## 10. Known Limitations & Issues

A complete analysis of architectural choices and remaining limitations is documented in [`docs/KNOWN_ISSUES.md`](file:///c:/Users/haroon%20traders/OneDrive/Desktop/Habib%20CS%20Stuff/CT_project2/docs/KNOWN_ISSUES.md). Key points include:
- Flood animation uses a column-by-column visual sweep rather than physical hydraulic elevation modeling.
- Baseline sandbag solver uses a greedy multi-source shortest-path heuristic (an upper bound) rather than an NP-hard exact minimum Steiner tree.
- No in-game pause or return-to-menu hotkey during active level planning (by design to keep the state machine robust and prevent memory corruption).

---

## 11. Credits and Environment

- **Development Environment**: Python `3.12.0` on Windows 11.
- **Rendering & Audio Library**: Pygame `2.6.1`.
- **Test Framework**: Pytest `8.3.5`.
- **Course**: Computational Thinking (University Academic Project).
- **Date**: November 2026.

