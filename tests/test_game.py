"""
Tests for the game state machine logic.
Updated in F07 to include the flooding phase.
No pygame window needed — all functions are pure logic.
"""
import pytest
from game import (
    create_game_state, change_phase, is_editing_allowed,
    request_confirmation, cancel_confirmation, confirm_routes,
    can_continue, retry_level, bonus_explanation, finish_flood,
    show_summary
)
from grid import create_grid
from entities import place_entity, build_layout
from config import (
    PHASE_PLANNING, PHASE_CONFIRMING, PHASE_FLOODING, PHASE_RESULTS, PHASE_SUMMARY,
    CELL_SHELTER, CELL_HOUSE, TEST_SANDBAG_BUDGET, ALLOWED_TRANSITIONS
)


# ---- F06 tests (updated for F07 flooding phase) ----

def test_initial_state():
    """Verify create_game_state starts in planning with no breakdown and no safe_cells."""
    state = create_game_state()
    assert state["phase"] == PHASE_PLANNING
    assert state["breakdown"] is None
    assert state["safe_cells"] is None


def test_transitions():
    """Verify legal and illegal phase transitions including flooding and summary."""
    state = create_game_state()

    # Legal: Plan -> Confirm
    change_phase(state, PHASE_CONFIRMING)
    assert state["phase"] == PHASE_CONFIRMING

    # Legal: Confirm -> Flooding (F07 change: was Confirm -> Results)
    change_phase(state, PHASE_FLOODING)
    assert state["phase"] == PHASE_FLOODING

    # Legal: Flooding -> Results
    change_phase(state, PHASE_RESULTS)
    assert state["phase"] == PHASE_RESULTS

    # Legal: Results -> Summary (F10)
    change_phase(state, PHASE_SUMMARY)
    assert state["phase"] == PHASE_SUMMARY

    # Illegal: Summary -> Planning or anything else (exiting summary requires new state)
    with pytest.raises(ValueError):
        change_phase(state, PHASE_PLANNING)

    # Reset for other checks
    state = create_game_state()

    # Legal: Plan -> Confirm -> Flooding -> Results -> Plan (Retry)
    change_phase(state, PHASE_CONFIRMING)
    change_phase(state, PHASE_FLOODING)
    change_phase(state, PHASE_RESULTS)
    change_phase(state, PHASE_PLANNING)
    assert state["phase"] == PHASE_PLANNING

    # Illegal: Plan -> Results (skipping confirm and flooding)
    with pytest.raises(ValueError):
        change_phase(state, PHASE_RESULTS)

    # Illegal: Plan -> Flooding (skipping confirm)
    with pytest.raises(ValueError):
        change_phase(state, PHASE_FLOODING)

    # Illegal: Plan -> Summary
    with pytest.raises(ValueError):
        change_phase(state, PHASE_SUMMARY)

    # Illegal: Confirm -> Results directly (must go through flooding now)
    change_phase(state, PHASE_CONFIRMING)
    with pytest.raises(ValueError):
        change_phase(state, PHASE_RESULTS)

    # Illegal: Confirm -> Summary
    with pytest.raises(ValueError):
        change_phase(state, PHASE_SUMMARY)

    # Illegal: Flooding -> Summary
    change_phase(state, PHASE_FLOODING)
    with pytest.raises(ValueError):
        change_phase(state, PHASE_SUMMARY)

    # Illegal: Results -> Confirm
    change_phase(state, PHASE_RESULTS)
    with pytest.raises(ValueError):
        change_phase(state, PHASE_CONFIRMING)


def test_editing_allowed():
    """Verify editing is only allowed in planning, not in confirming, flooding, results, or summary."""
    state = create_game_state()
    assert is_editing_allowed(state) is True

    change_phase(state, PHASE_CONFIRMING)
    assert is_editing_allowed(state) is False

    change_phase(state, PHASE_FLOODING)
    assert is_editing_allowed(state) is False

    change_phase(state, PHASE_RESULTS)
    assert is_editing_allowed(state) is False

    change_phase(state, PHASE_SUMMARY)
    assert is_editing_allowed(state) is False


def test_confirmation_flow():
    """Verify request and cancel confirmation."""
    state = create_game_state()
    request_confirmation(state)
    assert state["phase"] == PHASE_CONFIRMING

    cancel_confirmation(state)
    assert state["phase"] == PHASE_PLANNING


