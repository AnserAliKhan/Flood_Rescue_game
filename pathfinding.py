"""
Pathfinding module.
Implements recursive and iterative DFS to determine connectivity to the shelter.
Pure logic: NO pygame imports allowed.
"""
from config import DIRECTIONS, CELL_EMPTY
import grid as grid_module

def is_traversable(grid, row, col):
    """
    Checks if a cell can be entered.
    Returns True if in-bounds and not 'empty'.
    Example: is_traversable(grid, 0, 0) -> True
    """
    # Corrected: Use grid_module.in_bounds (the function in grid.py), not grid.in_bounds (the list object)
    if not grid_module.in_bounds(row, col, len(grid), len(grid[0])):
        return False
    return grid[row][col] != CELL_EMPTY

def dfs_visit(grid, row, col, visited):
    """
    Recursive DFS to visit all connected traversable cells.
    - Base case 1: Not traversable (out of bounds or empty).
    - Base case 2: Already visited.
    Example: dfs_visit(grid, 5, 15, set())
    """
    # Base case 1: Not traversable
    if not is_traversable(grid, row, col):
        return

    # Base case 2: Already visited (prevents infinite loops)
    if (row, col) in visited:
        return

    # Recursive case:
    # 1. Mark current cell as visited
    visited.add((row, col))

    # 2. Explore all 4 neighbors
    for dr, dc in DIRECTIONS:
        dfs_visit(grid, row + dr, col + dc, visited)

def find_shelter(entities):
    """
    Finds the shelter entity in the entities list.
    Raises ValueError if no shelter is found.
    Example: find_shelter(entities) -> {'type': 'shelter', ...}
    """
    for e in entities:
        if e["type"] == "shelter":
            return e
    raise ValueError("No shelter found in entities list.")

def find_connected_cells(grid, start_row, start_col):
    """
    Returns a set of all cells reachable from the starting position using recursive DFS.
    Example: find_connected_cells(grid, 5, 15) -> {(5, 15), (5, 16), ...}
    """
    visited = set()
    dfs_visit(grid, start_row, start_col, visited)
    return visited

def find_connected_cells_iterative(grid, start_row, start_col):
    """
    Returns a set of all reachable cells using an iterative DFS with a stack.
    Used for cross-checking recursive results.
    """
    visited = set()
    stack = [(start_row, start_col)]

    while stack:
        row, col = stack.pop()
        if is_traversable(grid, row, col) and (row, col) not in visited:
            visited.add((row, col))
            for dr, dc in DIRECTIONS:
                stack.append((row + dr, col + dc))

    return visited

def evaluate_connectivity(grid, entities):
    """
    Determines which buildings are connected to the shelter.
    Updates the 'connected' flag in each entity dictionary.
    Returns the visited set for potential flood animation.
    Example: evaluate_connectivity(grid, entities)
    """
    # 1. Find the shelter to get the starting point
    shelter = find_shelter(entities)
    start_row, start_col = shelter["row"], shelter["col"]

    # 2. Perform one traversal from the shelter
    visited = find_connected_cells(grid, start_row, start_col)

    # 3. Update connectivity flags for all buildings
    for e in entities:
        # The shelter's own flag is left unchanged per spec
        if e["type"] == "shelter":
            continue

        # A building is connected if its position is in the visited set
        if (e["row"], e["col"]) in visited:
            e["connected"] = True
        else:
            e["connected"] = False

    return visited
