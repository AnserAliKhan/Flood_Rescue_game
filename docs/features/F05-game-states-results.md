# F06: Game State Machine (Planning, Confirm, Results) with a Results Panel

## Goal
Make the game follow a proper flow: the player plans routes, confirms with a safety
dialog, the backend evaluates connectivity and score, and a results panel shows the
breakdown. The grid is frozen outside the planning phase. Retry returns to planning on
the SAME layout. The student must be able to explain what a state machine is, why
"phase" is stored in one variable, and why the backend result is computed before
anything is displayed.

## Context
F00 to F05 are done. Read CLAUDE.md, docs/DECISIONS.md (note amended D5 and D7) and the
existing files (config.py, grid.py, entities.py, sandbags.py, pathfinding.py, scoring.py,
interface.py, main.py) first. Rules that apply here:
- Pure logic must not import pygame. `game.py` is pure logic in this feature.
- The backend decides first: `evaluate_connectivity` and `build_score_breakdown` run
  BEFORE the results are drawn. Drawing only reads the stored breakdown.
- D4: Retry keeps the same layout (same entities, same positions).
- D5 (amended): the efficiency bonus is 0 unless all people are saved.
- D7: Continue is available only when all people were saved. Otherwise only Retry.
- The sandbag budget is still the temporary `TEST_SANDBAG_BUDGET` (real budget: F09/F10).
- The level is always Level 1 for now (a constant). Level switching is F10.

## Scope: files to create / change
- CREATE `game.py`: pure logic, NO pygame import
- CREATE `tests/test_game.py`: pytest tests
- CHANGE `config.py`: phase names, transition table, new layout and colour constants
- CHANGE `interface.py`: confirm button, confirmation dialog, results panel, safe/unsafe
  highlighting, phase display
- CHANGE `main.py`: store the game state, route clicks by phase, call game.py functions

Do NOT create other modules. No flood animation, no level switching, no menu, no
final summary, no baseline calculation.

## Requirements

### Game state (a dictionary)
One dictionary kept in main.py (named e.g. `state`) with exactly these keys:
- `"phase"`: one of `"planning"`, `"confirming"`, `"results"`
- `"breakdown"`: `None` until results exist, then the dictionary from
  `build_score_breakdown`
Phase names are constants in config.py. Never type the strings elsewhere.

### Transition table (in config.py, a dictionary)
```
ALLOWED_TRANSITIONS = {
    "planning":   ["confirming"],
    "confirming": ["planning", "results"],
    "results":    ["planning"],
}
```
A comment must explain that F07 will add a "flooding" phase between confirming and
results by editing this table.

### game.py (pure logic, no pygame)
Keep names simple; the plan may adjust them. Each function gets a docstring with a
one-line example.
- `create_game_state()`: returns `{"phase": "planning", "breakdown": None}`.
- `change_phase(state, new_phase)`: checks `ALLOWED_TRANSITIONS`. Raises `ValueError` for
  an illegal move (for example planning to results) and leaves the state unchanged.
  Otherwise sets the phase.
- `is_editing_allowed(state)`: True only in the planning phase. main.py uses this to
  decide whether sandbag placement, removal, the tool toggle and Reset may act.
- `request_confirmation(state)`: planning to confirming.
- `cancel_confirmation(state)`: confirming to planning. Nothing is evaluated or changed.
- `confirm_routes(state, grid, entities, total_budget)`: only valid in the confirming
  phase (else `ValueError`). Steps, in this order:
  1. validate: exactly one shelter exists (else `ValueError`)
  2. `evaluate_connectivity(grid, entities)`
  3. `build_score_breakdown(grid, entities, total_budget)`
  4. store the breakdown in `state["breakdown"]`
  5. change phase to results
  Returns the breakdown. If any step raises, the phase must stay "confirming" and
  `state["breakdown"]` must stay `None`.
- `can_continue(state)`: True only in the results phase and only if
  `state["breakdown"]["passed"]` is True (D7).
