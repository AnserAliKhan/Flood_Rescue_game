"""
Unit tests for the campaign module.
Tests campaign state, level preparation, result recording, level progression,
final summary aggregation, and full 3-level campaign playthrough.
Pure logic: NO pygame window required.
"""
import pytest
import copy
from config import (
    NUM_LEVELS, SANDBAG_MARGIN, EFFICIENCY_BONUS_PER_SANDBAG,
    POINTS_PER_PERSON, LEVEL_BUILDINGS, LEVEL_POPULATION,
    PHASE_PLANNING, PHASE_CONFIRMING, PHASE_FLOODING, PHASE_RESULTS, PHASE_SUMMARY
)
import sandbags
import game
import baseline
import campaign


# ---- Test 1: create_campaign structure and bounds ----

def test_create_campaign():
    """create_campaign returns level 1, empty results, and validates bounds."""
    c = campaign.create_campaign()
    assert set(c.keys()) == {"level", "level_results"}
    assert c["level"] == 1
    assert c["level_results"] == {}

    # Valid start level
    c3 = campaign.create_campaign(start_level=3)
    assert c3["level"] == 3

    # Out of bounds
    with pytest.raises(ValueError):
        campaign.create_campaign(0)

    with pytest.raises(ValueError):
        campaign.create_campaign(4)


# ---- Test 2: prepare_level output and bounds ----

def test_prepare_level():
    """prepare_level returns (grid, entities, baseline, budget) with correct counts."""
    for lvl in range(1, NUM_LEVELS + 1):
        grid, entities, b_sandbags, budget = campaign.prepare_level(lvl)
        assert budget == b_sandbags + SANDBAG_MARGIN
        assert len(grid) == 10
        assert len(grid[0]) == 30

        # Building counts (exclude shelter)
        b_entities = [e for e in entities if e["type"] != "shelter"]
        assert len(b_entities) == sum(LEVEL_BUILDINGS[lvl].values())
        assert sum(e["population"] for e in entities) == LEVEL_POPULATION[lvl]

    with pytest.raises(ValueError):
        campaign.prepare_level(0)

    with pytest.raises(ValueError):
        campaign.prepare_level(NUM_LEVELS + 1)


# ---- Test 3: prepare_level determinism ----

def test_prepare_level_determinism():
    """prepare_level called twice for same level produces identical layout, baseline, and budget."""
    g1, e1, b1, bud1 = campaign.prepare_level(1)
    g2, e2, b2, bud2 = campaign.prepare_level(1)

    assert e1 == e2
    assert g1 == g2
    assert b1 == b2
    assert bud1 == bud2


# ---- Test 4: prepare_level difficulty progression ----

def test_prepare_level_difficulty():
    """Buildings and populations strictly increase from Level 1 to 3."""
    _, e1, _, _ = campaign.prepare_level(1)
    _, e2, _, _ = campaign.prepare_level(2)
    _, e3, _, _ = campaign.prepare_level(3)

    b1 = len([e for e in e1 if e["type"] != "shelter"])
    b2 = len([e for e in e2 if e["type"] != "shelter"])
    b3 = len([e for e in e3 if e["type"] != "shelter"])
    assert b1 < b2 < b3
    assert (b1, b2, b3) == (7, 9, 11)

    p1 = sum(e["population"] for e in e1)
    p2 = sum(e["population"] for e in e2)
    p3 = sum(e["population"] for e in e3)
    assert p1 < p2 < p3
    assert (p1, p2, p3) == (20, 30, 40)


# ---- Test 5: record_level_result stores deep copy ----

def test_record_level_result_copy():
    """Mutating the original breakdown dictionary does not alter campaign storage."""
    c = campaign.create_campaign(start_level=1)
    breakdown = {
        "passed": True,
        "final_score": 125,
        "saved_people": 20
    }

    campaign.record_level_result(c, breakdown)
    # Mutate original
    breakdown["final_score"] = 999

    assert c["level_results"][1]["final_score"] == 125


# ---- Test 6: record_level_result validation and error safety ----

def test_record_level_result_validation():
    """Raises ValueError if passed is False or level already recorded. Campaign untouched."""
    c = campaign.create_campaign(start_level=1)

    # 1. Failed breakdown
    with pytest.raises(ValueError, match="not passed"):
        campaign.record_level_result(c, {"passed": False, "final_score": 0})
    assert c["level_results"] == {}

    # 2. Record passed breakdown
    campaign.record_level_result(c, {"passed": True, "final_score": 125})
    assert 1 in c["level_results"]

    # 3. Duplicate record for same level
    with pytest.raises(ValueError, match="already been recorded"):
        campaign.record_level_result(c, {"passed": True, "final_score": 125})
    assert c["level_results"][1]["final_score"] == 125


# ---- Test 7: complete_level on Level 1 (returns 'next_level') ----

def test_complete_level_next_level():
    """complete_level on passed Level 1 increments level to 2 and returns 'next_level'."""
    c = campaign.create_campaign(start_level=1)
    state = {
        "phase": PHASE_RESULTS,
        "breakdown": {"passed": True, "final_score": 125, "saved_people": 20}
    }

    outcome = campaign.complete_level(c, state)
    assert outcome == "next_level"
    assert c["level"] == 2
    assert 1 in c["level_results"]


