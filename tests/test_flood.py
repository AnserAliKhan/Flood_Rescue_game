"""
Tests for the flood animation logic module.
No pygame window needed — all functions are pure logic.
"""
import pytest
import copy
from grid import create_grid
from entities import place_entity
from config import CELL_SHELTER, CELL_HOUSE, CELL_SANDBAG, ROWS, COLS
import pathfinding
import scoring
import flood


# ---- Helper: build a small test grid with a shelter and optional buildings/sandbags ----

def _make_connected_grid():
    """
    Creates a 10x30 grid with:
      - shelter at (0, 0)
      - house at (0, 2), connected through a sandbag at (0, 1)
      - house at (5, 5), NOT connected (no path)
    Returns (grid, entities, safe_cells).
    """
    grid = create_grid(ROWS, COLS)
    entities = []
    place_entity(grid, entities, CELL_SHELTER, 0, 0)
    place_entity(grid, entities, CELL_HOUSE, 0, 2)
    place_entity(grid, entities, CELL_HOUSE, 5, 5)
    # Place a sandbag to connect the first house
    grid[0][1] = CELL_SANDBAG
    safe_cells = pathfinding.evaluate_connectivity(grid, entities)
    return grid, entities, safe_cells


# ---- Test 1: flooded + safe = all cells, no overlap ----

def test_flooded_cells_partition():
    """get_flooded_cells + safe_cells together cover all ROWS*COLS cells with zero overlap."""
    grid, entities, safe_cells = _make_connected_grid()
    flooded = flood.get_flooded_cells(grid, safe_cells)

    # Sizes add up
    assert len(flooded) + len(safe_cells) == ROWS * COLS
    # No overlap
    assert len(flooded & safe_cells) == 0


# ---- Test 2: no sandbags, only shelter is safe ----

def test_no_sandbags_299_flooded():
    """With only a shelter, 299 cells are flooded (only shelter cell is safe)."""
    grid = create_grid(ROWS, COLS)
    entities = []
    place_entity(grid, entities, CELL_SHELTER, 5, 15)
    safe_cells = pathfinding.evaluate_connectivity(grid, entities)
    flooded = flood.get_flooded_cells(grid, safe_cells)

    assert len(safe_cells) == 1         # just the shelter
    assert len(flooded) == ROWS * COLS - 1  # 299


# ---- Test 3: connected building not flooded, unconnected building IS flooded ----

def test_connected_building_not_flooded():
    """A building connected through sandbags is not in the flooded set. An unconnected one is."""
    grid, entities, safe_cells = _make_connected_grid()
    flooded = flood.get_flooded_cells(grid, safe_cells)

    # Connected house at (0, 2) should NOT be flooded
    assert (0, 2) not in flooded
    # Unconnected house at (5, 5) SHOULD be flooded
    assert (5, 5) in flooded


# ---- Test 4: disconnected sandbag island IS flooded ----

def test_disconnected_sandbag_flooded():
    """A sandbag island not linked to the shelter IS flooded."""
    grid = create_grid(ROWS, COLS)
    entities = []
    place_entity(grid, entities, CELL_SHELTER, 0, 0)
    # Disconnected sandbag island at row 9
    grid[9][29] = CELL_SANDBAG
    grid[9][28] = CELL_SANDBAG
    safe_cells = pathfinding.evaluate_connectivity(grid, entities)
    flooded = flood.get_flooded_cells(grid, safe_cells)

    assert (9, 29) in flooded
    assert (9, 28) in flooded


# ---- Test 5: compute_flood_steps structure ----

def test_compute_flood_steps_structure():
    """Returns exactly COLS lists. Every flooded cell exactly once. No safe cell. Correct columns."""
    grid, entities, safe_cells = _make_connected_grid()
    steps = flood.compute_flood_steps(grid, safe_cells)
    flooded = flood.get_flooded_cells(grid, safe_cells)

    # Exactly COLS items
    assert len(steps) == COLS

    # Every cell in item i has column i
    all_cells = set()
    for i, column_list in enumerate(steps):
        for row, col in column_list:
            assert col == i
            all_cells.add((row, col))

    # Every flooded cell appears exactly once
    assert all_cells == flooded

    # No safe cell appears
    assert len(all_cells & safe_cells) == 0


# ---- Test 6: current_step values ----