- `retry_level(state, grid, entities)`: only valid in the results phase (else
  `ValueError`). Calls `clear_sandbags(grid)`, sets every non-shelter entity's
  `"connected"` back to `None`, sets `state["breakdown"]` to `None`, changes the phase to
  planning. Buildings, shelter and positions must be unchanged (D4).
- `bonus_explanation(breakdown)`: returns a short string. If `passed` is False it returns
  a message that the efficiency bonus requires all people to be saved (for example
  "No efficiency bonus: not everyone was saved"). If `passed` is True it returns an empty
  string or a short congratulation. The text is defined as constants, not typed inline.

### config.py additions (each with a comment)
- Phase name constants, `ALLOWED_TRANSITIONS`, `CURRENT_LEVEL = 1`
- Button rectangles (x, y, width, height): CONFIRM, RETRY, CONTINUE, dialog YES and
  dialog CANCEL. The plan must show the layout numbers and prove that nothing overlaps
  inside the bottom panel (600 to 750 px) or the dialog.
- Button captions: "CONFIRM ROUTES / START FLOOD", "RETRY LEVEL", "CONTINUE TO NEXT
  LEVEL", "START FLOOD", "KEEP PLANNING"
- Colours: safe highlight (green), unsafe highlight (red), dialog background, dimmer
  overlay, disabled-button colour, results text colour
- Message texts (confirm dialog title, "coming in F10" message, bonus explanation texts)

### interface.py additions (Pygame only, no game rules, never modifies the grid)
- Phase display in the top panel: `Level 1   Phase: Planning` (phase name made readable).
  The sandbag counter and People/Buildings readouts from F02/F03 stay.
- Planning phase: the CONFIRM button is drawn in the bottom panel next to the existing
  tool and Reset buttons, reusing `draw_button`.
- `draw_confirm_dialog(screen, remaining, font, ...)`: dimmed overlay plus a centred box
  with the title, a line such as `Sandbags left: 12`, and the YES / CANCEL buttons. The
  grid stays partly visible behind it.
- `draw_results_panel(screen, breakdown, can_continue, ...)`: shown in the bottom panel
  during the results phase INSTEAD of the legend and tool buttons. Shows all of:
  level, total population, people saved, people not saved, houses / schools / hospitals
  connected, sandbags allocated / used / remaining, population score, efficiency bonus,
  FINAL SCORE (visually the largest). Use several columns so it fits in the panel height.
  If `passed` is False, also show the line from `bonus_explanation`. Buttons: RETRY
  always; CONTINUE only when `can_continue` is True.
- `draw_safe_unsafe(screen, entities, ...)`: results phase only. Loops over the entities
  and outlines or tints each building green if `connected` is True and red if False. Reads
  the entity data only.
- Buttons use the loop-and-reuse approach from F03, not copy-pasted blocks.

### main.py behaviour
- Create `state = create_game_state()` once.
- Event routing by phase:
  - **planning**: everything from F03 works (tool toggle, S key, place, remove, right
    click, Reset). Clicking CONFIRM calls `request_confirmation`. The tool is switched OFF
    when the dialog opens.
  - **confirming**: all grid and tool input is ignored. YES calls `confirm_routes`. CANCEL
    or ESC calls `cancel_confirmation`. Clicks outside the dialog do nothing.
  - **results**: the grid is frozen (clicks and hover still show selection and building
    info, but nothing changes). RETRY calls `retry_level`. CONTINUE (visible only when
    allowed) shows the "coming in F10" message and changes nothing else.
- Wrap game.py calls in try/except for `ValueError` and show the message in the message
  line instead of crashing.
- Closing the window exits cleanly. ESC exits the program in planning and results, and
  cancels the dialog in confirming.
- Hover info, selection, legend (in planning) and the top panel readouts from F01 to F03
  still work.

## Acceptance criteria
- [ ] The game starts in planning with the same behaviour as F03, plus a CONFIRM button.
- [ ] Clicking CONFIRM opens a dialog. CANCEL (or ESC) returns to planning with sandbags
      unchanged and nothing evaluated.