def test_confirm_routes_success():
    """Verify confirm_routes updates state and returns breakdown on a connected layout."""
    grid = create_grid(10, 30)
    entities = []
    place_entity(grid, entities, CELL_SHELTER, 0, 0)
    place_entity(grid, entities, CELL_HOUSE, 0, 1) # Connected (adjacent)

    state = create_game_state()
    change_phase(state, PHASE_CONFIRMING)

    breakdown = confirm_routes(state, grid, entities, 40)

    # F07: confirm_routes now goes to flooding, not results
    assert state["phase"] == PHASE_FLOODING
    assert state["breakdown"] == breakdown
    assert breakdown["passed"] is True
    assert entities[1]["connected"] is True
    # F07: safe_cells should be a set containing the shelter cell
    assert state["safe_cells"] is not None
    assert isinstance(state["safe_cells"], set)
    assert (0, 0) in state["safe_cells"]  # shelter is always safe


def test_confirm_routes_failure():
    """Verify confirm_routes raises ValueError and keeps state on failure."""
    grid = create_grid(10, 30)
    entities = []
    # No shelter
    place_entity(grid, entities, CELL_HOUSE, 0, 0)

    state = create_game_state()
    change_phase(state, PHASE_CONFIRMING)

    with pytest.raises(ValueError, match="shelter"):
        confirm_routes(state, grid, entities, 40)

    assert state["phase"] == PHASE_CONFIRMING
    assert state["breakdown"] is None
    assert state["safe_cells"] is None  # F07: safe_cells must also stay None


def test_can_continue():
    """Verify Continue button logic (only in results AND passed)."""
    state = create_game_state()

    # Planning
    assert can_continue(state) is False

    # Flooding (F07: must be False)
    state["phase"] = PHASE_FLOODING
    state["breakdown"] = {"passed": True}
    assert can_continue(state) is False

    # Results - Passed
    state["phase"] = PHASE_RESULTS
    state["breakdown"] = {"passed": True}
    assert can_continue(state) is True

    # Results - Failed
    state["breakdown"] = {"passed": False}
    assert can_continue(state) is False

    # Summary (F10: must be False)
    state["phase"] = PHASE_SUMMARY
    state["breakdown"] = {"passed": True}
    assert can_continue(state) is False


def test_retry_level():
    """Verify retry resets everything but keeps entities."""
    grid = create_grid(10, 30)
    entities = []
    place_entity(grid, entities, CELL_SHELTER, 0, 0)
    place_entity(grid, entities, CELL_HOUSE, 0, 1)
    grid[0][1] = "sandbag" # manually add

    state = create_game_state()
    state["phase"] = PHASE_RESULTS
    state["breakdown"] = {"passed": True}
    state["safe_cells"] = {(0, 0), (0, 1)}  # F07: set this too

    # Mark connected
    entities[1]["connected"] = True

    retry_level(state, grid, entities)

    assert state["phase"] == PHASE_PLANNING
    assert state["breakdown"] is None
    assert state["safe_cells"] is None  # F07: must be reset
    assert grid[0][1] == "empty" # sandbags cleared
    assert entities[1]["connected"] is None # flags reset
    assert len(entities) == 2 # buildings kept


def test_bonus_explanation():
    """Verify bonus message based on passed status."""
    assert "not everyone was saved" in bonus_explanation({"passed": False})
    assert "awarded" in bonus_explanation({"passed": True})


def test_full_cycle():
    """Test Plan -> Confirm -> Flooding -> Results -> Retry cycle."""
    grid = create_grid(10, 30)
    entities = []
    place_entity(grid, entities, CELL_SHELTER, 0, 0)
    place_entity(grid, entities, CELL_HOUSE, 0, 1)

    state = create_game_state()

    # First run (Success)
    request_confirmation(state)
    confirm_routes(state, grid, entities, 40)
    assert state["phase"] == PHASE_FLOODING  # F07: now flooding, not results
    assert state["safe_cells"] is not None

    # F07: finish the flood to get to results
    finish_flood(state)
    assert state["phase"] == PHASE_RESULTS
    assert state["breakdown"]["passed"] is True

    # Retry
    retry_level(state, grid, entities)
    assert state["phase"] == PHASE_PLANNING
    assert state["breakdown"] is None
    assert state["safe_cells"] is None

    # Second run (Fail by moving house away)
    entities[1]["row"], entities[1]["col"] = 0, 2
    grid[0][1] = "empty"

    request_confirmation(state)
    confirm_routes(state, grid, entities, 40)
    assert state["phase"] == PHASE_FLOODING

    finish_flood(state)
    assert state["phase"] == PHASE_RESULTS
    assert state["breakdown"]["passed"] is False


# ---- F07 new tests ----

