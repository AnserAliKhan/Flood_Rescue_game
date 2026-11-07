import pytest
from sandbags import (
    count_sandbags, remaining_sandbags, check_placement,
    place_sandbag, remove_sandbag, clear_sandbags
)
from grid import create_grid
from entities import build_layout
from config import (
    ROWS, COLS, TEST_SANDBAG_BUDGET, TEST_LAYOUT,
    CELL_EMPTY, CELL_SANDBAG, CELL_HOUSE, CELL_SHELTER
)

def test_counting():
    """Verify sandbag counting on fresh and populated grids."""
    grid = create_grid(ROWS, COLS)
    assert count_sandbags(grid) == 0

    grid[0][0] = CELL_SANDBAG
    grid[0][1] = CELL_SANDBAG
    grid[1][0] = CELL_SANDBAG
    assert count_sandbags(grid) == 3

def test_place_sandbag_success():
    """Verify placing a sandbag on empty cell works."""
    grid = create_grid(ROWS, COLS)
    budget = 40
    place_sandbag(grid, 0, 0, budget)
    assert grid[0][0] == CELL_SANDBAG
    assert remaining_sandbags(grid, budget) == 39

def test_place_sandbag_failures():
    """Verify placement constraints (occupied, bounds, budget)."""
    grid = create_grid(ROWS, COLS)
    entities = build_layout(grid, TEST_LAYOUT)
    budget = 40

    # 1. Occupied by building
    # Use a house from TEST_LAYOUT
    house_row, house_col = TEST_LAYOUT[1][1], TEST_LAYOUT[1][2]
    with pytest.raises(ValueError, match="building"):
        place_sandbag(grid, house_row, house_col, budget)

    # 2. Out of bounds
    with pytest.raises(ValueError, match="outside"):
        place_sandbag(grid, -1, 0, budget)
    with pytest.raises(ValueError, match="outside"):
        place_sandbag(grid, 10, 0, budget)

    # 3. Already a sandbag
    grid[0][0] = CELL_SANDBAG
    with pytest.raises(ValueError, match="already"):
        place_sandbag(grid, 0, 0, budget)

    # 4. Budget depletion
    small_budget = 2
    grid_small = create_grid(ROWS, COLS)
    place_sandbag(grid_small, 0, 0, small_budget)
    place_sandbag(grid_small, 0, 1, small_budget)
    with pytest.raises(ValueError, match="budget"):
        place_sandbag(grid_small, 0, 2, small_budget)

def test_remove_sandbag():
    """Verify sandbag removal and error cases."""
    grid = create_grid(ROWS, COLS)
    budget = 40
    place_sandbag(grid, 0, 0, budget)

    # Success
    remove_sandbag(grid, 0, 0)
    assert grid[0][0] == CELL_EMPTY
    assert remaining_sandbags(grid, budget) == 40

    # Failure: empty cell
    with pytest.raises(ValueError, match="Only sandbags"):
        remove_sandbag(grid, 0, 0)

    # Failure: building cell
    grid[1][1] = CELL_HOUSE
    with pytest.raises(ValueError, match="Only sandbags"):
        remove_sandbag(grid, 1, 1)

def test_clear_sandbags():
    """Verify Reset functionality."""
    grid = create_grid(ROWS, COLS)
    entities = build_layout(grid, TEST_LAYOUT)

    # Place some sandbags
    grid[0][0] = CELL_SANDBAG
    grid[0][1] = CELL_SANDBAG

    clear_sandbags(grid)

    # No sandbags left
    assert count_sandbags(grid) == 0
    # Buildings still there
    for e in entities:
        assert grid[e["row"]][e["col"]] == e["type"]

def test_budget_consistency():
    """Verify count + remaining always equals total budget."""
    grid = create_grid(ROWS, COLS)
    budget = 10

    # Sequence of actions
    place_sandbag(grid, 0, 0, budget)
    place_sandbag(grid, 0, 1, budget)
    remove_sandbag(grid, 0, 0)
    place_sandbag(grid, 1, 1, budget)

    assert count_sandbags(grid) + remaining_sandbags(grid, budget) == budget

def test_check_placement_reasons():
    """Verify that check_placement returns the correct (bool, reason) tuples."""
    grid = create_grid(ROWS, COLS)
    budget = 40

    # Valid
    assert check_placement(grid, 0, 0, budget) == (True, "")
    # Bounds
    assert check_placement(grid, -1, 0, budget)[0] is False
    # Building (Shelter)
    grid[5][15] = CELL_SHELTER
    assert check_placement(grid, 5, 15, budget)[0] is False
    # Already sandbag
    grid[0][0] = CELL_SANDBAG
    assert check_placement(grid, 0, 0, budget)[0] is False
    # Budget
    assert check_placement(grid, 0, 1, 0)[0] is False