- [ ] YES shows the results panel with every required number. All numbers come from the
      stored breakdown, none are typed in.
- [ ] During confirming and results, sandbags cannot be placed or removed, the tool key S
      does nothing, and Reset is unavailable.
- [ ] In results, connected buildings are marked green and unconnected red.
- [ ] If everyone is saved: CONTINUE and RETRY are shown, and the efficiency bonus is
      remaining sandbags times the weight.
- [ ] If anyone is unsaved: ONLY RETRY is shown, the bonus is 0, and the panel explains
      why.
- [ ] Building nothing and confirming gives 0 saved, bonus 0, final score 0.
- [ ] RETRY returns to planning with 0 sandbags placed, the full budget, and the same
      buildings at the same positions. Old colours (green/red) are gone.
- [ ] Clicking CONTINUE (when shown) changes no state and shows the placeholder message.
- [ ] Illegal transitions raise `ValueError` in game.py and never crash the window.
- [ ] `game.py` has no pygame import. `interface.py` modifies no game data.
- [ ] `pytest` passes, including the F00 to F05 tests.

## Tests (tests/test_game.py, no pygame window)
Build small grids with `create_grid` and `place_entity` (a shelter, a few buildings, a
few hand-placed sandbags). Use TEST_LAYOUT only where stated.
1. `create_game_state` returns phase "planning" and breakdown None.
2. Legal transitions work: planning to confirming, confirming to planning, confirming to
   results, results to planning.
3. Illegal transitions raise `ValueError` and leave the state unchanged: planning to
   results, planning to planning, results to confirming, an unknown phase name.
4. `is_editing_allowed` is True only in planning.
5. `cancel_confirmation` returns to planning, the breakdown stays None, entity
   `"connected"` flags stay None, and the grid is unchanged.
6. `confirm_routes` outside the confirming phase raises `ValueError`.
7. `confirm_routes` on a fully connected layout: phase becomes results, the stored
   breakdown equals the returned one, `passed` is True, and the entity flags are True.
8. `confirm_routes` on a partly connected layout: `passed` False, bonus 0, flags match the
   connectivity.
9. `confirm_routes` with no sandbags placed: saved 0, bonus 0, final 0.
10. `confirm_routes` on a grid with no shelter raises `ValueError`, and the state is still
    "confirming" with breakdown None.
11. `can_continue` is True only in results AND passed. It is False in planning, in
    confirming, and in results when not passed.
12. `retry_level` outside results raises `ValueError`.
13. `retry_level` after a failed run: phase planning, breakdown None, sandbag count 0,
    non-shelter flags None, and the entity list (ids, types, positions, populations) and
    the building cells in the grid are identical to before the run (compare copies).
14. Full cycle: plan, confirm, results, retry, plan a different route, confirm again gives
    a fresh, correct breakdown (no stale values from the first run).
15. The state dictionary keys are exactly `"phase"` and `"breakdown"`.
16. `bonus_explanation` returns a non-empty message when `passed` is False and no
    bonus-denied message when True.
17. Every phase in `ALLOWED_TRANSITIONS` (keys and targets) is a defined phase constant.

## Python concepts demonstrated
A state machine with a dictionary lookup table, state stored in a dictionary, functions
that validate before changing data, exceptions with try/except, separation of logic from
drawing, drawing from stored results instead of recalculating, event routing with
conditionals, reuse of one button function, constants for all text and numbers.

## Out of scope
Flood animation or timing (F07), a "flooding" phase, level generation and switching,
the real sandbag budget, a main menu, an instructions screen, the final summary and
cross-level totals (F10 and F11), sound, undo.

## End-of-feature report (required)
What was built, important code sections (especially `change_phase`, `confirm_routes` and
why evaluation happens before drawing), Python concepts used, how to run and test it,
known limitations (mention that Continue is a placeholder until F10 and that the budget
is still temporary), then STOP