import pytest
from config import (
    ROWS, COLS, CELL_SIZE, WINDOW_WIDTH, WINDOW_HEIGHT,
    POPULATION, LEVEL_BUILDINGS, LEVEL_POPULATION
)

def test_grid_size():
    """Check if the grid contains exactly 300 cells."""
    assert ROWS * COLS == 300

def test_grid_fits_window():
    """Check if the calculated grid pixels fit inside the window."""
    grid_width = COLS * CELL_SIZE
    grid_height = ROWS * CELL_SIZE
    assert grid_width <= WINDOW_WIDTH
    assert grid_height <= WINDOW_HEIGHT

def test_level_populations():
    """Check if population totals match LEVEL_POPULATION for all levels (D1)."""
    for level in range(1, 4):
        buildings = LEVEL_BUILDINGS[level]
        total_pop = sum(buildings[b_type] * POPULATION[b_type] for b_type in buildings)
        assert total_pop == LEVEL_POPULATION[level], f"Population mismatch for Level {level}"

def test_total_building_counts():
    """Check if total building counts are 7, 9, 11 for levels 1, 2, 3."""
    expected_counts = {1: 7, 2: 9, 3: 11}
    for level in range(1, 4):
        buildings = LEVEL_BUILDINGS[level]
        total_count = sum(buildings.values())
        assert total_count == expected_counts[level], f"Building count mismatch for Level {level}"

def test_hospital_progression():
    """Check if hospital count strictly increases from level 1 to 3."""
    h1 = LEVEL_BUILDINGS[1]["hospital"]
    h2 = LEVEL_BUILDINGS[2]["hospital"]
    h3 = LEVEL_BUILDINGS[3]["hospital"]
    assert h1 < h2 < h3, "Hospital count must strictly increase across levels"
