"""
tests/test_spec_section15.py - Verification Suite for SPEC Section 15

Each test corresponds directly to one item from SPEC Section 15 ("Testing and Validation").
Tests build their own minimal fixtures or call relevant pure logic modules,
verifying that all core mechanics, connectivity rules, budgets, scoring,
difficulty progression, and state management satisfy the formal specification.
"""

import copy
import pytest
import config
from config import (
    ROWS, COLS, CELL_EMPTY, CELL_HOUSE, CELL_SCHOOL, CELL_HOSPITAL, CELL_SHELTER, CELL_SANDBAG,
    POINTS_PER_PERSON, EFFICIENCY_BONUS_PER_SANDBAG, SANDBAG_MARGIN,
    LEVEL_BUILDINGS, LEVEL_SEEDS, POPULATION
)
import grid
import entities
import sandbags
import pathfinding
import scoring
import level_generator
import baseline
import campaign
import game
import flood


# ---- Item 1: 300 cells ----

def test_15_01_grid_cell_count():
    """SPEC 15.1: Grid contains exactly 300 cells (10 rows x 30 cols)."""
    g = grid.create_grid(ROWS, COLS)
    assert len(g) == ROWS == 10
    assert all(len(row) == COLS == 30 for row in g)
    total_cells = sum(len(row) for row in g)
    assert total_cells == 300


# ---- Item 2: No building overlaps another ----

def test_15_02_no_building_overlaps():
    """SPEC 15.2: No building overlaps another building (default levels + 50 seeds)."""
    for lvl in range(1, 4):
        # 1. Default seeds
        g, ents = level_generator.generate_level(lvl, LEVEL_SEEDS[lvl])
        positions = [(e["row"], e["col"]) for e in ents]
        assert len(positions) == len(set(positions)), f"Overlap found on level {lvl} default seed"

        # 2. 50 random seeds per level
        for seed_offset in range(50):
            test_seed = LEVEL_SEEDS[lvl] + 1000 + seed_offset
            g_rnd, ents_rnd = level_generator.generate_level(lvl, test_seed)
            rnd_positions = [(e["row"], e["col"]) for e in ents_rnd]
            assert len(rnd_positions) == len(set(rnd_positions)), f"Overlap found on level {lvl} seed {test_seed}"


# ---- Item 3: Exactly one shelter per level ----

def test_15_03_exactly_one_shelter_per_level():
    """SPEC 15.3: Exactly one shelter is generated per level."""
    for lvl in range(1, 4):
        g, ents = level_generator.generate_level(lvl, LEVEL_SEEDS[lvl])
        shelters = [e for e in ents if e["type"] == CELL_SHELTER]
        assert len(shelters) == 1, f"Expected exactly 1 shelter on level {lvl}, found {len(shelters)}"


# ---- Item 4: Population totals are correct ----

def test_15_04_population_totals():
    """SPEC 15.4: Population totals are correct (Level 1: 20, Level 2: 30, Level 3: 40)."""
    expected_populations = {1: 20, 2: 30, 3: 40}
    for lvl, expected_pop in expected_populations.items():
        g, ents = level_generator.generate_level(lvl, LEVEL_SEEDS[lvl])
        total_pop = entities.total_population(ents)
        assert total_pop == expected_pop, f"Level {lvl} pop was {total_pop}, expected {expected_pop}"


# ---- Item 5: Sandbag budget calculation ----

def test_15_05_sandbag_budget_calculation():
    """
    SPEC 15.5: The sandbag budget is calculated correctly.
    Equals baseline + SANDBAG_MARGIN; on a hand-made layout, baseline matches hand-computed value.
    """
    # Hand-made layout: Shelter at (0, 0), House at (0, 4) -> 3 sandbag cells between them
    g = grid.create_grid(ROWS, COLS)
    ents = []
    entities.place_entity(g, ents, CELL_SHELTER, 0, 0)
    entities.place_entity(g, ents, CELL_HOUSE, 0, 4)

    hand_route = baseline.calculate_baseline_route(g, ents)
    hand_baseline = len(hand_route)
    assert hand_baseline == 3  # (0, 1), (0, 2), (0, 3)

    budget = baseline.calculate_sandbag_budget(hand_baseline)
    assert budget == 3 + SANDBAG_MARGIN


# ---- Item 6: Sandbags cannot be placed outside grid ----

def test_15_06_sandbag_cannot_be_placed_out_of_bounds():
    """SPEC 15.6: Sandbags cannot be placed outside the grid (including negative indexes)."""
    g = grid.create_grid(ROWS, COLS)
    out_of_bounds_coords = [(-1, 0), (0, -1), (10, 0), (0, 30), (-5, -5), (100, 100)]
    for r, c in out_of_bounds_coords:
        with pytest.raises(ValueError):
            sandbags.place_sandbag(g, r, c, 10)


# ---- Item 7: Sandbags cannot overwrite buildings ----

