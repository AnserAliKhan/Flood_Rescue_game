# Plan: F06 Game State Machine (Planning, Confirm, Results) with a Results Panel

## Context
This feature transforms the project from a set of tools into a structured game. It introduces a state machine to manage three phases: **Planning** (placing sandbags), **Confirming** (safety dialog), and **Results** (scoring breakdown). The core logic ensures that the backend (connectivity and scoring) is fully processed before the results are displayed, and that the grid is frozen during the results phase.

## Proposed Implementation

### 1. Files to Create or Change

- **`game.py` (CREATE)**: Pure logic module managing the game state transitions and the confirmation process. No Pygame imports.
- **`tests/test_game.py` (CREATE)**: Pytest suite to validate state transitions, the confirmation logic, and the retry process.
- **`config.py` (CHANGE)**: Add phase constants, the transition table, button layout rectangles, and UI text/colors for the results panel and dialog.
- **`interface.py` (CHANGE)**: Add rendering for the confirmation dialog, the results panel, and the safe/unsafe building highlights.
- **`main.py` (CHANGE)**: Integrate the state machine. Route inputs (clicks/keys) based on the current phase.

### 2. Constants and Functions

#### `config.py` (Additions)
- **Phases**: `PHASE_PLANNING = "planning"`, `PHASE_CONFIRMING = "confirming"`, `PHASE_RESULTS = "results"`.
- **Transitions**: `ALLOWED_TRANSITIONS` dictionary mapping each phase to its valid next phases.
- **Layout**: 
    - `BTN_CONFIRM_RECT`, `BTN_RETRY_RECT`, `BTN_CONTINUE_RECT`.
    - `DIALOG_RECT` (centered box), `DIALOG_YES_RECT`, `DIALOG_CANCEL_RECT`.
- **UI**: Colors for `COLOR_SAFE` (green), `COLOR_UNSAFE` (red), `COLOR_DIALOG_BG`, `COLOR_DIMMER`, `COLOR_DISABLED`.
- **Texts**: Captions for all buttons, dialog titles, and the bonus explanation constants.

#### `game.py` (Pure Logic)
- `create_game_state() -> dict`: Returns `{"phase": PHASE_PLANNING, "breakdown": None}`.
- `change_phase(state, new_phase) -> None`: Checks `ALLOWED_TRANSITIONS`. Raises `ValueError` if illegal.
- `is_editing_allowed(state) -> bool`: True only if `state["phase"] == PHASE_PLANNING`.
- `request_confirmation(state) -> None`: Transition from planning to confirming.
- `cancel_confirmation(state) -> None`: Transition from confirming back to planning.
- `confirm_routes(state, grid, entities, total_budget) -> dict`: 
    - Validates shelter existence.
    - Calls `pathfinding.evaluate_connectivity` and `scoring.build_score_breakdown`.
    - Stores breakdown in `state["breakdown"]`.
    - Transitions to `PHASE_RESULTS`.
- `can_continue(state) -> bool`: True if in results phase AND `state["breakdown"]["passed"]` is True.
- `retry_level(state, grid, entities) -> None`: 
    - Calls `sandbags.clear_sandbags(grid)`.
    - Resets `connected` flags of all entities to `None`.
    - Sets `state["breakdown"]` to `None`.
    - Transitions to `PHASE_PLANNING`.
- `bonus_explanation(breakdown) -> str`: Returns a constant message based on the `passed` flag.

#### `interface.py` (Pygame Rendering)
- `draw_confirm_dialog(screen, remaining, ...)`: Renders a dimmed overlay and a centered confirmation box with YES/CANCEL buttons.
- `draw_results_panel(screen, breakdown, can_continue, ...)`: Replaces the legend/tools in the bottom panel. Renders the multi-column breakdown and the RETRY/CONTINUE buttons.
- `draw_safe_unsafe(screen, entities)`: Highlights buildings green/red based on their `connected` flag.

#### `main.py` (Integration)
- **Routing Logic**:
    - **Planning**: Standard tool/grid interaction. "Confirm" button $\rightarrow$ `request_confirmation`.
    - **Confirming**: Grid/Tools ignored. "YES" $\rightarrow$ `confirm_routes`. "CANCEL"/ESC $\rightarrow$ `cancel_confirmation`.
    - **Results**: Grid frozen (read-only). "RETRY" $\rightarrow$ `retry_level`. "CONTINUE" $\rightarrow$ Placeholder message.

### 3. Bottom Panel Layout
Total Width: 1200px. Height: 150px (600 to 750px).
- **Planning Phase**: 
    - Legend (left side, 0-650px).
    - Tool Button ($x=50, y=600$).
    - Reset Button ($x=300, y=600$).
    - Confirm Button ($x=550, y=600, w=250, h=50$).
- **Results Phase**:
    - Results Grid: 3-4 columns of text (Level, Pop, Saved, Unsaved, Buildings, Sandbags, Scores).
    - Retry Button: Left side.
    - Continue Button: Right side (conditional).
    - Layout ensures text is centered and buttons are far apart.

### 4. `confirm_routes` Failure Handling
The function follows a strict sequence:
1. Shelter Validation $\rightarrow$ 2. Connectivity $\rightarrow$ 3. Scoring $\rightarrow$ 4. State Update.
If any step raises an exception (e.g., `ValueError` from `find_shelter` or `check_evaluated`), the function terminates immediately. Because the `state["phase"]` and `state["breakdown"]` are only updated at the very end, a failure leaves the game in the `"confirming"` phase with `breakdown = None`.

### 5. Testing Plan (`tests/test_game.py`)
- **Transitions**: Verify legal transitions (Plan $\rightarrow$ Confirm $\rightarrow$ Results $\rightarrow$ Plan) and illegal ones (Plan $\rightarrow$ Results).
- **Confirmation**:
    - `cancel_confirmation` returns to planning and leaves data unchanged.
    - `confirm_routes` (success) updates phase to results and populates the breakdown.
    - `confirm_routes` (failure) raises `ValueError` and keeps state as confirming.
- **Continue/Retry**:
    - `can_continue` is True only when passed.
    - `retry_level` clears sandbags, resets `connected` flags, and returns to planning.
- **Cycle Test**: Plan $\rightarrow$ Confirm $\rightarrow$ Results $\rightarrow$ Retry $\rightarrow$ Plan $\rightarrow$ Confirm (verify a second run gives fresh results).

### 6. Ambiguities and Conflicts
- **D4 vs Retry**: D4 specifies the layout is kept. `retry_level` must strictly clear sandbags and flags but not entities.
- **D7**: "Continue" depends on `passed`. This is handled in `can_continue`.

### 7. Risks
- **State Leakage**: Ensuring that `retry_level` resets *everything* (flags, breakdown, sandbags) so the next run isn't tainted by the previous one.
- **Z-Order**: The confirmation dialog must be drawn last to ensure it covers the grid and panels.
