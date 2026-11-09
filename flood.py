"""
Flood animation logic.
Computes which cells are flooded, builds column-by-column step lists,
and converts elapsed time to step counts.
Pure logic: NO pygame imports allowed.
"""


def get_flooded_cells(grid, safe_cells):
    """
    Returns the set of (row, col) for every cell NOT in the safe set.
    Uses nested loops over the grid dimensions.
    Example: get_flooded_cells(grid, {(5, 15)}) -> {(0, 0), (0, 1), ...}
    """
    flooded = set()
    for row in range(len(grid)):
        for col in range(len(grid[0])):
            if (row, col) not in safe_cells:
                flooded.add((row, col))
    return flooded


def compute_flood_steps(grid, safe_cells):
    """
    Returns a list of COLS items. Item i is the list of (row, col) of
    flooded cells in column i (left-to-right sweep).
    Example: compute_flood_steps(grid, safe) -> [[(0,0),(1,0),...], [(0,1),...], ...]
    """
    steps = []
    for col in range(len(grid[0])):
        column_cells = []
        for row in range(len(grid)):
            if (row, col) not in safe_cells:
                column_cells.append((row, col))
        steps.append(column_cells)
    return steps


def current_step(elapsed_ms, step_ms):
    """
    Returns how many steps have been revealed so far.
    Integer division, clamped to >= 0.
    Example: current_step(120, 60) -> 2
    """
    if elapsed_ms < 0:
        return 0
    return elapsed_ms // step_ms


def cells_flooded_at(steps, step_count):
    """
    Returns the set of cells in the first step_count items of steps.
    step_count is clamped to [0, len(steps)].
    Example: cells_flooded_at(steps, 3) -> {(0,0), (1,0), (0,1), ...}
    """
    result = set()
    # Clamp step_count to valid range
    count = max(0, min(step_count, len(steps)))
    for i in range(count):
        for cell in steps[i]:
            result.add(cell)
    return result


def is_flood_finished(elapsed_ms, step_ms, total_steps, hold_ms):
    """
    Returns True once the full sweep plus the end hold time has passed.
    Example: is_flood_finished(2600, 60, 30, 800) -> True
    """
    total_time = total_steps * step_ms + hold_ms
    return elapsed_ms >= total_time

