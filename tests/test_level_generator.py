"""
Unit tests for the level_generator module.
Tests composition, constraints, random placement, solvability,
determinism, purity, and stress testing across many seeds.
Pure logic: NO pygame window required.
"""
import pytest
import random
import copy
from config import (
    ROWS, COLS, CELL_EMPTY, CELL_SHELTER, CELL_HOUSE, CELL_SCHOOL, CELL_HOSPITAL,
    LEVEL_BUILDINGS, LEVEL_POPULATION, LEVEL_SEEDS, LEVEL_REGIONS,
    POPULATION, DIRECTIONS
)
from grid import create_grid
from entities import place_entity, count_buildings, total_population
import pathfinding
import scoring
import level_generator


# ---- Test 1: get_level_composition returns D1 counts, raises on invalid levels ----

def test_level_composition_valid_and_invalid():
    """Verify D1 building counts for levels 1, 2, 3 and errors for 0 and 4."""
    assert level_generator.get_level_composition(1) == {"house": 5, "school": 2, "hospital": 0}
    assert level_generator.get_level_composition(2) == {"house": 6, "school": 2, "hospital": 1}
    assert level_generator.get_level_composition(3) == {"house": 7, "school": 2, "hospital": 2}

    with pytest.raises(ValueError):
        level_generator.get_level_composition(0)

    with pytest.raises(ValueError):
        level_generator.get_level_composition(4)


# ---- Test 2: population mismatch raises ValueError ----

def test_level_composition_population_mismatch(monkeypatch):
    """If LEVEL_POPULATION is altered to mismatch building counts, ValueError is raised."""
    # Temporarily corrupt Level 1 population
    corrupted_pop = dict(LEVEL_POPULATION)
    corrupted_pop[1] = 999
    monkeypatch.setattr(level_generator, "LEVEL_POPULATION", corrupted_pop)

    with pytest.raises(ValueError, match="population"):
        level_generator.get_level_composition(1)


# ---- Test 3: generate_level counts, population, and single shelter ----

@pytest.mark.parametrize("lvl,exp_pop,exp_bldgs", [
    (1, 20, {"house": 5, "school": 2, "hospital": 0}),
    (2, 30, {"house": 6, "school": 2, "hospital": 1}),
    (3, 40, {"house": 7, "school": 2, "hospital": 2}),
])
def test_generate_level_counts_and_populations(lvl, exp_pop, exp_bldgs):
    """Grid has 300 cells, exactly 1 shelter, correct building counts, and correct population."""
    grid, entities = level_generator.generate_level(lvl)

    # 300 cells
    assert len(grid) == ROWS
    assert all(len(row) == COLS for row in grid)

    # Exactly 1 shelter
    shelters = [e for e in entities if e["type"] == CELL_SHELTER]
    assert len(shelters) == 1

    # Exact building counts
    b_counts = count_buildings(entities)
    assert b_counts == exp_bldgs

    # Total population
    assert total_population(entities) == exp_pop

    # Formula check: (2*houses) + (5*schools) + (8*hospitals)
    calc_pop = (
        b_counts["house"] * POPULATION["house"]
        + b_counts["school"] * POPULATION["school"]
        + b_counts["hospital"] * POPULATION["hospital"]
    )
    assert calc_pop == exp_pop


# ---- Test 4: grid entity consistency ----

def test_grid_entity_consistency():
    """Every entity's grid cell holds its type; non-empty cells equal entity count."""
    for lvl in (1, 2, 3):
        grid, entities = level_generator.generate_level(lvl)

        non_empty_count = sum(
            1 for r in range(ROWS) for c in range(COLS) if grid[r][c] != CELL_EMPTY
        )
        assert non_empty_count == len(entities)

        for e in entities:
            assert grid[e["row"]][e["col"]] == e["type"]


# ---- Test 5: no entity overlaps and all in bounds ----

def test_no_overlaps_and_in_bounds():
    """No two entities share a cell and none is out of bounds."""
    for lvl in (1, 2, 3):
        grid, entities = level_generator.generate_level(lvl)
        positions = set()
        for e in entities:
            r, c = e["row"], e["col"]
            assert 0 <= r < ROWS
            assert 0 <= c < COLS
            assert (r, c) not in positions
            positions.add((r, c))


# ---- Test 6: spacing rule (MIN_BUILDING_GAP = 1) ----

def test_spacing_rule():
    """No building or shelter has an orthogonal neighbor that is another entity."""
    for lvl in (1, 2, 3):
        grid, entities = level_generator.generate_level(lvl)
        entity_positions = {(e["row"], e["col"]) for e in entities}

        for r, c in entity_positions:
            for dr, dc in DIRECTIONS:
                neighbor = (r + dr, c + dc)
                assert neighbor not in entity_positions, (
                    f"Entity at ({r}, {c}) touches another entity at {neighbor} orthogonally"
                )


