"""
Unit tests for the baseline module.
Tests the greedy shortest-path heuristic, multi-source BFS,
shared path reduction, relay buildings, budget calculation,
upper-bound invariants, and end-to-end game scoring integration.
Pure logic: NO pygame window required.
"""
import pytest
import copy
from config import (
    ROWS, COLS, CELL_EMPTY, CELL_SHELTER, CELL_HOUSE, CELL_SANDBAG,
    SANDBAG_MARGIN, EFFICIENCY_BONUS_PER_SANDBAG, TEST_LAYOUT,
    LEVEL_POPULATION
)
from grid import create_grid
from entities import place_entity, build_layout
import sandbags
import pathfinding
import scoring
import level_generator
import baseline


# ---- Test 1: Shelter only, no buildings ----

def test_shelter_only_no_buildings():
    """Shelter only with 0 buildings has baseline 0 and empty route."""
    grid = create_grid(ROWS, COLS)
    entities = []
    place_entity(grid, entities, CELL_SHELTER, 5, 10)

    route = baseline.calculate_baseline_route(grid, entities)
    assert route == []
    assert baseline.calculate_baseline_sandbags(grid, entities) == 0


# ---- Test 2: Building directly next to shelter (Cost 0) ----

def test_building_adjacent_to_shelter():
    """A building directly adjacent to shelter requires 0 sandbags (Decision D3)."""
    grid = create_grid(ROWS, COLS)
    entities = []
    place_entity(grid, entities, CELL_SHELTER, 5, 10)
    place_entity(grid, entities, CELL_HOUSE, 5, 11)

    route = baseline.calculate_baseline_route(grid, entities)
    assert route == []
    assert baseline.calculate_baseline_sandbags(grid, entities) == 0


# ---- Test 3: Straight line single building ----

def test_single_building_straight_line():
    """Shelter at (5, 10), house at (5, 15) requires exactly 4 sandbags: (5,11) to (5,14)."""
    grid = create_grid(ROWS, COLS)
    entities = []
    place_entity(grid, entities, CELL_SHELTER, 5, 10)
    place_entity(grid, entities, CELL_HOUSE, 5, 15)

    route = baseline.calculate_baseline_route(grid, entities)
    assert route == [(5, 11), (5, 12), (5, 13), (5, 14)]
    assert baseline.calculate_baseline_sandbags(grid, entities) == 4


# ---- Test 4: Diagonal building ----

def test_diagonal_building():
    """Shelter at (5, 10), house at (6, 11) requires exactly 1 sandbag: (5, 11) or (6, 10)."""
    grid = create_grid(ROWS, COLS)
    entities = []
    place_entity(grid, entities, CELL_SHELTER, 5, 10)
    place_entity(grid, entities, CELL_HOUSE, 6, 11)

    route = baseline.calculate_baseline_route(grid, entities)
    assert len(route) == 1
    assert route[0] in {(5, 11), (6, 10)}
    assert baseline.calculate_baseline_sandbags(grid, entities) == 1


# ---- Test 5: Collinear chain (shared path) ----

def test_collinear_chain_shared_path():
    """Collinear chain shelter (5, 10), houses (5, 15) and (5, 20): baseline is 8, not 13."""
    grid = create_grid(ROWS, COLS)
    entities = []
    place_entity(grid, entities, CELL_SHELTER, 5, 10)
    place_entity(grid, entities, CELL_HOUSE, 5, 15)
    place_entity(grid, entities, CELL_HOUSE, 5, 20)

    route = baseline.calculate_baseline_route(grid, entities)
    # 4 bags from shelter to house 1 + 4 bags from house 1 to house 2 = 8 bags
    assert len(route) == 8
    assert baseline.calculate_baseline_sandbags(grid, entities) == 8
    assert baseline.route_connects_everything(grid, entities, route) is True


# ---- Test 6: Shared trunk ----