def test_15_07_sandbag_cannot_overwrite_buildings():
    """SPEC 15.7: Sandbags cannot overwrite buildings (house, school, hospital, shelter)."""
    g = grid.create_grid(ROWS, COLS)
    ents = []
    entities.place_entity(g, ents, CELL_SHELTER, 5, 5)
    entities.place_entity(g, ents, CELL_HOUSE, 5, 6)
    entities.place_entity(g, ents, CELL_SCHOOL, 5, 7)
    entities.place_entity(g, ents, CELL_HOSPITAL, 5, 8)

    for e in ents:
        with pytest.raises(ValueError):
            sandbags.place_sandbag(g, e["row"], e["col"], 10)


# ---- Item 8: Placing sandbag decreases remaining budget ----

def test_15_08_placement_decreases_remaining_budget():
    """SPEC 15.8: Sandbag placement decreases the remaining budget by one."""
    g = grid.create_grid(ROWS, COLS)
    total_budget = 10
    assert sandbags.remaining_sandbags(g, total_budget) == 10

    sandbags.place_sandbag(g, 1, 1, total_budget)
    assert sandbags.remaining_sandbags(g, total_budget) == 9

    sandbags.place_sandbag(g, 1, 2, total_budget)
    assert sandbags.remaining_sandbags(g, total_budget) == 8


# ---- Item 9: Removing sandbag restores budget ----

def test_15_09_removal_restores_remaining_budget():
    """SPEC 15.9: Removing a sandbag restores the budget by one."""
    g = grid.create_grid(ROWS, COLS)
    total_budget = 10
    sandbags.place_sandbag(g, 1, 1, total_budget)
    sandbags.place_sandbag(g, 1, 2, total_budget)
    assert sandbags.remaining_sandbags(g, total_budget) == 8

    sandbags.remove_sandbag(g, 1, 2)
    assert sandbags.remaining_sandbags(g, total_budget) == 9

    sandbags.remove_sandbag(g, 1, 1)
    assert sandbags.remaining_sandbags(g, total_budget) == 10


# ---- Item 10: Diagonal connections not accepted ----

def test_15_10_diagonal_connections_not_accepted():
    """SPEC 15.10: Diagonal connections are not accepted."""
    g = grid.create_grid(ROWS, COLS)
    ents = []
    entities.place_entity(g, ents, CELL_SHELTER, 0, 0)
    entities.place_entity(g, ents, CELL_HOUSE, 1, 1)  # Diagonally adjacent

    # Without sandbag
    connected_cells = pathfinding.find_connected_cells(g, 0, 0)
    assert (1, 1) not in connected_cells

    # Diagonal sandbag placed at (2, 2)
    g[2][2] = CELL_SANDBAG
    connected_cells = pathfinding.find_connected_cells(g, 0, 0)
    assert (1, 1) not in connected_cells


# ---- Item 11: Valid horizontal connections accepted ----

def test_15_11_horizontal_connections_accepted():
    """SPEC 15.11: Valid horizontal connections are accepted."""
    g = grid.create_grid(ROWS, COLS)
    ents = []
    entities.place_entity(g, ents, CELL_SHELTER, 3, 0)
    entities.place_entity(g, ents, CELL_HOUSE, 3, 3)

    # Place horizontal chain of sandbags at (3, 1) and (3, 2)
    g[3][1] = CELL_SANDBAG
    g[3][2] = CELL_SANDBAG

    connected_cells = pathfinding.find_connected_cells(g, 3, 0)
    assert (3, 3) in connected_cells


# ---- Item 12: Valid vertical connections accepted ----

def test_15_12_vertical_connections_accepted():
    """SPEC 15.12: Valid vertical connections are accepted."""
    g = grid.create_grid(ROWS, COLS)
    ents = []
    entities.place_entity(g, ents, CELL_SHELTER, 0, 4)
    entities.place_entity(g, ents, CELL_HOUSE, 3, 4)

    # Place vertical chain of sandbags at (1, 4) and (2, 4)
    g[1][4] = CELL_SANDBAG
    g[2][4] = CELL_SANDBAG

    connected_cells = pathfinding.find_connected_cells(g, 0, 4)
    assert (3, 4) in connected_cells


# ---- Item 13: Connected buildings marked safe ----

def test_15_13_connected_buildings_marked_safe():
    """SPEC 15.13: Buildings connected to the shelter are marked safe (connected=True)."""
    g = grid.create_grid(ROWS, COLS)
    ents = []
    entities.place_entity(g, ents, CELL_SHELTER, 0, 0)
    entities.place_entity(g, ents, CELL_HOUSE, 0, 2)
    g[0][1] = CELL_SANDBAG

    safe_cells = pathfinding.evaluate_connectivity(g, ents)
    assert ents[1]["connected"] is True
    assert (0, 2) in safe_cells


# ---- Item 14: Disconnected buildings marked unsafe ----

