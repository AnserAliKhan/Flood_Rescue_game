import pytest
import scoring
import config
from grid import create_grid
from entities import place_entity, build_layout
from pathfinding import evaluate_connectivity
from sandbags import place_sandbag

def test_check_evaluated():
    """Verify ValueError is raised if connectivity is not evaluated."""
    grid = create_grid(config.ROWS, config.COLS)
    entities = []
    place_entity(grid, entities, config.CELL_SHELTER, 0, 0)
    place_entity(grid, entities, config.CELL_HOUSE, 1, 1)

    # Fresh layout has connected=None
    with pytest.raises(ValueError, match="Connectivity has not been evaluated"):
        scoring.check_evaluated(entities)

    # After evaluation, it should pass
    evaluate_connectivity(grid, entities)
    scoring.check_evaluated(entities)

def test_nobody_connected():
    """Nobody connected: saved 0, bonus 0, passed False, final score 0."""
    grid = create_grid(config.ROWS, config.COLS)
    entities = []
    place_entity(grid, entities, config.CELL_SHELTER, 0, 0)
    place_entity(grid, entities, config.CELL_HOUSE, 5, 5)

    evaluate_connectivity(grid, entities)
    breakdown = scoring.build_score_breakdown(grid, entities, 40)

    assert breakdown["saved_people"] == 0
    assert breakdown["unsaved_people"] == config.POPULATION["house"]
    assert breakdown["houses_connected"] == 0
    assert breakdown["passed"] is False
    assert breakdown["efficiency_bonus"] == 0
    assert breakdown["final_score"] == 0

def test_everybody_connected():
    """Everyone connected: saved = total, passed True, bonus calculated."""
    grid = create_grid(config.ROWS, config.COLS)
    entities = []
    place_entity(grid, entities, config.CELL_SHELTER, 0, 0)
    place_entity(grid, entities, config.CELL_HOUSE, 0, 1)

    evaluate_connectivity(grid, entities)
    # budget 10, used 0 (building next to shelter), remaining 10
    breakdown = scoring.build_score_breakdown(grid, entities, 10)

    expected_pop = config.POPULATION["house"]
    expected_bonus = 10 * config.EFFICIENCY_BONUS_PER_SANDBAG

    assert breakdown["saved_people"] == expected_pop
    assert breakdown["unsaved_people"] == 0
    assert breakdown["passed"] is True
    assert breakdown["efficiency_bonus"] == expected_bonus
    assert breakdown["final_score"] == (expected_pop * config.POINTS_PER_PERSON) + expected_bonus

def test_partial_connectivity():
    """Partial: some connected, some not -> bonus must be 0."""
    grid = create_grid(config.ROWS, config.COLS)
    entities = []
    place_entity(grid, entities, config.CELL_SHELTER, 0, 0)
    place_entity(grid, entities, config.CELL_HOUSE, 0, 1) # Connected
    place_entity(grid, entities, config.CELL_HOUSE, 5, 5) # Unconnected

    evaluate_connectivity(grid, entities)
    breakdown = scoring.build_score_breakdown(grid, entities, 40)

    assert breakdown["saved_people"] == config.POPULATION["house"]
    assert breakdown["unsaved_people"] == config.POPULATION["house"]
    assert breakdown["passed"] is False
    assert breakdown["efficiency_bonus"] == 0

def test_connected_by_type():
    """Verify count_connected_by_type reflects correct populations and types."""
    grid = create_grid(config.ROWS, config.COLS)
    entities = []
    place_entity(grid, entities, config.CELL_SHELTER, 0, 0)
    place_entity(grid, entities, config.CELL_SCHOOL, 0, 1)
    place_entity(grid, entities, config.CELL_HOSPITAL, 0, 2)
    place_entity(grid, entities, config.CELL_HOUSE, 5, 5) # Unconnected

    evaluate_connectivity(grid, entities)
    breakdown = scoring.build_score_breakdown(grid, entities, 40)

    assert breakdown["schools_connected"] == 1
    assert breakdown["hospitals_connected"] == 1
    assert breakdown["houses_connected"] == 0
    assert breakdown["saved_people"] == config.POPULATION["school"] + config.POPULATION["hospital"]

