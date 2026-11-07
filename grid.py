"""
Grid logic module.
Handles the data structure and coordinate conversions for the game grid.
Pure logic: NO pygame imports allowed.
"""

def create_grid(rows, cols):
    """
    Creates a 2D list initialized to 'empty'.
    Example: create_grid(2, 2) -> [['empty', 'empty'], ['empty', 'empty']]
    """
    return [["empty" for _ in range(cols)] for _ in range(rows)]

def in_bounds(row, col, rows, cols):
    """
    Checks if a coordinate is within the grid boundaries.
    Example: in_bounds(0, 0, 10, 30) -> True
    """
    return 0 <= row < rows and 0 <= col < cols

def get_cell(grid, row, col):
    """
    Returns the value of a cell with bounds checking.
    Example: get_cell(grid, 0, 0) -> 'empty'
    """
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0

    if not in_bounds(row, col, rows, cols):
        raise IndexError(f"Grid access out of bounds: ({row}, {col})")

    return grid[row][col]

def set_cell(grid, row, col, value):
    """
    Sets the value of a cell with bounds checking.
    Example: set_cell(grid, 0, 0, 'house')
    """
    rows = len(grid)
    cols = len(grid[0]) if rows > 0 else 0

    if not in_bounds(row, col, rows, cols):
        raise IndexError(f"Grid access out of bounds: ({row}, {col})")

    grid[row][col] = value

def pixel_to_cell(x, y, origin_x, origin_y, cell_size, rows, cols):
    """
    Converts screen pixel coordinates to (row, col) grid indices.
    Returns None if the pixel is outside the grid.
    Example: pixel_to_cell(60, 170, 60, 170, 36, 10, 30) -> (0, 0)
    """
    # Relative position from grid top-left
    rel_x = x - origin_x
    rel_y = y - origin_y

    if rel_x < 0 or rel_y < 0:
        return None

    col = rel_x // cell_size
    row = rel_y // cell_size

    if not in_bounds(row, col, rows, cols):
        return None

    return (row, col)

def cell_to_pixel(row, col, origin_x, origin_y, cell_size):
    """
    Converts (row, col) grid indices to the top-left screen pixel coordinate.
    Example: cell_to_pixel(0, 0, 60, 170, 36) -> (60, 170)
    """
    x = origin_x + (col * cell_size)
    y = origin_y + (row * cell_size)
    return (x, y)