# ---- Test 8: complete_level on final level (returns 'summary') ----

def test_complete_level_summary():
    """complete_level on passed Level 3 keeps level at 3 and returns 'summary'."""
    c = campaign.create_campaign(start_level=3)
    state = {
        "phase": PHASE_RESULTS,
        "breakdown": {"passed": True, "final_score": 225, "saved_people": 40}
    }

    outcome = campaign.complete_level(c, state)
    assert outcome == "summary"
    assert c["level"] == 3
    assert 3 in c["level_results"]


# ---- Test 9: complete_level invalid states and error safety ----

def test_complete_level_invalid_states():
    """complete_level raises ValueError in non-results phases or unpassed states."""
    c = campaign.create_campaign(start_level=1)

    # Planning
    state_plan = {"phase": PHASE_PLANNING, "breakdown": None}
    with pytest.raises(ValueError, match="Cannot complete level"):
        campaign.complete_level(c, state_plan)
    assert c["level"] == 1
    assert c["level_results"] == {}

    # Confirming
    state_conf = {"phase": PHASE_CONFIRMING, "breakdown": None}
    with pytest.raises(ValueError):
        campaign.complete_level(c, state_conf)

    # Flooding
    state_flood = {"phase": PHASE_FLOODING, "breakdown": {"passed": True}}
    with pytest.raises(ValueError):
        campaign.complete_level(c, state_flood)

    # Summary
    state_sum = {"phase": PHASE_SUMMARY, "breakdown": {"passed": True}}
    with pytest.raises(ValueError):
        campaign.complete_level(c, state_sum)

    # Results with passed=False
    state_fail = {"phase": PHASE_RESULTS, "breakdown": {"passed": False}}
    with pytest.raises(ValueError):
        campaign.complete_level(c, state_fail)


# ---- Test 10: is_last_level and is_campaign_complete helpers ----

def test_is_last_level_and_complete():
    """is_last_level and is_campaign_complete correctness across stages."""
    c = campaign.create_campaign(start_level=1)
    assert campaign.is_last_level(c) is False
    assert campaign.is_campaign_complete(c) is False

    c["level_results"][1] = {"passed": True}
    c["level"] = 2
    assert campaign.is_last_level(c) is False
    assert campaign.is_campaign_complete(c) is False

    c["level_results"][2] = {"passed": True}
    c["level"] = 3
    assert campaign.is_last_level(c) is True
    assert campaign.is_campaign_complete(c) is False

    c["level_results"][3] = {"passed": True}
    assert campaign.is_last_level(c) is True
    assert campaign.is_campaign_complete(c) is True


# ---- Test 11: build_final_summary for full campaign ----

def test_build_final_summary_full():
    """Summary sums, row order, and efficiency match hand-calculated numbers."""
    c = campaign.create_campaign(start_level=1)
    c["level_results"] = {
        1: {
            "saved_people": 20, "total_population": 20,
            "sandbags_used": 24, "sandbags_allocated": 29,
            "population_score": 100, "efficiency_bonus": 25, "final_score": 125
        },
        2: {
            "saved_people": 30, "total_population": 30,
            "sandbags_used": 34, "sandbags_allocated": 39,
            "population_score": 150, "efficiency_bonus": 25, "final_score": 175
        },
        3: {
            "saved_people": 40, "total_population": 40,
            "sandbags_used": 35, "sandbags_allocated": 40,
            "population_score": 200, "efficiency_bonus": 25, "final_score": 225
        }
    }

    summary = campaign.build_final_summary(c)

    assert summary["levels_completed"] == 3
    assert [r["level"] for r in summary["rows"]] == [1, 2, 3]

    assert summary["total_score"] == 125 + 175 + 225  # 525
    assert summary["total_people_saved"] == 90
    assert summary["total_population"] == 90
    assert summary["sandbags_allocated"] == 29 + 39 + 40  # 108
    assert summary["sandbags_used"] == 24 + 34 + 35        # 93
    assert summary["sandbags_remaining"] == 108 - 93       # 15
    # 100 * 15 / 108 = 13.888... -> 13.9
    assert summary["efficiency_percent"] == 13.9


# ---- Test 12: build_final_summary for partial and empty campaigns ----

def test_build_final_summary_partial_and_empty():
    """Partial and empty campaigns build cleanly with 0.0 efficiency and no exceptions."""
    # 1. Empty campaign
    c_empty = campaign.create_campaign()
    s_empty = campaign.build_final_summary(c_empty)
    assert s_empty["levels_completed"] == 0
    assert s_empty["rows"] == []
    assert s_empty["total_score"] == 0
    assert s_empty["efficiency_percent"] == 0.0

    # 2. Partial campaign (Level 1 only)
    c_part = campaign.create_campaign()
    c_part["level_results"][1] = {
        "saved_people": 20, "total_population": 20,
        "sandbags_used": 20, "sandbags_allocated": 25,
        "population_score": 100, "efficiency_bonus": 25, "final_score": 125
    }
    s_part = campaign.build_final_summary(c_part)
    assert s_part["levels_completed"] == 1
    assert s_part["total_score"] == 125
    assert s_part["efficiency_percent"] == 20.0  # 100 * 5 / 25