def test_current_step_values():
    """0 at 0 ms, 0 just before step_ms, 1 at step_ms, correct at larger times, 0 for negative."""
    step_ms = 60
    assert flood.current_step(0, step_ms) == 0
    assert flood.current_step(59, step_ms) == 0     # just before
    assert flood.current_step(60, step_ms) == 1     # exactly step_ms
    assert flood.current_step(120, step_ms) == 2    # two steps
    assert flood.current_step(1800, step_ms) == 30  # full sweep
    assert flood.current_step(-10, step_ms) == 0    # negative


# ---- Test 7: cells_flooded_at bounds ----

def test_cells_flooded_at_bounds():
    """step_count 0 is empty, >= COLS is everything, middle value only has lower columns. Never shrinks."""
    grid, entities, safe_cells = _make_connected_grid()
    steps = flood.compute_flood_steps(grid, safe_cells)
    flooded = flood.get_flooded_cells(grid, safe_cells)

    # 0 steps -> empty
    assert flood.cells_flooded_at(steps, 0) == set()

    # COLS or more -> all flooded
    assert flood.cells_flooded_at(steps, COLS) == flooded
    assert flood.cells_flooded_at(steps, COLS + 100) == flooded

    # Middle value: only cells in columns below that value
    mid = 10
    mid_cells = flood.cells_flooded_at(steps, mid)
    for row, col in mid_cells:
        assert col < mid

    # Result never shrinks as step_count grows
    prev = set()
    for i in range(COLS + 1):
        current = flood.cells_flooded_at(steps, i)
        assert prev.issubset(current)
        prev = current


# ---- Test 8: is_flood_finished timing ----

def test_is_flood_finished_timing():
    """False before total time, True at and after total time."""
    step_ms = 60
    total_steps = 30
    hold_ms = 800
    total_time = total_steps * step_ms + hold_ms  # 2600

    assert flood.is_flood_finished(0, step_ms, total_steps, hold_ms) is False
    assert flood.is_flood_finished(total_time - 1, step_ms, total_steps, hold_ms) is False
    assert flood.is_flood_finished(total_time, step_ms, total_steps, hold_ms) is True
    assert flood.is_flood_finished(total_time + 1000, step_ms, total_steps, hold_ms) is True


# ---- Test 9: purity — functions don't modify inputs ----

def test_purity():
    """get_flooded_cells, compute_flood_steps, cells_flooded_at leave inputs unchanged."""
    grid, entities, safe_cells = _make_connected_grid()

    # Deep copy everything before
    grid_copy = copy.deepcopy(grid)
    entities_copy = copy.deepcopy(entities)
    safe_copy = copy.deepcopy(safe_cells)

    # Run all functions
    flood.get_flooded_cells(grid, safe_cells)
    steps = flood.compute_flood_steps(grid, safe_cells)
    flood.cells_flooded_at(steps, 15)

    # Compare after
    assert grid == grid_copy
    assert entities == entities_copy
    assert safe_cells == safe_copy


# ---- Test 10: animation cannot change the result ----

def test_animation_cannot_change_result():
    """Build breakdown before, run flood functions, build again — identical. Flags unchanged."""
    grid, entities, safe_cells = _make_connected_grid()

    # Build breakdown BEFORE flood functions
    breakdown_before = scoring.build_score_breakdown(grid, entities, 40)
    flags_before = [(e["id"], e["connected"]) for e in entities]

    # Run all flood functions (simulating a full animation)
    flooded = flood.get_flooded_cells(grid, safe_cells)
    steps = flood.compute_flood_steps(grid, safe_cells)
    for i in range(COLS + 1):
        flood.cells_flooded_at(steps, i)

    # Build breakdown AFTER
    breakdown_after = scoring.build_score_breakdown(grid, entities, 40)
    flags_after = [(e["id"], e["connected"]) for e in entities]

    assert breakdown_before == breakdown_after
    assert flags_before == flags_after


# ---- Test 11: shelter cell is never flooded ----

def test_shelter_never_flooded():
    """The shelter cell never appears in any flooded set."""
    grid, entities, safe_cells = _make_connected_grid()
    shelter_pos = (0, 0)

    # Full flooded set
    flooded = flood.get_flooded_cells(grid, safe_cells)
    assert shelter_pos not in flooded

    # Step-by-step
    steps = flood.compute_flood_steps(grid, safe_cells)
    for i in range(COLS + 1):
        partial = flood.cells_flooded_at(steps, i)
        assert shelter_pos not in partial

