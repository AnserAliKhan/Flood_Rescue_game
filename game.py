"""
Game state machine logic.
Handles transitions between planning, confirming, flooding, and results phases.
Pure logic: NO pygame imports allowed.
"""
from config import (
    PHASE_PLANNING, PHASE_CONFIRMING, PHASE_FLOODING, PHASE_RESULTS,
    ALLOWED_TRANSITIONS, CELL_SHELTER, MSG_BONUS_DENIED, MSG_BONUS_AWARDED
)
import pathfinding
import scoring
import sandbags

def create_game_state():
    """
    Initializes the game state dictionary.
    Example: create_game_state() -> {'phase': 'planning', 'breakdown': None, 'safe_cells': None}
    """
    return {
        "phase": PHASE_PLANNING,
        "breakdown": None,
        "safe_cells": None
    }

def change_phase(state, new_phase):
    """
    Updates the game phase if the transition is allowed.
    Raises ValueError for illegal moves.
    Example: change_phase(state, 'confirming')
    """
    current_phase = state["phase"]
    if new_phase not in ALLOWED_TRANSITIONS.get(current_phase, []):
        raise ValueError(f"Illegal phase transition: {current_phase} to {new_phase}")

    state["phase"] = new_phase

def is_editing_allowed(state):
    """
    Returns True only if the player is currently in the planning phase.
    Example: is_editing_allowed(state) -> True
    """
    return state["phase"] == PHASE_PLANNING

def request_confirmation(state):
    """
    Transitions the game from planning to confirming.
    """
    change_phase(state, PHASE_CONFIRMING)

def cancel_confirmation(state):
    """
    Transitions the game from confirming back to planning.
    """
    change_phase(state, PHASE_PLANNING)

def confirm_routes(state, grid, entities, total_budget):
    """
    Executes connectivity evaluation and scoring, then transitions to flooding.
    The backend decides the result BEFORE the animation starts.
    Returns the breakdown dictionary.
    Example: confirm_routes(state, grid, entities, 40)
    """
    if state["phase"] != PHASE_CONFIRMING:
        raise ValueError("Confirmation can only happen in the confirming phase")

    # 1. Validate: Exactly one shelter must exist
    shelters = [e for e in entities if e["type"] == CELL_SHELTER]
    if len(shelters) != 1:
        raise ValueError("Game must have exactly one shelter to evaluate connectivity")

    # 2. Backend evaluation
    # This is the atomic operation: if any step fails, the phase remains 'confirming'
    visited = pathfinding.evaluate_connectivity(grid, entities)
    breakdown = scoring.build_score_breakdown(grid, entities, total_budget)

    # 3. Update state — store both breakdown AND safe set before the animation
    state["breakdown"] = breakdown
    state["safe_cells"] = visited
    change_phase(state, PHASE_FLOODING)

    return breakdown

def finish_flood(state):
    """
    Ends the flood animation and transitions to results.
    Only valid in the flooding phase. Changes nothing except the phase.
    Example: finish_flood(state)
    """
    if state["phase"] != PHASE_FLOODING:
        raise ValueError("finish_flood is only valid in the flooding phase")
    change_phase(state, PHASE_RESULTS)

def can_continue(state):
    """
    Returns True only in the results phase if the level was passed.
    """
    if state["phase"] != PHASE_RESULTS:
        return False

    return state["breakdown"]["passed"] if state["breakdown"] else False

def retry_level(state, grid, entities):
    """
    Resets the grid and connectivity flags, returning the game to planning.
    """
    if state["phase"] != PHASE_RESULTS:
        raise ValueError("Retry is only available in the results phase")

    # Clear sandbags
    sandbags.clear_sandbags(grid)

    # Reset connectivity flags to None
    for e in entities:
        if e["type"] != CELL_SHELTER:
            e["connected"] = None

    # Clear breakdown, safe cells, and transition
    state["breakdown"] = None
    state["safe_cells"] = None
    change_phase(state, PHASE_PLANNING)

def bonus_explanation(breakdown):
    """
    Returns a user-friendly explanation of the efficiency bonus.
    Example: bonus_explanation({'passed': False}) -> "No efficiency bonus: not everyone was saved"
    """
    if not breakdown or not breakdown["passed"]:
        return MSG_BONUS_DENIED

    return MSG_BONUS_AWARDED