def test_shared_trunk():
    """Shelter (5, 5), houses (5, 15) and (5, 17): baseline is 10, not 20."""
    grid = create_grid(ROWS, COLS)
    entities = []
    place_entity(grid, entities, CELL_SHELTER, 5, 5)
    place_entity(grid, entities, CELL_HOUSE, 5, 15)
    place_entity(grid, entities, CELL_HOUSE, 5, 17)

    route = baseline.calculate_baseline_route(grid, entities)
    # Shelter to house 1 is 9 bags (cols 6..14). House 1 to house 2 is 1 bag (col 16).
    assert len(route) == 10
    assert baseline.calculate_baseline_sandbags(grid, entities) == 10
    assert baseline.route_connects_everything(grid, entities, route) is True


# ---- Test 7: Branching route ----

def test_branching_route():
    """Shelter (5, 10), houses (5, 15) and (2, 13): baseline is 6, route contains (4, 13) and (3, 13)."""
    grid = create_grid(ROWS, COLS)
    entities = []
    place_entity(grid, entities, CELL_SHELTER, 5, 10)
    place_entity(grid, entities, CELL_HOUSE, 5, 15)
    place_entity(grid, entities, CELL_HOUSE, 2, 13)

    route = baseline.calculate_baseline_route(grid, entities)
    # Nearest is (5, 15) at cost 4. Branch to (2, 13) takes 2 bags: (4, 13), (3, 13).
    assert len(route) == 6
    assert (4, 13) in route
    assert (3, 13) in route
    assert baseline.calculate_baseline_sandbags(grid, entities) == 6
    assert baseline.route_connects_everything(grid, entities, route) is True


# ---- Test 8: Relay building (Decision D3) ----

def test_relay_building():
    """Shelter (5, 10), houses (5, 15) and (5, 16): baseline is 4 (house 2 touches house 1)."""
    grid = create_grid(ROWS, COLS)
    entities = []
    place_entity(grid, entities, CELL_SHELTER, 5, 10)
    place_entity(grid, entities, CELL_HOUSE, 5, 15)
    place_entity(grid, entities, CELL_HOUSE, 5, 16)

    route = baseline.calculate_baseline_route(grid, entities)
    assert len(route) == 4
    assert baseline.calculate_baseline_sandbags(grid, entities) == 4
    assert baseline.route_connects_everything(grid, entities, route) is True


# ---- Test 9: bfs_to_nearest_target unit behavior ----

def test_bfs_unit_behavior():
    """bfs_to_nearest_target finds nearest of two targets, handles cost-0, and handles empty targets."""
    grid = create_grid(ROWS, COLS)

    # 1. Finds nearest of two targets
    sources = {(5, 10)}
    targets = {(5, 12), (5, 20)}  # (5, 12) is 1 cell away, (5, 20) is 9 cells away
    result = baseline.bfs_to_nearest_target(grid, sources, targets)
    assert result is not None
    path, reached = result
    assert reached == (5, 12)
    assert path == [(5, 11)]

    # 2. Target touching source yields empty path (cost 0)
    sources = {(5, 10)}
    targets = {(5, 11)}
    result = baseline.bfs_to_nearest_target(grid, sources, targets)
    assert result == ([], (5, 11))

    # 3. Empty targets yields None
    assert baseline.bfs_to_nearest_target(grid, sources, set()) is None


# ---- Test 10: Route properties across layouts ----

def test_route_properties():
    """Route has no duplicates, all cells were empty, none is entity, len == baseline."""
    layouts = [
        [(CELL_SHELTER, 5, 10), (CELL_HOUSE, 5, 15)],
        [(CELL_SHELTER, 5, 10), (CELL_HOUSE, 5, 15), (CELL_HOUSE, 2, 13)],
        [(CELL_SHELTER, 5, 5), (CELL_HOUSE, 5, 15), (CELL_HOUSE, 5, 17)]
    ]
    for layout in layouts:
        grid = create_grid(ROWS, COLS)
        entities = build_layout(grid, layout)
        route = baseline.calculate_baseline_route(grid, entities)

        # No duplicate cells
        assert len(route) == len(set(route))

        # Every cell in route was CELL_EMPTY
        entity_coords = {(e["row"], e["col"]) for e in entities}
        for r, c in route:
            assert (r, c) not in entity_coords
            assert grid[r][c] == CELL_EMPTY

        # Length matches baseline
        assert len(route) == baseline.calculate_baseline_sandbags(grid, entities)


