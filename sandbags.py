"""
Sandbags logic module.
Handles counting, placing, and removing sandbags on the grid.
Pure logic: NO pygame imports allowed.
"""
from config import CELL_EMPTY, CELL_SANDBAG, CELL_HOUSE, CELL_SCHOOL, CELL_HOSPITAL, CELL_SHELTER

# Error reasons
MSG_OUT_OF_BOUNDS = "Position is outside the grid."
MSG_OCCUPIED = "Cannot place sandbag on a building."
MSG_ALREADY_SANDBAG = "Cell already contains a sandbag."
MSG_NO_BUDGET = "No sandbags remaining in budget."

def count_sandbags(grid):
    """
    Counts all cells that are marked as 'sandbag'.
    Example: count_sandbags(grid) -> 15
    """
    count = 0
    for row in grid:
        for cell in row:
            if cell == CELL_SANDBAG:
                count += 1
    return count

def remaining_sandbags(grid, total_budget):
    """
    Calculates remaining budget based on the grid state.
    Example: remaining_sandbags(grid, 40) -> 25
    """
    return total_budget - count_sandbags(grid)

def check_placement(grid, row, col, total_budget):
    """
    Checks if a sandbag can be placed at the given position.
    Returns (True, "") if allowed, otherwise (False, reason).
    Example: check_placement(grid, 0, 0, 40) -> (True, "")
    """
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0

    # 1. Bounds check
    if not (0 <= row < rows and 0 <= col < cols):
        return False, MSG_OUT_OF_BOUNDS

    # 2. Building check
    cell = grid[row][col]
    if cell in (CELL_HOUSE, CELL_SCHOOL, CELL_HOSPITAL, CELL_SHELTER):
        return False, MSG_OCCUPIED

    # 3. Existing sandbag check
    if cell == CELL_SANDBAG:
        return False, MSG_ALREADY_SANDBAG

    # 4. Budget check
    if remaining_sandbags(grid, total_budget) <= 0:
        return False, MSG_NO_BUDGET

    return True, ""

def place_sandbag(grid, row, col, total_budget):
    """
    Places a sandbag if allowed. Raises ValueError with reason if not.
    Example: place_sandbag(grid, 0, 0, 40)
    """
    allowed, reason = check_placement(grid, row, col, total_budget)
    if not allowed:
        raise ValueError(reason)

    grid[row][col] = CELL_SANDBAG

def remove_sandbag(grid, row, col):
    """
    Removes a sandbag. Raises ValueError if position is not a sandbag.
    Example: remove_sandbag(grid, 0, 0)
    """
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0

    if not (0 <= row < rows and 0 <= col < cols):
        raise ValueError(MSG_OUT_OF_BOUNDS)

    if grid[row][col] != CELL_SANDBAG:
        raise ValueError("Only sandbags can be removed.")

    grid[row][col] = CELL_EMPTY

def clear_sandbags(grid):
    """
    Turns all sandbags back to empty. Buildings are untouched.
    Example: clear_sandbags(grid)
    """
    for row in range(len(grid)):
        for col in range(len(grid[0])):
            if grid[row][col] == CELL_SANDBAG:
                grid[row][col] = CELL_EMPTY