# ---- Test 7: region constraints ----

def test_region_constraints():
    """All buildings are in building_cols; shelter is in shelter_cols."""
    for lvl in (1, 2, 3):
        grid, entities = level_generator.generate_level(lvl)
        regions = LEVEL_REGIONS[lvl]
        b_cmin, b_cmax = regions["buildings_cols"]
        s_cmin, s_cmax = regions["shelter_cols"]

        for e in entities:
            if e["type"] == CELL_SHELTER:
                assert s_cmin <= e["col"] <= s_cmax
            else:
                assert b_cmin <= e["col"] <= b_cmax


# ---- Test 8: determinism with same and different seeds ----

def test_determinism_same_and_different_seeds():
    """Same seed gives identical layout; different seeds give different layouts."""
    g1, e1 = level_generator.generate_level(1, seed=42)
    g2, e2 = level_generator.generate_level(1, seed=42)
    assert e1 == e2
    assert g1 == g2

    # Different seeds should produce different layouts
    _, e_seed1 = level_generator.generate_level(1, seed=10)
    _, e_seed2 = level_generator.generate_level(1, seed=20)
    pos1 = [(e["row"], e["col"]) for e in e_seed1]
    pos2 = [(e["row"], e["col"]) for e in e_seed2]
    assert pos1 != pos2


# ---- Test 9: default seed equals LEVEL_SEEDS ----

def test_default_seed_uses_config():
    """seed=None gives the exact same result as passing LEVEL_SEEDS[level]."""
    for lvl in (1, 2, 3):
        g_default, e_default = level_generator.generate_level(lvl, seed=None)
        g_explicit, e_explicit = level_generator.generate_level(lvl, seed=LEVEL_SEEDS[lvl])
        assert e_default == e_explicit
        assert g_default == g_explicit


# ---- Test 10: global random state is untouched ----

def test_global_random_unmodified():
    """Calling generate_level does not affect the global random stream."""
    random.seed(999)
    first_val = random.random()

    # Reset seed and call generate_level in between
    random.seed(999)
    level_generator.generate_level(1)
    second_val = random.random()

    assert first_val == second_val


# ---- Test 11: stress test across 200 seeds ----

def test_stress_200_seeds():
    """Stress test: 200 seeds on all 3 levels. All pass constraints and solvability."""
    for lvl in (1, 2, 3):
        exp_pop = LEVEL_POPULATION[lvl]
        for seed in range(200):
            grid, entities = level_generator.generate_level(lvl, seed=seed)

            # Invariants
            assert total_population(entities) == exp_pop
            assert len(entities) == sum(LEVEL_BUILDINGS[lvl].values()) + 1
            assert level_generator.is_level_solvable(grid, entities) is True

            # Spacing
            positions = {(e["row"], e["col"]) for e in entities}
            for r, c in positions:
                for dr, dc in DIRECTIONS:
                    assert (r + dr, c + dc) not in positions


# ---- Test 12: neighbors_are_free behavior ----

def test_neighbors_are_free_behavior():
    """Isolated cell is True, adjacent to building is False, corners are handled correctly."""
    grid = create_grid(ROWS, COLS)

    # Empty grid cell
    assert level_generator.neighbors_are_free(grid, 5, 5) is True

    # Corner of empty grid
    assert level_generator.neighbors_are_free(grid, 0, 0) is True

    # Place a building at (5, 5)
    grid[5][5] = CELL_HOUSE

    # Orthogonal neighbor of building is NOT free
    assert level_generator.neighbors_are_free(grid, 5, 6) is False
    assert level_generator.neighbors_are_free(grid, 5, 4) is False
    assert level_generator.neighbors_are_free(grid, 4, 5) is False
    assert level_generator.neighbors_are_free(grid, 6, 5) is False

    # Diagonal neighbor IS free
    assert level_generator.neighbors_are_free(grid, 4, 4) is True
    assert level_generator.neighbors_are_free(grid, 6, 6) is True


# ---- Test 13: is_level_solvable cases ----

