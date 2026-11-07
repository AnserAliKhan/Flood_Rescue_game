import pytest
from entities import (
    create_entity, place_entity, get_entity_at,
    get_entities_by_type, count_buildings, total_population, build_layout
)
from grid import create_grid
from config import (
    ROWS, COLS, POPULATION, CELL_SHELTER, CELL_HOUSE,
    CELL_SCHOOL, CELL_HOSPITAL, TEST_LAYOUT
)

def test_create_entity():
    """Verify entity dictionary keys and population values."""
    # House
    house = create_entity(0, CELL_HOUSE, 1, 3)
    assert house == {
        "id": 0, "type": CELL_HOUSE, "row": 1, "col": 3,
        "population": POPULATION["house"], "connected": None
    }
    # Shelter
    shelter = create_entity(1, CELL_SHELTER, 5, 15)
    assert shelter["population"] == 0
    assert shelter["connected"] is None

    # Unknown type
    with pytest.raises(ValueError):
        create_entity(2, "spaceship", 0, 0)

def test_place_entity_success():
    """Verify successful placement updates both grid and entities list."""
    grid = create_grid(ROWS, COLS)
    entities = []
    entity = place_entity(grid, entities, CELL_HOUSE, 1, 3)

    assert grid[1][3] == CELL_HOUSE
    assert len(entities) == 1
    assert entities[0] == entity
    assert entity["id"] == 0

def test_place_entity_failures():
    """Verify placement restrictions (occupied, bounds, second shelter)."""
    grid = create_grid(ROWS, COLS)
    entities = []

    # Valid first placement
    place_entity(grid, entities, CELL_HOUSE, 1, 3)

    # Occupied
    with pytest.raises(ValueError, match="occupied"):
        place_entity(grid, entities, CELL_HOUSE, 1, 3)

    # Out of bounds
    with pytest.raises(ValueError, match="out of bounds"):
        place_entity(grid, entities, CELL_HOUSE, -1, 0)
    with pytest.raises(ValueError, match="out of bounds"):
        place_entity(grid, entities, CELL_HOUSE, 10, 0)

    # Second shelter
    place_entity(grid, entities, CELL_SHELTER, 5, 15)
    with pytest.raises(ValueError, match="shelter already exists"):
        place_entity(grid, entities, CELL_SHELTER, 6, 16)

    # Verify grid/list unchanged after failures
    assert len(entities) == 2
    assert grid[1][3] == CELL_HOUSE

def test_get_entity_at():
    """Verify finding an entity by its position."""
    grid = create_grid(ROWS, COLS)
    entities = []
    place_entity(grid, entities, CELL_HOUSE, 1, 3)

    assert get_entity_at(entities, 1, 3)["type"] == CELL_HOUSE
    assert get_entity_at(entities, 0, 0) is None

def test_build_layout_consistency():
    """Verify consistency between entities list and grid for the test layout."""
    grid = create_grid(ROWS, COLS)
    entities = build_layout(grid, TEST_LAYOUT)

    # 1. Counts
    assert len(entities) == len(TEST_LAYOUT)
    assert count_buildings(entities) == {"house": 6, "school": 2, "hospital": 1}
    assert total_population(entities) == 30

    # 2. Consistency: every entity's grid cell holds its type
    for e in entities:
        assert grid[e["row"]][e["col"]] == e["type"]

    # 3. Consistency: number of non-empty cells == number of entities
    non_empty_cells = 0
    for row in grid:
        for cell in row:
            if cell != "empty":
                non_empty_cells += 1
    assert non_empty_cells == len(entities)

def test_layout_bounds():
    """Verify all positions in TEST_LAYOUT are inside the grid."""
    for _, row, col in TEST_LAYOUT:
        assert 0 <= row < ROWS
        assert 0 <= col < COLS