def test_15_14_disconnected_buildings_marked_unsafe():
    """SPEC 15.14: Disconnected buildings are marked unsafe (connected=False)."""
    g = grid.create_grid(ROWS, COLS)
    ents = []
    entities.place_entity(g, ents, CELL_SHELTER, 0, 0)
    entities.place_entity(g, ents, CELL_HOUSE, 5, 5)

    safe_cells = pathfinding.evaluate_connectivity(g, ents)
    assert ents[1]["connected"] is False
    assert (5, 5) not in safe_cells


# ---- Item 15: Population score calculation ----

def test_15_15_population_score_calculation():
    """SPEC 15.15: Population scores are calculated correctly (saved people x POINTS_PER_PERSON)."""
    # 7 people saved -> 7 * 5 = 35 points
    pop_score = scoring.calculate_population_score(7)
    assert pop_score == 7 * POINTS_PER_PERSON


# ---- Item 16: Efficiency bonus calculation (Amended D5) ----

def test_15_16_efficiency_bonus_calculation_amended_d5():
    """
    SPEC 15.16: Efficiency bonuses are calculated correctly.
    Under authoritative Decision D5 (which amends SPEC 9.2):
    bonus = remaining_sandbags * EFFICIENCY_BONUS_PER_SANDBAG only if ALL people are saved;
    otherwise bonus is 0.
    """
    # Case A: Everyone saved (all_saved=True) -> bonus awarded
    bonus_passed = scoring.calculate_efficiency_bonus(remaining_sandbags=6, all_saved=True)
    assert bonus_passed == 6 * EFFICIENCY_BONUS_PER_SANDBAG

    # Case B: Incomplete evacuation (all_saved=False) -> bonus strictly 0
    bonus_failed = scoring.calculate_efficiency_bonus(remaining_sandbags=6, all_saved=False)
    assert bonus_failed == 0


# ---- Item 17: Levels have increasing difficulty ----

def test_15_17_levels_increasing_difficulty():
    """
    SPEC 15.17: The three levels have increasing difficulty.
    Buildings: 7 < 9 < 11; Population: 20 < 30 < 40; Hospitals: 0 < 1 < 2.
    """
    counts = []
    pops = []
    hosps = []

    for lvl in (1, 2, 3):
        b_dict = LEVEL_BUILDINGS[lvl]
        total_bldgs = sum(b_dict.values())
        counts.append(total_bldgs)
        hosps.append(b_dict["hospital"])
        pop = (b_dict["house"] * POPULATION["house"] +
               b_dict["school"] * POPULATION["school"] +
               b_dict["hospital"] * POPULATION["hospital"])
        pops.append(pop)

    assert counts == [7, 9, 11]
    assert pops == [20, 30, 40]
    assert hosps == [0, 1, 2]


# ---- Item 18: Restart retains no old level data ----

def test_15_18_restart_retains_no_old_data():
    """
    SPEC 15.18: The game can be restarted without retaining old level data.
    After completing level 1, a fresh load has clean scores, empty grid, and identical layout (D4).
    """
    camp = campaign.create_campaign(start_level=1)
    g, ents, base, bud = campaign.prepare_level(1)
    state = game.create_game_state()

    # Place sandbag and confirm
    sandbags.place_sandbag(g, 1, 1, bud)
    game.request_confirmation(state)
    game.confirm_routes(state, g, ents, bud)
    game.finish_flood(state)
    assert len(state["safe_cells"]) > 0

    # Restart
    fresh_camp = campaign.create_campaign(start_level=1)
    fresh_g, fresh_ents, fresh_base, fresh_bud = campaign.prepare_level(1)
    fresh_state = game.create_game_state()

    # Assert clean restart
    assert fresh_camp["level_results"] == {}
    assert fresh_state["phase"] == config.PHASE_PLANNING
    assert fresh_state["breakdown"] is None
    assert fresh_state["safe_cells"] is None
    assert sandbags.count_sandbags(fresh_g) == 0
    assert all(e["connected"] is None for e in fresh_ents if e["type"] != CELL_SHELTER)

    # Determinism per D4: layout equals the original layout before sandbags were placed
    clean_g, clean_ents, _, _ = campaign.prepare_level(1)
    assert fresh_g == clean_g
    assert fresh_ents == clean_ents
    assert fresh_base == base
    assert fresh_bud == bud


# ---- Item 19: Flood animation does not affect score calculation ----

def test_15_19_flood_animation_does_not_affect_scoring():
    """
    SPEC 15.19: The flood animation does not interfere with the underlying score calculation.
    Breakdown before flood matches breakdown after all flood animation steps run on the same state.
    """
    g, ents, base, bud = campaign.prepare_level(1)
    state = game.create_game_state()

    game.request_confirmation(state)
    game.confirm_routes(state, g, ents, bud)

    breakdown_before = copy.deepcopy(state["breakdown"])

    # Simulate flood animation steps
    steps = flood.compute_flood_steps(g, state["safe_cells"])
    for s in range(COLS + 1):
        _ = flood.cells_flooded_at(steps, s)

    game.finish_flood(state)
    breakdown_after = state["breakdown"]

    assert breakdown_before == breakdown_after