# ---- Test 11: route_connects_everything helper and purity ----

def test_route_connects_everything():
    """route_connects_everything is True for baseline, False for empty, and leaves inputs unchanged."""
    grid = create_grid(ROWS, COLS)
    entities = []
    place_entity(grid, entities, CELL_SHELTER, 5, 10)
    place_entity(grid, entities, CELL_HOUSE, 5, 15)

    route = baseline.calculate_baseline_route(grid, entities)

    grid_before = copy.deepcopy(grid)
    entities_before = copy.deepcopy(entities)

    # Valid route connects everything
    assert baseline.route_connects_everything(grid, entities, route) is True

    # Empty route fails
    assert baseline.route_connects_everything(grid, entities, []) is False

    # Original grid and entities are unchanged
    assert grid == grid_before
    assert entities == entities_before
    assert all(e["connected"] is None for e in entities if e["type"] != CELL_SHELTER)


# ---- Test 12: Upper-bound check against independent direct distances ----

def test_upper_bound_invariant():
    """
    Greedy heuristic is an upper bound on true minimum, and is guaranteed to be <=
    the sum of independent shelter-to-building shortest paths, because the network
    only expands (new buildings can connect to existing sandbags or buildings).
    """
    for lvl in (1, 2, 3):
        grid, entities = level_generator.generate_level(lvl)
        shelter = [e for e in entities if e["type"] == CELL_SHELTER][0]
        buildings = [e for e in entities if e["type"] != CELL_SHELTER]

        # Calculate sum of direct distances from shelter alone
        independent_sum = 0
        for b in buildings:
            res = baseline.bfs_to_nearest_target(
                grid,
                {(shelter["row"], shelter["col"])},
                {(b["row"], b["col"])}
            )
            assert res is not None
            path, _ = res
            independent_sum += len(path)

        actual_baseline = baseline.calculate_baseline_sandbags(grid, entities)
        assert actual_baseline <= independent_sum


# ---- Test 13: Determinism and entity list order independence ----

def test_determinism_and_entity_order_independence():
    """Identical routes are generated regardless of the order of entities in the list."""
    grid1 = create_grid(ROWS, COLS)
    entities1 = []
    place_entity(grid1, entities1, CELL_SHELTER, 5, 10)
    place_entity(grid1, entities1, CELL_HOUSE, 5, 15)
    place_entity(grid1, entities1, CELL_HOUSE, 2, 13)

    grid2 = create_grid(ROWS, COLS)
    entities2 = []
    place_entity(grid2, entities2, CELL_HOUSE, 2, 13)
    place_entity(grid2, entities2, CELL_HOUSE, 5, 15)
    place_entity(grid2, entities2, CELL_SHELTER, 5, 10)

    route1 = baseline.calculate_baseline_route(grid1, entities1)
    route2 = baseline.calculate_baseline_route(grid2, entities2)
    assert route1 == route2


# ---- Test 14: Error handling on missing shelter or pre-paved sandbag ----

def test_error_handling():
    """Raises ValueError if no shelter exists or if grid already has sandbags."""
    # 1. No shelter
    grid = create_grid(ROWS, COLS)
    entities = []
    place_entity(grid, entities, CELL_HOUSE, 5, 15)
    with pytest.raises(ValueError, match="shelter"):
        baseline.calculate_baseline_route(grid, entities)

    # 2. Grid already contains sandbag
    grid = create_grid(ROWS, COLS)
    entities = []
    place_entity(grid, entities, CELL_SHELTER, 5, 10)
    place_entity(grid, entities, CELL_HOUSE, 5, 15)
    grid[0][0] = CELL_SANDBAG

    with pytest.raises(ValueError, match="sandbag"):
        baseline.calculate_baseline_route(grid, entities)

    # Grid is unchanged after error
    assert grid[0][0] == CELL_SANDBAG