def test_is_level_solvable_cases():
    """Valid layout is True, blocked shelter is False, blocked building is False, ringed building is False."""
    # 1. Simple valid layout
    grid = create_grid(ROWS, COLS)
    entities = []
    place_entity(grid, entities, CELL_SHELTER, 5, 15)
    place_entity(grid, entities, CELL_HOUSE, 3, 10)
    assert level_generator.is_level_solvable(grid, entities) is True

    # 2. Shelter surrounded by buildings / edges (no empty orthogonal neighbor)
    g_shelter_blocked = create_grid(ROWS, COLS)
    e_shelter_blocked = []
    # Put shelter at corner (0,0) and block both orthogonal neighbors
    place_entity(g_shelter_blocked, e_shelter_blocked, CELL_SHELTER, 0, 0)
    place_entity(g_shelter_blocked, e_shelter_blocked, CELL_HOUSE, 0, 1)
    place_entity(g_shelter_blocked, e_shelter_blocked, CELL_HOUSE, 1, 0)
    assert level_generator.is_level_solvable(g_shelter_blocked, e_shelter_blocked) is False

    # 3. Building at corner surrounded by other buildings
    g_bldg_blocked = create_grid(ROWS, COLS)
    e_bldg_blocked = []
    place_entity(g_bldg_blocked, e_bldg_blocked, CELL_SHELTER, 5, 15)
    place_entity(g_bldg_blocked, e_bldg_blocked, CELL_HOUSE, 0, 0)
    place_entity(g_bldg_blocked, e_bldg_blocked, CELL_SCHOOL, 0, 1)
    place_entity(g_bldg_blocked, e_bldg_blocked, CELL_SCHOOL, 1, 0)
    assert level_generator.is_level_solvable(g_bldg_blocked, e_bldg_blocked) is False

    # 4. Building completely cut off by a closed ring of buildings
    # Put a house in corner (0,0) and a ring around it: (0,2), (1,2), (2,2), (2,1), (2,0)
    g_ring = create_grid(ROWS, COLS)
    e_ring = []
    place_entity(g_ring, e_ring, CELL_SHELTER, 8, 20)
    place_entity(g_ring, e_ring, CELL_HOUSE, 0, 0)
    for r, c in [(0, 2), (1, 2), (2, 2), (2, 1), (2, 0)]:
        place_entity(g_ring, e_ring, CELL_SCHOOL, r, c)
    assert level_generator.is_level_solvable(g_ring, e_ring) is False


# ---- Test 14: generator purity ----

def test_generator_purity():
    """is_level_solvable and helpers do not modify input grid/entities."""
    grid, entities = level_generator.generate_level(1)

    grid_copy = copy.deepcopy(grid)
    entities_copy = copy.deepcopy(entities)

    level_generator.is_level_solvable(grid, entities)
    level_generator.neighbors_are_free(grid, 5, 5)
    level_generator.is_valid_spot(grid, 5, 5, (0, 29), (0, 9))

    assert grid == grid_copy
    assert entities == entities_copy


# ---- Test 15: RuntimeError path on impossible constraints ----

def test_runtime_error_on_impossible_constraints(monkeypatch):
    """If MAX_LEVEL_RESTARTS is 1 and constraints are impossible, raises RuntimeError."""
    monkeypatch.setattr(level_generator, "MAX_LEVEL_RESTARTS", 1)
    # Impossible region: 0-width column region where multiple buildings cannot fit with spacing
    impossible_regions = {
        1: {"buildings_cols": (0, 0), "shelter_cols": (0, 0), "rows": (0, 0)},
    }
    monkeypatch.setattr(level_generator, "LEVEL_REGIONS", impossible_regions)

    with pytest.raises(RuntimeError, match="Failed to generate"):
        level_generator.generate_level(1)


# ---- Test 16: difficulty progression metrics ----

def test_difficulty_progression_metrics():
    """Verify 7 < 9 < 11 buildings, 20 < 30 < 40 pop, hospital strictly increases (0 -> 1 -> 2)."""
    c1 = level_generator.get_level_composition(1)
    c2 = level_generator.get_level_composition(2)
    c3 = level_generator.get_level_composition(3)

    b1 = sum(c1.values())
    b2 = sum(c2.values())
    b3 = sum(c3.values())
    assert b1 < b2 < b3
    assert (b1, b2, b3) == (7, 9, 11)

    assert LEVEL_POPULATION[1] < LEVEL_POPULATION[2] < LEVEL_POPULATION[3]
    assert (LEVEL_POPULATION[1], LEVEL_POPULATION[2], LEVEL_POPULATION[3]) == (20, 30, 40)

    # Hospital progression
    assert c1["hospital"] == 0
    assert c2["hospital"] == 1
    assert c3["hospital"] == 2
    assert c1["hospital"] < c2["hospital"] < c3["hospital"]


# ---- Test 17: integration with connectivity & scoring on empty board ----

def test_generated_level_integration_zero_sandbags():
    """With no sandbags placed, zero buildings are connected (due to spacing gap), score is 0."""
    for lvl in (1, 2, 3):
        grid, entities = level_generator.generate_level(lvl)

        visited = pathfinding.evaluate_connectivity(grid, entities)
        # Because of MIN_BUILDING_GAP, no building is adjacent to the shelter
        for e in entities:
            if e["type"] != CELL_SHELTER:
                assert e["connected"] is False

        breakdown = scoring.build_score_breakdown(grid, entities, 40)
        assert breakdown["saved_people"] == 0
        assert breakdown["passed"] is False
        assert breakdown["population_score"] == 0
        assert breakdown["efficiency_bonus"] == 0
        assert breakdown["final_score"] == 0

