import pytest
from grid import (
    create_grid, in_bounds, get_cell, set_cell,
    pixel_to_cell, cell_to_pixel
)
from config import ROWS, COLS, CELL_SIZE, GRID_ORIGIN_X, GRID_ORIGIN_Y

def test_create_grid():
    """Verify grid size and initial state."""
    grid = create_grid(10, 30)
    assert len(grid) == 10
    assert len(grid[0]) == 30
    for row in grid:
        for cell in row:
            assert cell == "empty"

def test_row_independence():
    """Ensure that modifying one row does not affect others (checks for shallow copy bug)."""
    grid = create_grid(10, 30)
    grid[0][0] = "house"
    assert grid[1][0] == "empty", "Modifying row 0 affected row 1! Shallow copy detected."

def test_in_bounds():
    """Verify boundary checks."""
    assert in_bounds(0, 0, 10, 30) is True
    assert in_bounds(9, 29, 10, 30) is True
    assert in_bounds(-1, 0, 10, 30) is False
    assert in_bounds(0, -1, 10, 30) is False
    assert in_bounds(10, 0, 10, 30) is False
    assert in_bounds(0, 30, 10, 30) is False

def test_get_set_cell():
    """Verify cell access and error handling."""
    grid = create_grid(10, 30)
    set_cell(grid, 5, 5, "school")
    assert get_cell(grid, 5, 5) == "school"

    with pytest.raises(IndexError):
        get_cell(grid, -1, 0)
    with pytest.raises(IndexError):
        get_cell(grid, 10, 0)
    with pytest.raises(IndexError):
        set_cell(grid, 0, 30, "house")

def test_pixel_to_cell_basic():
    """Verify basic pixel to cell conversions."""
    # Top-left pixel of cell (0,0)
    assert pixel_to_cell(GRID_ORIGIN_X, GRID_ORIGIN_Y, GRID_ORIGIN_X, GRID_ORIGIN_Y, CELL_SIZE, 10, 30) == (0, 0)
    # One cell to the right (0,1)
    assert pixel_to_cell(GRID_ORIGIN_X + CELL_SIZE, GRID_ORIGIN_Y, GRID_ORIGIN_X, GRID_ORIGIN_Y, CELL_SIZE, 10, 30) == (0, 1)
    # One cell down (1,0)
    assert pixel_to_cell(GRID_ORIGIN_X, GRID_ORIGIN_Y + CELL_SIZE, GRID_ORIGIN_X, GRID_ORIGIN_Y, CELL_SIZE, 10, 30) == (1, 0)
    # Bottom-right pixel of last cell (9,29)
    assert pixel_to_cell(GRID_ORIGIN_X + (29 * CELL_SIZE) + (CELL_SIZE - 1),
                         GRID_ORIGIN_Y + (9 * CELL_SIZE) + (CELL_SIZE - 1),
                         GRID_ORIGIN_X, GRID_ORIGIN_Y, CELL_SIZE, 10, 30) == (9, 29)

def test_pixel_to_cell_boundaries():
    """Verify pixels just outside the grid return None."""
    # Just left
    assert pixel_to_cell(GRID_ORIGIN_X - 1, GRID_ORIGIN_Y, GRID_ORIGIN_X, GRID_ORIGIN_Y, CELL_SIZE, 10, 30) is None
    # Just above
    assert pixel_to_cell(GRID_ORIGIN_X, GRID_ORIGIN_Y - 1, GRID_ORIGIN_X, GRID_ORIGIN_Y, CELL_SIZE, 10, 30) is None
    # Just right
    assert pixel_to_cell(GRID_ORIGIN_X + (30 * CELL_SIZE), GRID_ORIGIN_Y, GRID_ORIGIN_X, GRID_ORIGIN_Y, CELL_SIZE, 10, 30) is None
    # Just below
    assert pixel_to_cell(GRID_ORIGIN_X, GRID_ORIGIN_Y + (10 * CELL_SIZE), GRID_ORIGIN_X, GRID_ORIGIN_Y, CELL_SIZE, 10, 30) is None

def test_coordinate_round_trip():
    """Verify cell_to_pixel and pixel_to_cell round trip."""
    for row in range(10):
        for col in range(30):
            pixel = cell_to_pixel(row, col, GRID_ORIGIN_X, GRID_ORIGIN_Y, CELL_SIZE)
            # Use center of cell to be safe
            center_x = pixel[0] + CELL_SIZE // 2
            center_y = pixel[1] + CELL_SIZE // 2
            assert pixel_to_cell(center_x, center_y, GRID_ORIGIN_X, GRID_ORIGIN_Y, CELL_SIZE, 10, 30) == (row, col)