# ---- Test 15: calculate_sandbag_budget formula and margin ----

def test_sandbag_budget_formula(monkeypatch):
    """calculate_sandbag_budget returns baseline + SANDBAG_MARGIN; raises on negative baseline."""
    assert baseline.calculate_sandbag_budget(10) == 10 + SANDBAG_MARGIN

    # Monkeypatch margin
    import config
    monkeypatch.setattr(config, "SANDBAG_MARGIN", 12)
    assert baseline.calculate_sandbag_budget(10) == 22

    with pytest.raises(ValueError, match="negative"):
        baseline.calculate_sandbag_budget(-1)


# ---- Test 16: End-to-end integration for default seeds (Levels 1, 2, 3) ----

@pytest.mark.parametrize("lvl", [1, 2, 3])
def test_end_to_end_default_seed_levels(lvl):
    """Paving baseline route succeeds with budget, rescues all, and awards bonus."""
    grid, entities = level_generator.generate_level(lvl)
    b_sandbags = baseline.calculate_baseline_sandbags(grid, entities)
    budget = baseline.calculate_sandbag_budget(b_sandbags)

    route = baseline.calculate_baseline_route(grid, entities)

    # Pave every route cell using place_sandbag with the calculated budget
    for r, c in route:
        sandbags.place_sandbag(grid, r, c, budget)

    # Evaluate connectivity and scoring
    pathfinding.evaluate_connectivity(grid, entities)
    breakdown = scoring.build_score_breakdown(grid, entities, budget)

    assert breakdown["passed"] is True
    assert breakdown["saved_people"] == LEVEL_POPULATION[lvl]
    assert breakdown["sandbags_remaining"] == SANDBAG_MARGIN
    assert breakdown["efficiency_bonus"] == SANDBAG_MARGIN * EFFICIENCY_BONUS_PER_SANDBAG
    assert breakdown["final_score"] == (LEVEL_POPULATION[lvl] * 5) + (SANDBAG_MARGIN * 5)


# ---- Test 17: Stress test across 200 seeds ----

def test_stress_200_seeds():
    """Stress test: 200 seeds on levels 1, 2, 3 all generate valid routes that connect everything."""
    for lvl in (1, 2, 3):
        for seed in range(200):
            grid, entities = level_generator.generate_level(lvl, seed=seed)
            route = baseline.calculate_baseline_route(grid, entities)
            assert baseline.route_connects_everything(grid, entities, route) is True
            assert len(route) == baseline.calculate_baseline_sandbags(grid, entities)


# ---- Test 18: Budget enforces placement limits ----

def test_budget_enforces_limit():
    """Placing one more sandbag than the calculated budget raises ValueError."""
    grid, entities = level_generator.generate_level(1)
    b_sandbags = baseline.calculate_baseline_sandbags(grid, entities)
    budget = baseline.calculate_sandbag_budget(b_sandbags)

    route = baseline.calculate_baseline_route(grid, entities)
    for r, c in route:
        sandbags.place_sandbag(grid, r, c, budget)

    # Now remaining sandbags is exactly SANDBAG_MARGIN (5). Place 5 more:
    placed = 0
    for r in range(ROWS):
        for c in range(COLS):
            if grid[r][c] == CELL_EMPTY:
                sandbags.place_sandbag(grid, r, c, budget)
                placed += 1
                if placed == SANDBAG_MARGIN:
                    break
        if placed == SANDBAG_MARGIN:
            break

    # Budget is now fully exhausted; placing 1 more must raise ValueError
    with pytest.raises(ValueError, match="budget"):
        for r in range(ROWS):
            for c in range(COLS):
                if grid[r][c] == CELL_EMPTY:
                    sandbags.place_sandbag(grid, r, c, budget)