def test_finish_flood_valid():
    """finish_flood in flooding phase sets results. Breakdown and safe_cells unchanged."""
    grid = create_grid(10, 30)
    entities = []
    place_entity(grid, entities, CELL_SHELTER, 0, 0)
    place_entity(grid, entities, CELL_HOUSE, 0, 1)

    state = create_game_state()
    change_phase(state, PHASE_CONFIRMING)
    confirm_routes(state, grid, entities, 40)
    assert state["phase"] == PHASE_FLOODING

    # Save references before finish_flood
    breakdown_before = state["breakdown"]
    safe_before = state["safe_cells"]

    finish_flood(state)

    assert state["phase"] == PHASE_RESULTS
    assert state["breakdown"] is breakdown_before  # same object, unchanged
    assert state["safe_cells"] is safe_before      # same object, unchanged


def test_finish_flood_invalid():
    """finish_flood outside flooding raises ValueError, state unchanged."""
    state = create_game_state()

    # Planning
    with pytest.raises(ValueError):
        finish_flood(state)
    assert state["phase"] == PHASE_PLANNING

    # Confirming
    change_phase(state, PHASE_CONFIRMING)
    with pytest.raises(ValueError):
        finish_flood(state)
    assert state["phase"] == PHASE_CONFIRMING

    # Results (need to go through flooding first)
    change_phase(state, PHASE_FLOODING)
    change_phase(state, PHASE_RESULTS)
    with pytest.raises(ValueError):
        finish_flood(state)
    assert state["phase"] == PHASE_RESULTS


def test_retry_resets_safe_cells():
    """After retry, state['safe_cells'] is None."""
    grid = create_grid(10, 30)
    entities = []
    place_entity(grid, entities, CELL_SHELTER, 0, 0)

    state = create_game_state()
    state["phase"] = PHASE_RESULTS
    state["breakdown"] = {"passed": False}
    state["safe_cells"] = {(0, 0)}

    retry_level(state, grid, entities)
    assert state["safe_cells"] is None


def test_retry_from_flooding_invalid():
    """retry_level from flooding raises ValueError (retry only from results)."""
    grid = create_grid(10, 30)
    entities = []
    place_entity(grid, entities, CELL_SHELTER, 0, 0)

    state = create_game_state()
    state["phase"] = PHASE_FLOODING

    with pytest.raises(ValueError):
        retry_level(state, grid, entities)
    assert state["phase"] == PHASE_FLOODING


def test_state_keys():
    """create_game_state() keys are exactly phase, breakdown, safe_cells."""
    state = create_game_state()
    assert set(state.keys()) == {"phase", "breakdown", "safe_cells"}


def test_all_transition_phases_defined():
    """Every phase in ALLOWED_TRANSITIONS (keys and values) is a defined PHASE_* constant."""
    defined_phases = {PHASE_PLANNING, PHASE_CONFIRMING, PHASE_FLOODING, PHASE_RESULTS, PHASE_SUMMARY}
    for key, targets in ALLOWED_TRANSITIONS.items():
        assert key in defined_phases, f"Key {key} is not a defined phase constant"
        for target in targets:
            assert target in defined_phases, f"Target {target} is not a defined phase constant"


# ---- F10: Summary Phase Tests ----

def test_show_summary_valid():
    """show_summary in results with passed=True transitions to summary phase."""
    state = create_game_state()
    state["phase"] = PHASE_RESULTS
    state["breakdown"] = {"passed": True, "saved_people": 20}

    show_summary(state)
    assert state["phase"] == PHASE_SUMMARY
    assert state["breakdown"]["passed"] is True


def test_show_summary_invalid():
    """show_summary outside results or without passed=True raises ValueError."""
    state = create_game_state()

    # 1. In planning phase
    with pytest.raises(ValueError, match="results phase"):
        show_summary(state)

    # 2. In results phase with passed=False
    state["phase"] = PHASE_RESULTS
    state["breakdown"] = {"passed": False}
    with pytest.raises(ValueError, match="passed level"):
        show_summary(state)
    assert state["phase"] == PHASE_RESULTS

    # 3. In results phase with breakdown=None
    state["breakdown"] = None
    with pytest.raises(ValueError, match="passed level"):
        show_summary(state)
    assert state["phase"] == PHASE_RESULTS


def test_summary_phase_restrictions():
    """In summary phase, editing and continue are disallowed; retry raises ValueError."""
    grid = create_grid(10, 30)
    entities = []
    place_entity(grid, entities, CELL_SHELTER, 0, 0)

    state = create_game_state()
    state["phase"] = PHASE_SUMMARY
    state["breakdown"] = {"passed": True}

    assert is_editing_allowed(state) is False
    assert can_continue(state) is False

    with pytest.raises(ValueError, match="results phase"):
        retry_level(state, grid, entities)
    assert state["phase"] == PHASE_SUMMARY
