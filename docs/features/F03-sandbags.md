# F03: Sandbag Placement, Removal, Budget and Validation

## Goal
Let the player place and remove sandbags on empty cells with the mouse, with a limited
budget and strict validation. The grid is the single source of truth: a sandbag is a
cell whose value is "sandbag". The student must be able to explain why the remaining
count is calculated from the grid instead of being stored in a separate counter.

## Context
F00 to F02 are done. Read CLAUDE.md, docs/DECISIONS.md and the existing files
(config.py, grid.py, entities.py, interface.py, main.py) first. Rules that apply here:
- Pure logic must not import pygame.
- Rendering reads from the grid and never duplicates it.
- Buildings and the shelter can never be overwritten (SPEC 6.4).
- The real budget is `baseline_sandbags + SANDBAG_MARGIN` (D2). The baseline calculator
  does not exist yet (F09), so this feature uses a temporary fixed budget.

## Scope: files to create / change
- CREATE `sandbags.py`: pure logic, NO pygame import
- CREATE `tests/test_sandbags.py`: pytest tests
- CHANGE `config.py`: add the temporary budget, button layout and message constants
- CHANGE `interface.py`: draw buttons, the sandbag counter and a message line
- CHANGE `main.py`: tool toggle, placement and removal by mouse, Reset

Do NOT create other modules. No pathfinding, connectivity, scoring, game states,
confirm button, flood animation or level logic.

## Requirements

### Single source of truth
The number of sandbags used is the number of cells equal to `"sandbag"` in the grid.
Do NOT keep a separate "used" counter variable. Only the total budget is stored
(a constant or a variable). Remaining = total - sandbags counted in the grid.
This makes it impossible for the counter and the picture to disagree.

### sandbags.py (pure logic)
Keep names simple; the plan may adjust them. Each function gets a docstring with a
one-line example.
- `count_sandbags(grid)`: counts cells equal to `"sandbag"` with nested loops.
- `remaining_sandbags(grid, total_budget)`: `total_budget - count_sandbags(grid)`.
- `check_placement(grid, row, col, total_budget)`: returns `(True, "")` if placement is
  allowed, otherwise `(False, reason)`. Reasons, checked in this order:
  1. position outside the grid
  2. cell is a building or the shelter
  3. cell already holds a sandbag
  4. no sandbags remaining
  Reasons are short, player-readable strings (define them as constants in config.py or
  at the top of sandbags.py, not typed repeatedly).
- `place_sandbag(grid, row, col, total_budget)`: calls `check_placement`. If not allowed,
  raises `ValueError(reason)` and leaves the grid unchanged. Otherwise sets the cell to
  `"sandbag"`.
- `remove_sandbag(grid, row, col)`: raises `ValueError` if the position is out of bounds
  or the cell is not a sandbag (a building must never be erased by this function).
  Otherwise sets the cell back to `"empty"`.
- `clear_sandbags(grid)`: turns every sandbag back to `"empty"`, touching nothing else.
  Used by Reset.
Negative indexes must be rejected, not wrapped (reuse `grid.in_bounds`).

### config.py additions (each with a comment)
- `TEST_SANDBAG_BUDGET = 40`: temporary generous value for testing. Comment: replaced by
  `baseline_sandbags + SANDBAG_MARGIN` in F09/F10.
- Button rectangles in the bottom panel as `(x, y, width, height)` tuples for: the
  sandbag tool and Reset. They must not overlap the F02 legend. The plan must show the
  layout numbers.
- Colours for button normal / active / hover states, button text colour, and a message
  text colour.
- Label constants for the sandbag cell ("B", already planned in F02) and the button
  captions ("SANDBAG TOOL", "RESET").

### interface.py additions
- `draw_button(screen, rect, text, font, active, hovered)`: draws one button. Reuse for
  both buttons, no copy-paste.
- `draw_sandbag_counter(screen, remaining, total, font)`: top panel, for example
  `Sandbags: 37 / 40`. The text turns a warning colour when remaining is 0.
- `draw_message(screen, text, font)`: one line for feedback messages (shows nothing if
  the text is empty).
- A sandbag cell must look clearly different from every building and from empty cells
  (colour from `CELL_COLORS`, label "B").
