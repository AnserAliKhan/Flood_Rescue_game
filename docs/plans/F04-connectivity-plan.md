# Plan: F04 Recursive DFS Connectivity from the Shelter

## Context
This feature implements the "brain" of the flood simulation. Using a recursive Depth-First Search (DFS), the game will determine which buildings are connected to the shelter through the network of sandbags and other buildings. This is a pure logic implementation used to set the `connected` flag on each entity.

## Proposed Implementation

### 1. Files to Create or Change

- **`pathfinding.py` (CREATE)**: Pure logic module containing the DFS algorithms and connectivity evaluation. No Pygame imports.
- **`tests/test_pathfinding.py` (CREATE)**: Pytest suite to validate connectivity rules, recursion, and edge cases.
- **`config.py` (CHANGE)**: Add the `DIRECTIONS` constant to ensure consistency across the project.

### 2. Functions and Constants

#### `config.py` (Addition)
- `DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]`: Up, Down, Left, Right. Defined here to be accessible by any future pathfinding or grid-walking logic.

#### `pathfinding.py` (Pure Logic)
- `is_traversable(grid, row, col) -> bool`: Returns `True` if the position is in-bounds and the cell is NOT `"empty"`.
- `dfs_visit(grid, row, col, visited) -> None`: The recursive core.
    - **Base Case 1**: Position is not traversable (out of bounds or empty) $\rightarrow$ return.
    - **Base Case 2**: Position `(row, col)` is already in the `visited` set $\rightarrow$ return.
    - **Recursive Case**: Add `(row, col)` to `visited`. For each `(dr, dc)` in `DIRECTIONS`, call `dfs_visit(grid, row + dr, col + dc, visited)`.
- `find_shelter(entities) -> dict`: Returns the shelter entity or raises `ValueError`.
- `find_connected_cells(grid, start_row, start_col) -> set`: Initializes an empty `visited` set, calls `dfs_visit` from the start, and returns the set.
- `find_connected_cells_iterative(grid, start_row, start_col) -> set`: Implements the same logic using a `list` as a stack and a `while` loop.
- `evaluate_connectivity(grid, entities) -> set`: 
    1. Finds the shelter.
    2. Runs `find_connected_cells` from the shelter.
    3. Loops through all entities (except shelter) and sets `entity["connected"] = (entity_pos in visited)`.
    4. Returns the visited set.

### 3. DFS Visit Step-by-Step
1. **Call**: `dfs_visit` is called on a cell.
2. **Check Bounds/Type**: If the cell is outside the grid or is `"empty"`, the function stops immediately (Base Case 1).
3. **Check Visited**: If the cell's coordinates are already in the `visited` set, the function stops to prevent infinite loops (Base Case 2).
4. **Mark Visited**: The current cell is added to the `visited` set.
5. **Explore**: The function looks at the 4 neighbors (Up, Down, Left, Right). For each neighbor, it calls `dfs_visit` again.
6. **Unwind**: Once all neighbors are explored, the function returns to the previous caller.

### 4. Testing Strategy (`tests/test_pathfinding.py`)
Tests will use small, manually constructed grids for clarity:
- **Minimal Grids**: Use `create_grid(3, 3)` and manually set `grid[r][c] = "sandbag"` to create specific scenarios (e.g., a straight line, a gap, a diagonal).
- **Consistency Tests**: Compare the result of `find_connected_cells` (recursive) with `find_connected_cells_iterative` on the same grid.
- **Decision D3 Tests**: 
    - Shelter adjacent to building $\rightarrow$ Connected.
    - Building adjacent to building $\rightarrow$ Relay connection.

### 5. Specific Tests
- **`test_is_traversable`**: Checks empty cells, building cells, and out-of-bounds.
- **`test_no_sandbags`**: Only shelter is visited.
- **`test_simple_chains`**: Horizontal and vertical paths to houses.
- **`test_diagonals_fail`**: Ensure diagonals do not connect.
- **`test_gaps`**: Ensure a single `"empty"` cell breaks the connection.
- **`test_building_relay`**: House A connects to Shelter $\rightarrow$ House B next to House A also connects.
- **`test_deep_recursion`**: Create a "snake" path of $\approx 150$ cells to ensure no `RecursionError`.
- **`test_evaluate_connectivity`**: Verify the `connected` flags in the entity dictionaries are correctly updated.

### 6. Ambiguities and Conflicts
- None identified. The spec explicitly addresses D3 and the a-priori result requirement.

### 7. Risks
- **Recursion Limit**: Python's default limit is 1000. A 10x30 grid has 300 cells, so the maximum depth is 300. This is safely below the limit, but will be documented in the report.
- **Infinite Loops**: If the `visited` set is not updated *before* the recursive calls, the algorithm will loop forever between two adjacent cells.
