# F01: Grid Data Model, Rendering, Mouse-to-Cell Conversion

## Goal
Build the 30 x 10 grid as a 2D list, draw all 300 cells from that data, and convert
mouse positions into (row, col) coordinates. The student must be able to explain how a
pixel on screen becomes a cell in the list. Still no buildings, sandbags or game rules.

## Context
F00 is done (config.py, main.py, tests/test_config.py). Read CLAUDE.md,
docs/DECISIONS.md and the F00 files first. Key rules from CLAUDE.md that apply here:
the grid is `grid[row][col]`, rendering must read from the grid data (never duplicate
it), and pure logic must not import pygame.

## Scope: files to create / change
- CREATE `grid.py`: pure logic, NO pygame import
- CREATE `interface.py`: all Pygame drawing and layout, imports pygame
- CREATE `tests/test_grid.py`: pytest tests for grid.py
- CHANGE `config.py`: add layout and colour constants (listed below)
- CHANGE `main.py`: create the grid, draw it, handle mouse hover and click

Do NOT create any other module. No entities, sandbags, pathfinding, scoring or levels.

## Requirements

### config.py additions (each with a comment)
- Panel layout: `TOP_PANEL_HEIGHT = 100`, `BOTTOM_PANEL_HEIGHT = 150`
- Grid position: `GRID_ORIGIN_X = (WINDOW_WIDTH - COLS * CELL_SIZE) // 2` (= 60) and
  `GRID_ORIGIN_Y = 170`. Derive X from existing constants, do not hard-code 60.
- Cell type names as constants or strings: `"empty"`, `"house"`, `"school"`,
  `"hospital"`, `"shelter"`, `"sandbag"`. Only `"empty"` is used in F01, but define all
  now so later features share one vocabulary.
- Colours as RGB tuples: background, panel, grid line, text, hover highlight,
  selected highlight, and a dictionary `CELL_COLORS` mapping every cell type name to a
  colour (use the colour table in SPEC.md section 3.3 for the building types).

### grid.py (pure logic, no pygame)
Functions (names may be adjusted in the plan, but keep them simple and documented):
- `create_grid(rows, cols)`: returns a 2D list where every cell is `"empty"`.
  Use nested loops or a list comprehension. Do NOT use `[[x] * cols] * rows`
  (all rows would be the same list; a test must catch this bug).
- `in_bounds(row, col, rows, cols)`: True if the position is inside the grid.
- `get_cell(grid, row, col)` and `set_cell(grid, row, col, value)`: access with a bounds
  check. Out-of-bounds must raise `IndexError` (or return a clearly documented value).
  Negative indexes must NOT silently wrap around like normal Python lists.
- `pixel_to_cell(x, y, origin_x, origin_y, cell_size, rows, cols)`:
  returns `(row, col)` or `None` if the pixel is outside the grid. Uses integer
  division (`//`). Note the order: x gives the column, y gives the row.
- `cell_to_pixel(row, col, origin_x, origin_y, cell_size)`:
  returns the top-left pixel `(x, y)` of a cell.
Each function gets a docstring with a one-line example.

### interface.py (Pygame only)
- `draw_panels(screen, ...)`: top panel (shows "FLOOD RESCUE" and the hover/selected
  readout) and bottom panel (empty placeholder rectangle). Colours from config.
- `draw_grid(screen, grid, ...)`: nested loops over every row and column. The fill
  colour of each cell comes from `CELL_COLORS[grid[row][col]]`. Draw visible cell borders.
- `draw_coordinates(screen, ...)`: column numbers (0 to 29) above the grid and row
  numbers (0 to 9) to the left of it, using a small font.
- `draw_highlight(screen, cell, color, ...)`: outline one cell (used for hover and
  selection).
interface.py contains no game rules and does not modify the grid.

### main.py behaviour
- Create the grid with `create_grid(ROWS, COLS)`.
- Every frame: read the mouse position, call `pixel_to_cell`, and highlight the hovered
  cell.
- Left click on a cell: remember it as "selected" and keep it highlighted. Clicking
  outside the grid does nothing. The selection lives in a variable in main.py. It must
  NOT be written into the grid data (sandbags come in F03).
- The top panel shows, for example, `Hover: (row 3, col 14)  Selected: (row 9, col 29)`,
  or `Hover: -` when the mouse is outside the grid.
- ESC and window close still exit cleanly.

## Acceptance criteria
- [ ] `python main.py` shows the window with a top panel, a centered grid of 30 columns
      by 10 rows, and a bottom panel.
- [ ] Exactly 300 cells are drawn, equal squares with visible borders.
- [ ] Column numbers and row numbers are visible and correct.
- [ ] Hovering a cell highlights it and shows the right (row, col) in the top panel.
      The top-left cell reads (0, 0), the cell to its right (0, 1), the one below
      it (1, 0), and the bottom-right cell (9, 29).
- [ ] Clicking a cell selects it. Clicking outside the grid does nothing, and nothing
      crashes when the mouse is outside the window.
- [ ] The drawn colours come from the grid data. (Check: temporarily setting one cell to
      `"house"` in main.py makes it brown/orange, then remove that line.)
- [ ] `grid.py` has no pygame import. `interface.py` and `main.py` contain no grid logic
      beyond calling grid.py functions.
- [ ] `pytest` passes, including the F00 tests.
- [ ] No magic numbers in main.py or interface.py. Values come from config.py.

## Tests (tests/test_grid.py, no pygame window)
1. `create_grid(10, 30)` has 10 rows, each with 30 cells, 300 in total, all `"empty"`.
2. Row independence: setting `grid[0][0]` does not change `grid[1][0]`.
3. `in_bounds` is True for (0,0) and (9,29), and False for (-1,0), (0,-1), (10,0), (0,30).
4. `get_cell` / `set_cell` round trip, and both raise on out-of-bounds positions,
   including negative indexes.
5. `pixel_to_cell` returns (0,0) for the top-left pixel of the grid, (0,1) one cell to
   the right, (1,0) one cell down, and (9,29) for the bottom-right cell.
6. `pixel_to_cell` boundaries: the last pixel of cell (0,0) is still (0,0), and the next
   pixel is (0,1). Pixels just outside the grid on all four sides return `None`.
7. Round trip: for every (row, col), `pixel_to_cell` applied to the centre of the cell
   from `cell_to_pixel` returns the same (row, col).

## Python concepts demonstrated
2D lists, nested loops, integer division and modulo reasoning, functions with parameters
and return values, `None` as "no result", tuples, dictionaries (cell type to colour),
bounds validation, separation of logic from presentation.

## Out of scope
Buildings, sandbags, placing or removing anything, tool buttons, levels, random
generation, pathfinding, scoring, game states, menus, flood animation, icons.

## End-of-feature report (required)
What was built, important code sections (especially `pixel_to_cell` explained step by
step with a numeric example), Python concepts used, how to run and test it, known
limitations. Then STOP.