- A helper that tells whether a mouse position is inside a button rectangle may live
  here (e.g. using `pygame.Rect.collidepoint`).
interface.py contains no game rules and does not modify the grid.

### main.py behaviour
- A variable `tool_active` (bool) starts as False.
- Clicking the SANDBAG TOOL button, or pressing the S key, toggles it. The button looks
  active when on.
- With the tool ON:
  - Left click on an empty cell places a sandbag via `place_sandbag`.
  - Left click on an existing sandbag removes it via `remove_sandbag`.
  - Right click on a sandbag also removes it.
- With the tool OFF, clicking the grid behaves exactly as in F01 (selection only).
- A rejected placement must not crash. Catch the `ValueError` and show its reason in the
  message line (for example "Cannot build on a building" or "No sandbags left"). The
  message disappears after about 2 seconds (use a timer constant in config.py) or when
  the next valid action happens.
- Clicking the RESET button calls `clear_sandbags`. Buildings must stay untouched.
- The top panel shows the sandbag counter, always computed from the grid.
- Hover, building info, legend, ESC and window close from F01 and F02 still work.

## Acceptance criteria
- [ ] With the tool on, clicking empty cells turns them into sandbags with the "B" label
      and the counter decreases by 1 each time (40, 39, 38, ...).
- [ ] Clicking a sandbag (tool on) or right-clicking it removes it and the counter
      increases by 1. The cell returns to empty.
- [ ] Clicking any house, school, hospital or the shelter never changes it. A message
      explains why.
- [ ] After placing all 40 sandbags, a 41st click is rejected with a message and the
      counter stays at 0.
- [ ] Removing one sandbag after reaching 0 allows placing again.
- [ ] RESET removes all sandbags, restores the counter to 40, and leaves all 10
      buildings in place.
- [ ] With the tool off, clicks only select cells and place nothing.
- [ ] Clicking outside the grid and on panel areas does nothing and does not crash.
- [ ] `sandbags.py` has no pygame import. No `used` counter variable exists anywhere.
- [ ] `pytest` passes, including the F00 to F02 tests.

## Tests (tests/test_sandbags.py, no pygame window)
Use a grid built with `create_grid` and `build_layout(grid, TEST_LAYOUT)`.
1. `count_sandbags` is 0 on a fresh layout and 3 after three placements.
2. `place_sandbag` on an empty cell sets `"sandbag"` and `remaining_sandbags` drops by 1.
3. Placing on every building cell and on the shelter raises `ValueError` and leaves the
   grid identical (compare a copy made before the attempt).
4. Placing out of bounds (including row -1 and col -1) raises `ValueError`.
5. Placing on a cell that already has a sandbag raises `ValueError` and does not change
   the count.
6. With a budget of 3: three placements succeed, the fourth raises `ValueError`, and the
   count stays 3.
7. `check_placement` returns the expected `(bool, reason)` for each of the four failure
   cases, and `(True, "")` for a valid one.
8. `remove_sandbag` restores `"empty"` and increases `remaining_sandbags` by 1.
9. `remove_sandbag` raises `ValueError` on an empty cell, on every building cell, and out
   of bounds. Buildings are unchanged afterwards.
10. Place then remove then place again within a budget of 1 works (budget is restored).
11. `clear_sandbags` removes all sandbags, keeps all 10 buildings, and the number of
    non-empty cells equals the number of entities again.
12. Consistency: after any sequence of placements and removals,
    `count_sandbags(grid) + remaining_sandbags(grid, budget) == budget`.

## Python concepts demonstrated
Conditional statements and validation order, functions returning tuples, exceptions
(`ValueError`) with `try/except`, nested loops (counting), a single source of truth,
event handling for different mouse buttons, boolean state variables (toggle), reuse of
one function for several buttons.

## Out of scope
Pathfinding or checking whether sandbags connect, diagonal rules (connectivity is F04),
a confirm button, locking the grid, game states, scoring, the real budget calculation,
levels, dragging to place many sandbags, sound, flood animation, undo history.

## End-of-feature report (required)
What was built, important code sections (especially `check_placement` and why the count
comes from the grid), Python concepts used, how to run and test it, known limitations.
Then STOP.