def test_old_spec_example():
    """Old SPEC example: 20 people, 16 saved, budget 20, 15 used."""
    # We simulate this by manually setting flags
    entities = [
        {"type": "house", "population": 2, "connected": True} for _ in range(8)
    ] + [
        {"type": "house", "population": 2, "connected": False} for _ in range(2)
    ]
    # Total population = 20. Saved = 16.

    grid = create_grid(config.ROWS, config.COLS)
    for _ in range(15): # 15 used
        # Find an empty cell to put a sandbag
        for r in range(config.ROWS):
            for c in range(config.COLS):
                if grid[r][c] == config.CELL_EMPTY:
                    grid[r][c] = config.CELL_SANDBAG
                    break
            else: continue
            break

    breakdown = scoring.build_score_breakdown(grid, entities, 20)

    assert breakdown["saved_people"] == 16
    assert breakdown["unsaved_people"] == 4
    assert breakdown["population_score"] == 80 # 16 * 5
    assert breakdown["efficiency_bonus"] == 0 # Not passed
    assert breakdown["final_score"] == 80
    assert breakdown["passed"] is False

def test_build_nothing_exploit():
    """A layout with no sandbags and far-away shelter gives bonus 0."""
    grid = create_grid(config.ROWS, config.COLS)
    entities = []
    place_entity(grid, entities, config.CELL_SHELTER, 0, 0)
    place_entity(grid, entities, config.CELL_HOUSE, 9, 29)

    evaluate_connectivity(grid, entities)
    breakdown = scoring.build_score_breakdown(grid, entities, 40)

    assert breakdown["sandbags_used"] == 0
    assert breakdown["sandbags_remaining"] == 40
    assert breakdown["passed"] is False
    assert breakdown["efficiency_bonus"] == 0
    assert breakdown["final_score"] == 0

def test_consistency_invariants():
    """Verify arithmetic invariants for different layouts."""
    for i in range(4):
        grid = create_grid(config.ROWS, config.COLS)
        entities = []
        place_entity(grid, entities, config.CELL_SHELTER, 0, 0)
        # Randomly place a building and some sandbags
        place_entity(grid, entities, config.CELL_HOUSE, 1 if i==0 else 2, 1)
        if i % 2 == 0:
            grid[0][1] = config.CELL_SANDBAG

        evaluate_connectivity(grid, entities)
        b = scoring.build_score_breakdown(grid, entities, 40)

        assert b["saved_people"] + b["unsaved_people"] == b["total_population"]
        assert b["sandbags_used"] + b["sandbags_remaining"] == b["sandbags_allocated"]
        assert b["final_score"] == b["population_score"] + b["efficiency_bonus"]
        if not b["passed"]:
            assert b["efficiency_bonus"] == 0
        else:
            assert b["efficiency_bonus"] == b["sandbags_remaining"] * config.EFFICIENCY_BONUS_PER_SANDBAG

def test_monkeypatch_weights(monkeypatch):
    """Verify that changing config constants updates the score."""
    monkeypatch.setattr(config, "POINTS_PER_PERSON", 10)
    monkeypatch.setattr(config, "EFFICIENCY_BONUS_PER_SANDBAG", 100)

    grid = create_grid(config.ROWS, config.COLS)
    entities = []
    place_entity(grid, entities, config.CELL_SHELTER, 0, 0)
    place_entity(grid, entities, config.CELL_HOUSE, 0, 1) # Connected

    evaluate_connectivity(grid, entities)
    breakdown = scoring.build_score_breakdown(grid, entities, 10)

    # saved = 2, pop_score = 2 * 10 = 20
    # remaining = 10, bonus = 10 * 100 = 1000
    assert breakdown["population_score"] == 20
    assert breakdown["efficiency_bonus"] == 1000
    assert breakdown["final_score"] == 1020

def test_immutability():
    """Verify build_score_breakdown does not modify grid or entities."""
    grid = create_grid(config.ROWS, config.COLS)
    entities = []
    place_entity(grid, entities, config.CELL_SHELTER, 0, 0)
    place_entity(grid, entities, config.CELL_HOUSE, 0, 1)
    evaluate_connectivity(grid, entities)

    import copy
    grid_copy = copy.deepcopy(grid)
    entities_copy = copy.deepcopy(entities)

    scoring.build_score_breakdown(grid, entities, 40)

    assert grid == grid_copy
    assert entities == entities_copy

def test_is_level_passed_error():
    """Verify ValueError when no non-shelter entities exist."""
    entities = []
    place_entity(create_grid(10, 30), entities, config.CELL_SHELTER, 0, 0)
    with pytest.raises(ValueError, match="No buildings present"):
        scoring.is_level_passed(entities)