# ---- Test 13: Full headless playthrough of all 3 levels (Score 525) ----

def test_full_headless_playthrough():
    """Full playthrough on levels 1..3 with baseline routes passes all and scores 525."""
    c = campaign.create_campaign(start_level=1)

    for expected_lvl in range(1, NUM_LEVELS + 1):
        assert c["level"] == expected_lvl
        grid, entities, b_sandbags, budget = campaign.prepare_level(c["level"])
        route = baseline.calculate_baseline_route(grid, entities)

        # Place baseline route
        for r, c_coord in route:
            sandbags.place_sandbag(grid, r, c_coord, budget)

        # Full game flow
        state = game.create_game_state()
        game.request_confirmation(state)
        breakdown = game.confirm_routes(state, grid, entities, budget)
        assert breakdown["passed"] is True
        assert breakdown["sandbags_remaining"] == SANDBAG_MARGIN

        game.finish_flood(state)
        outcome = campaign.complete_level(c, state)

        if expected_lvl < NUM_LEVELS:
            assert outcome == "next_level"
        else:
            assert outcome == "summary"
            game.show_summary(state)
            assert state["phase"] == PHASE_SUMMARY

    summary = campaign.build_final_summary(c)
    assert summary["levels_completed"] == 3
    assert summary["total_people_saved"] == 90

    # Expected formula: 450 (people points) + 3 * SANDBAG_MARGIN * EFFICIENCY_BONUS_PER_SANDBAG (75) = 525
    expected_total = (90 * POINTS_PER_PERSON) + (3 * SANDBAG_MARGIN * EFFICIENCY_BONUS_PER_SANDBAG)
    assert summary["total_score"] == expected_total  # 525


# ---- Test 14: Fail then retry leaves campaign untouched ----

def test_fail_then_retry():
    """Failing a level raises on complete_level; retry preserves layout; campaign untouched."""
    c = campaign.create_campaign(start_level=1)
    grid, entities, b_sandbags, budget = campaign.prepare_level(1)

    # Confirm with zero sandbags -> fails
    state = game.create_game_state()
    game.request_confirmation(state)
    breakdown = game.confirm_routes(state, grid, entities, budget)
    assert breakdown["passed"] is False

    game.finish_flood(state)

    # complete_level raises
    with pytest.raises(ValueError):
        campaign.complete_level(c, state)
    assert c["level_results"] == {}

    # Retry returns to planning with same entities
    game.retry_level(state, grid, entities)
    assert state["phase"] == PHASE_PLANNING
    assert c["level_results"] == {}
    assert c["level"] == 1


# ---- Test 15: Pass then retry then fail records nothing until Continue ----

def test_pass_then_retry_then_fail():
    """Passing without clicking Continue records nothing; retrying and failing stores nothing."""
    c = campaign.create_campaign(start_level=1)
    grid, entities, b_sandbags, budget = campaign.prepare_level(1)
    route = baseline.calculate_baseline_route(grid, entities)

    for r, c_coord in route:
        sandbags.place_sandbag(grid, r, c_coord, budget)

    state = game.create_game_state()
    game.request_confirmation(state)
    game.confirm_routes(state, grid, entities, budget)
    game.finish_flood(state)

    # Player decides to RETRY instead of clicking Continue
    game.retry_level(state, grid, entities)
    assert c["level_results"] == {}

    # Now confirms with no sandbags (fails)
    game.request_confirmation(state)
    game.confirm_routes(state, grid, entities, budget)
    game.finish_flood(state)

    assert state["breakdown"]["passed"] is False
    with pytest.raises(ValueError):
        campaign.complete_level(c, state)
    assert c["level_results"] == {}


# ---- Test 16: Restart campaign independence ----

def test_restart_independence():
    """New campaign is independent of old one; Level 1 seed gives identical layout."""
    c1 = campaign.create_campaign(start_level=1)
    c1["level_results"][1] = {"passed": True, "final_score": 125}

    # Play again creates new campaign
    c2 = campaign.create_campaign(start_level=1)
    assert c2["level_results"] == {}

    # Mutating c1 does not affect c2
    c1["level_results"][2] = {"passed": True}
    assert 2 not in c2["level_results"]

    # Level 1 layout is identical
    g1, e1, b1, bud1 = campaign.prepare_level(1)
    g2, e2, b2, bud2 = campaign.prepare_level(1)
    assert e1 == e2
    assert bud1 == bud2


# ---- Test 17: Monkeypatch SANDBAG_MARGIN adjusts budgets ----

def test_sandbag_margin_monkeypatch(monkeypatch):
    """Monkeypatching SANDBAG_MARGIN adjusts prepared budgets accordingly."""
    import config
    monkeypatch.setattr(config, "SANDBAG_MARGIN", 10)

    _, _, baseline_val, budget = campaign.prepare_level(1)
    assert budget == baseline_val + 10

