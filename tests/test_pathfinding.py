import pytest
from pathfinding import (
    is_traversable, dfs_visit, find_shelter,
    find_connected_cells, find_connected_cells_iterative, evaluate_connectivity
)
from grid import create_grid
from entities import place_entity, build_layout
from config import ROWS, COLS, CELL_SHELTER, CELL_HOUSE, CELL_SANDBAG, CELL_EMPTY, TEST_LAYOUT

def test_is_traversable():
    """Verify traversable checks for various cell types and bounds."""
    grid = create_grid(ROWS, COLS)
    grid[0][0] = CELL_SHELTER
    grid[0][1] = CELL_SANDBAG
    grid[0][2] = CELL_HOUSE

    assert is_traversable(grid, 0, 0) is True  # Shelter
    assert is_traversable(grid, 0, 1) is True  # Sandbag
    assert is_traversable(grid, 0, 2) is True  # House
    assert is_traversable(grid, 1, 0) is False # Empty
    assert is_traversable(grid, -1, 0) is False # Out of bounds
    assert is_traversable(grid, 10, 0) is False # Out of bounds

def test_no_sandbags():
    """Shelter alone: only shelter visited, non-adjacent buildings unconnected."""
    grid = create_grid(ROWS, COLS)
    entities = []
    # Place shelter at (5, 15) and a house at (5, 17) (gap of 1 empty cell)
    place_entity(grid, entities, CELL_SHELTER, 5, 15)
    place_entity(grid, entities, CELL_HOUSE, 5, 17)

    visited = evaluate_connectivity(grid, entities)

    assert (5, 15) in visited
    assert (5, 17) not in visited
    assert entities[1]["connected"] is False

def test_straight_chains():
    """Verify simple horizontal and vertical paths."""
    # Horizontal
    grid_h = create_grid(ROWS, COLS)
    entities_h = []
    place_entity(grid_h, entities_h, CELL_SHELTER, 0, 0)
    grid_h[0][1] = CELL_SANDBAG
    grid_h[0][2] = CELL_SANDBAG
    place_entity(grid_h, entities_h, CELL_HOUSE, 0, 3)

    visited_h = evaluate_connectivity(grid_h, entities_h)
    assert (0, 3) in visited_h
    assert entities_h[1]["connected"] is True

    # Vertical
    grid_v = create_grid(ROWS, COLS)
    entities_v = []
    place_entity(grid_v, entities_v, CELL_SHELTER, 0, 0)
    grid_v[1][0] = CELL_SANDBAG
    grid_v[2][0] = CELL_SANDBAG
    place_entity(grid_v, entities_v, CELL_HOUSE, 3, 0)

    visited_v = evaluate_connectivity(grid_v, entities_v)
    assert (3, 0) in visited_v
    assert entities_v[1]["connected"] is True

def test_diagonals_fail():
    """Ensure diagonal connections are not accepted."""
    grid = create_grid(ROWS, COLS)
    entities = []
    place_entity(grid, entities, CELL_SHELTER, 0, 0)
    # House at (1, 1) - diagonal
    place_entity(grid, entities, CELL_HOUSE, 1, 1)

    visited = evaluate_connectivity(grid, entities)
    assert (1, 1) not in visited
    assert entities[1]["connected"] is False

def test_gap_and_fill():
    """Verify that a gap breaks connection and filling it restores it."""
    grid = create_grid(ROWS, COLS)
    entities = []
    place_entity(grid, entities, CELL_SHELTER, 0, 0)
    grid[0][1] = CELL_SANDBAG
    # gap at (0, 2)
    grid[0][3] = CELL_SANDBAG
    place_entity(grid, entities, CELL_HOUSE, 0, 4)

    visited1 = evaluate_connectivity(grid, entities)
    assert entities[1]["connected"] is False

    # Fill the gap
    grid[0][2] = CELL_SANDBAG
    visited2 = evaluate_connectivity(grid, entities)
    assert entities[1]["connected"] is True

def test_building_adjacent_to_shelter():
    """Decision D3: Building next to shelter is connected with 0 sandbags."""
    grid = create_grid(ROWS, COLS)
    entities = []
    place_entity(grid, entities, CELL_SHELTER, 0, 0)
    place_entity(grid, entities, CELL_HOUSE, 0, 1)

    evaluate_connectivity(grid, entities)
    assert entities[1]["connected"] is True

def test_building_relay():
    """Decision D3: A connected building relays the network to adjacent buildings."""
    grid = create_grid(ROWS, COLS)
    entities = []
    place_entity(grid, entities, CELL_SHELTER, 0, 0)
    grid[0][1] = CELL_SANDBAG
    place_entity(grid, entities, CELL_HOUSE, 0, 2) # House A
    place_entity(grid, entities, CELL_HOUSE, 0, 3) # House B next to A

    evaluate_connectivity(grid, entities)
    assert entities[1]["connected"] is True # House A
    assert entities[2]["connected"] is True # House B

