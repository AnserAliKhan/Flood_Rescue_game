"""
tests/test_fuzz_playthrough.py - Fuzz Testing and System Invariants (F12)

Simulates hundreds of randomized playthroughs across all campaign levels,
exercising random sandbag placements, confirmations, flood completions, and retries.
Validates fundamental mathematical and structural invariants across all trials.
"""

import random
import pytest
import config
from config import (
    ROWS, COLS, CELL_SHELTER, CELL_SANDBAG, SANDBAG_MARGIN, LEVEL_SEEDS
)
import campaign
import sandbags
import game
import flood
import baseline
import level_generator


@pytest.mark.parametrize("level_num", [1, 2, 3])
def test_fuzz_random_playthrough_invariants(level_num):
    """
    Fuzzes 100 random playthroughs per level (seeds 0..99).
    Places random sandbags up to budget, executes complete game phase flow,
    and asserts mathematical invariants and state consistency.
    """
    for seed in range(100):
        rng = random.Random(seed)

        # 1. Setup fresh level
        game_grid, entities_list, baseline_val, budget = campaign.prepare_level(level_num)
        initial_entities = [dict(e) for e in entities_list]

        # 2. Place random legal sandbags
        num_attempts = rng.randint(0, budget + 10)
        for _ in range(num_attempts):
            r = rng.randint(0, ROWS - 1)
            c = rng.randint(0, COLS - 1)
            try:
                sandbags.place_sandbag(game_grid, r, c, budget)
            except ValueError:
                pass  # Ignore invalid placements (out of budget, occupied, etc.)

        # 3. Create state and execute full game flow
        state = game.create_game_state()
        game.request_confirmation(state)
        game.confirm_routes(state, game_grid, entities_list, budget)
        game.finish_flood(state)

        breakdown = state["breakdown"]

        # 4. Assert Mathematical & Logical Invariants
        # Invariant A: Conservation of population
        assert breakdown["saved_people"] + breakdown["unsaved_people"] == breakdown["total_population"]

        # Invariant B: Conservation of sandbag budget
        assert breakdown["sandbags_used"] + breakdown["sandbags_remaining"] == breakdown["sandbags_allocated"]
        assert breakdown["sandbags_allocated"] == budget

        # Invariant C: Final score summation
        assert breakdown["final_score"] == breakdown["population_score"] + breakdown["efficiency_bonus"]

        # Invariant D: Efficiency bonus rule (Amended Decision D5)
        if not breakdown["passed"]:
            assert breakdown["efficiency_bonus"] == 0
        else:
            assert breakdown["efficiency_bonus"] == breakdown["sandbags_remaining"] * config.EFFICIENCY_BONUS_PER_SANDBAG

        # Invariant E: Passed definition
        assert breakdown["passed"] == (breakdown["unsaved_people"] == 0)

        # Invariant F: Grid integrity (exactly 300 cells)
        assert len(game_grid) == ROWS
        assert all(len(row) == COLS for row in game_grid)

        # Invariant G: Entity cell integrity
        for orig in initial_entities:
            assert game_grid[orig["row"]][orig["col"]] == orig["type"]

        # Invariant H: Entity connectivity flags evaluated
        for e in entities_list:
            if e["type"] != CELL_SHELTER:
                assert e["connected"] in (True, False)

        # Invariant I: Exact disjoint partition of all 300 cells (safe vs flooded)
        safe_cells = state["safe_cells"]
        flooded_cells = flood.get_flooded_cells(game_grid, safe_cells)
        assert safe_cells.isdisjoint(flooded_cells)
        assert len(safe_cells | flooded_cells) == ROWS * COLS == 300

        # 5. Retry Level cleans grid and restores identical layout
        game.retry_level(state, game_grid, entities_list)
        assert sandbags.count_sandbags(game_grid) == 0
        assert state["phase"] == config.PHASE_PLANNING
        assert state["breakdown"] is None
        assert state["safe_cells"] is None
        for e in entities_list:
            if e["type"] != CELL_SHELTER:
                assert e["connected"] is None


@pytest.mark.parametrize("level_num", [1, 2, 3])
def test_fuzz_baseline_solution_always_passes(level_num):
    """
    Fuzzes 50 level seeds per level, verifying that applying the greedy baseline route
    always connects 100% of civilians, passes the level, and leaves exactly SANDBAG_MARGIN unused.
    """
    for seed in range(50):
        # Generate arbitrary seed level
        test_seed = LEVEL_SEEDS[level_num] + 500 + seed
        g, ents = level_generator.generate_level(level_num, test_seed)
        base_route = baseline.calculate_baseline_route(g, ents)
        base_cost = len(base_route)
        budget = baseline.calculate_sandbag_budget(base_cost)

        # Place the baseline route onto the grid
        for r, c in base_route:
            g[r][c] = CELL_SANDBAG

        state = game.create_game_state()
        game.request_confirmation(state)
        game.confirm_routes(state, g, ents, budget)
        game.finish_flood(state)

        breakdown = state["breakdown"]

        # Baseline route guarantees 100% salvation
        assert breakdown["passed"] is True
        assert breakdown["saved_people"] == breakdown["total_population"]
        assert breakdown["unsaved_people"] == 0
        assert breakdown["sandbags_remaining"] == SANDBAG_MARGIN
        assert breakdown["efficiency_bonus"] == SANDBAG_MARGIN * config.EFFICIENCY_BONUS_PER_SANDBAG
