import pytest
from game import (
    create_game_state, change_phase, is_editing_allowed,
    request_confirmation, cancel_confirmation, confirm_routes,
    can_continue, retry_level, bonus_explanation
)
from grid import create_grid
from entities import place_entity, build_layout
from config import (
    PHASE_PLANNING, PHASE_CONFIRMING, PHASE_RESULTS,
    CELL_SHELTER, CELL_HOUSE, TEST_SANDBAG_BUDGET
)

def test_initial_state():
    """Verify create_game_state starts in planning with no breakdown."""
    state = create_game_state()
    assert state["phase"] == PHASE_PLANNING
    assert state["breakdown"] is None

def test_transitions():
    """Verify legal and illegal phase transitions."""
    state = create_game_state()

    # Legal: Plan -> Confirm
    change_phase(state, PHASE_CONFIRMING)
    assert state["phase"] == PHASE_CONFIRMING

    # Legal: Confirm -> Results
    change_phase(state, PHASE_RESULTS)
    assert state["phase"] == PHASE_RESULTS

    # Legal: Results -> Plan
    change_phase(state, PHASE_PLANNING)
    assert state["phase"] == PHASE_PLANNING

    # Illegal: Plan -> Results
    with pytest.raises(ValueError):
        change_phase(state, PHASE_RESULTS)

    # Illegal: Results -> Confirm
    change_phase(state, PHASE_CONFIRMING)
    change_phase(state, PHASE_RESULTS)
    with pytest.raises(ValueError):
        change_phase(state, PHASE_CONFIRMING)

def test_editing_allowed():
    """Verify editing is only allowed in planning."""
    state = create_game_state()
    assert is_editing_allowed(state) is True

    change_phase(state, PHASE_CONFIRMING)
    assert is_editing_allowed(state) is False

    change_phase(state, PHASE_RESULTS)
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
    place_entity(grid, entities, CELL_HOUSE, 0, 1) # Connected

    state = create_game_state()
    change_phase(state, PHASE_CONFIRMING)

    breakdown = confirm_routes(state, grid, entities, 40)

    assert state["phase"] == PHASE_RESULTS
    assert state["breakdown"] == breakdown
    assert breakdown["passed"] is True
    assert entities[1]["connected"] is True

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

def test_can_continue():
    """Verify Continue button logic (only in results AND passed)."""
    state = create_game_state()

    # Planning
    assert can_continue(state) is False

    # Results - Passed
    state["phase"] = PHASE_RESULTS
    state["breakdown"] = {"passed": True}
    assert can_continue(state) is True

    # Results - Failed
    state["breakdown"] = {"passed": False}
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

    # Mark connected
    entities[1]["connected"] = True

    retry_level(state, grid, entities)

    assert state["phase"] == PHASE_PLANNING
    assert state["breakdown"] is None
    assert grid[0][1] == "empty" # sandbags cleared
    assert entities[1]["connected"] is None # flags reset
    assert len(entities) == 2 # buildings kept

def test_bonus_explanation():
    """Verify bonus message based on passed status."""
    assert "not everyone was saved" in bonus_explanation({"passed": False})
    assert "awarded" in bonus_explanation({"passed": True})

def test_full_cycle():
    """Test Plan -> Confirm -> Results -> Retry cycle."""
    grid = create_grid(10, 30)
    entities = []
    place_entity(grid, entities, CELL_SHELTER, 0, 0)
    place_entity(grid, entities, CELL_HOUSE, 0, 1)

    state = create_game_state()

    # First run (Success)
    request_confirmation(state)
    confirm_routes(state, grid, entities, 40)
    assert state["phase"] == PHASE_RESULTS
    assert state["breakdown"]["passed"] is True

    # Retry
    retry_level(state, grid, entities)
    assert state["phase"] == PHASE_PLANNING
    assert state["breakdown"] is None

    # Second run (Fail by removing connection)
    # (No sandbags, but house at 0,1 is adjacent so it's connected by default)
    # Let's move the house to (0, 2)
    entities[1]["row"], entities[1]["col"] = 0, 2
    grid[0][1] = "empty" # Ensure no sandbag

    request_confirmation(state)
    confirm_routes(state, grid, entities, 40)
    assert state["phase"] == PHASE_RESULTS
    assert state["breakdown"]["passed"] is False