def test_shared_route():
    """Verify shared routes and visited set uniqueness."""
    grid = create_grid(ROWS, COLS)
    entities = []
    place_entity(grid, entities, CELL_SHELTER, 0, 0)
    grid[0][1] = CELL_SANDBAG
    # Split to two houses
    grid[1][1] = CELL_SANDBAG
    place_entity(grid, entities, CELL_HOUSE, 2, 1)
    grid[0][2] = CELL_SANDBAG
    place_entity(grid, entities, CELL_HOUSE, 0, 3)

    visited = evaluate_connectivity(grid, entities)
    assert entities[1]["connected"] is True
    assert entities[2]["connected"] is True
    # The shared sandbag (0, 1) should only be in the set once
    assert (0, 1) in visited

def test_disconnected_island():
    """Island of sandbags not connected to shelter should not be visited."""
    grid = create_grid(ROWS, COLS)
    entities = []
    place_entity(grid, entities, CELL_SHELTER, 0, 0)
    place_entity(grid, entities, CELL_HOUSE, 9, 29)
    grid[9][28] = CELL_SANDBAG
    grid[8][29] = CELL_SANDBAG

    visited = evaluate_connectivity(grid, entities)
    assert (9, 29) not in visited
    assert (9, 28) not in visited
    assert (8, 29) not in visited

def test_dynamic_update():
    """Verify that removing a sandbag updates connectivity flags on next call."""
    grid = create_grid(ROWS, COLS)
    entities = []
    place_entity(grid, entities, CELL_SHELTER, 0, 0)
    grid[0][1] = CELL_SANDBAG
    place_entity(grid, entities, CELL_HOUSE, 0, 2)

    evaluate_connectivity(grid, entities)
    assert entities[1]["connected"] is True

    # Break the path
    grid[0][1] = CELL_EMPTY
    evaluate_connectivity(grid, entities)
    assert entities[1]["connected"] is False

def test_loops_and_branches():
    """Ensure square rings or plus shapes don't cause infinite loops."""
    grid = create_grid(ROWS, COLS)
    entities = []
    place_entity(grid, entities, CELL_SHELTER, 1, 1)
    # Square ring of sandbags
    grid[0][1] = CELL_SANDBAG
    grid[0][2] = CELL_SANDBAG
    grid[1][2] = CELL_SANDBAG
    grid[1][0] = CELL_SANDBAG
    grid[2][0] = CELL_SANDBAG
    grid[2][1] = CELL_SANDBAG
    grid[2][2] = CELL_SANDBAG

    visited = find_connected_cells(grid, 1, 1)
    # Total visited: shelter + 7 sandbags = 8. (0,0) is not reachable.
    assert len(visited) == 8

def test_deep_recursion():
    """Verify a long snake path does not cause RecursionError."""
    grid = create_grid(ROWS, COLS)
    entities = []
    place_entity(grid, entities, CELL_SHELTER, 0, 0)

    # Create snake path
    for r in range(ROWS):
        if r % 2 == 0:
            for c in range(1, COLS):
                grid[r][c] = CELL_SANDBAG
        else:
            for c in range(COLS-1, 0, -1):
                grid[r][c] = CELL_SANDBAG

    # Place house at the end
    place_entity(grid, entities, CELL_HOUSE, 9, 0)
    grid[9][0] = CELL_SANDBAG

    visited = evaluate_connectivity(grid, entities)
    assert (9, 0) in visited

def test_recursive_vs_iterative():
    """Compare recursive and iterative DFS results on various grids."""
    grids_to_test = [
        # 1. Empty grid
        create_grid(ROWS, COLS),
        # 2. TEST_LAYOUT with no sandbags
        create_grid(ROWS, COLS),
        # 3. Snake path
        create_grid(ROWS, COLS)
    ]
    # Setup 2
    entities_test = []
    from entities import build_layout
    g2 = create_grid(ROWS, COLS)
    build_layout(g2, TEST_LAYOUT)
    grids_to_test[1] = g2

    # Setup 3 (Snake)
    g3 = create_grid(ROWS, COLS)
    for r in range(ROWS):
        if r % 2 == 0:
            for c in range(COLS): g3[r][c] = CELL_SANDBAG
        else:
            for c in range(COLS-1, -1, -1): g3[r][c] = CELL_SANDBAG
    grids_to_test[2] = g3

    for g in grids_to_test:
        start_r, start_c = 5, 15
        g[start_r][start_c] = CELL_SHELTER

        rec = find_connected_cells(g, start_r, start_c)
        ite = find_connected_cells_iterative(g, start_r, start_c)
        assert rec == ite

def test_find_shelter_error():
    """Verify ValueError when no shelter is present."""
    with pytest.raises(ValueError):
        find_shelter([])

def test_evaluate_connectivity_flags():
    """Verify shelter is unchanged and others are set to True/False."""
    grid = create_grid(ROWS, COLS)
    entities = []
    place_entity(grid, entities, CELL_SHELTER, 0, 0)
    place_entity(grid, entities, CELL_HOUSE, 0, 1)

    evaluate_connectivity(grid, entities)
    assert entities[0]["connected"] is None
    assert entities[1]["connected"] is True
