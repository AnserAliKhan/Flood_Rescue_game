# Plan: F01 Grid Data Model, Rendering, and Mouse Conversion

## Context
Following the project skeleton, this feature implements the core 2D grid data structure and its visual representation. The primary goal is to establish a clean separation between the grid's logic (coordinates and data) and its interface (drawing and mouse interaction), ensuring the student can explain how a screen pixel maps to a grid cell.

## Proposed Implementation

### 1. Files to Create or Change

- **`config.py` (CHANGE)**: Add constants for panel heights, grid origin, cell types, and a comprehensive color palette.
- **`grid.py` (CREATE)**: Pure logic module for grid manipulation. No Pygame imports allowed.
- **`interface.py` (CREATE)**: Pygame-based rendering functions to draw the grid, panels, and coordinates.
- **`main.py` (CHANGE)**: Integrate the grid and interface. Handle mouse tracking for hovering and selection.
- **`tests/test_grid.py` (CREATE)**: Pytest suite to validate grid logic and coordinate conversion.

### 2. Constants and Functions

#### `config.py` (Additions)
- **Layout**: `TOP_PANEL_HEIGHT = 100`, `BOTTOM_PANEL_HEIGHT = 150`, `GRID_ORIGIN_X = (WINDOW_WIDTH - COLS * CELL_SIZE) // 2`, `GRID_ORIGIN_Y = 170`.
- **Cell Types**: `"empty"`, `"house"`, `"school"`, `"hospital"`, `"shelter"`, `"sandbag"`.
- **Colors**: RGB tuples for `COLOR_BG`, `COLOR_PANEL`, `COLOR_GRID_LINE`, `COLOR_TEXT`, `COLOR_HOVER`, `COLOR_SELECTED`.
- **`CELL_COLORS`**: Dictionary mapping every cell type to an RGB tuple (from SPEC.md 3.3).

#### `grid.py` (Pure Logic)
- `create_grid(rows, cols) -> list`: Returns a 2D list of `"empty"` cells.
- `in_bounds(row, col, rows, cols) -> bool`: Checks if coordinates are within `[0, rows)` and `[0, cols)`.
- `get_cell(grid, row, col) -> str`: Returns cell value; raises `IndexError` if out of bounds.
- `set_cell(grid, row, col, value) -> None`: Sets cell value; raises `IndexError` if out of bounds.
- `pixel_to_cell(x, y, origin_x, origin_y, cell_size, rows, cols) -> tuple | None`: Converts screen pixels to `(row, col)` or `None`.
- `cell_to_pixel(row, col, origin_x, origin_y, cell_size) -> tuple`: Converts `(row, col)` to top-left `(x, y)`.

#### `interface.py` (Pygame Rendering)
- `draw_panels(screen, hover_info, selected_info)`: Draws top/bottom panels and current selection text.
- `draw_grid(screen, grid)`: Renders cells based on `CELL_COLORS` and draws borders.
- `draw_coordinates(screen)`: Draws 0-29 (cols) above and 0-9 (rows) to the left of the grid.
- `draw_highlight(screen, cell, color)`: Draws a highlighted border around a specific cell.

#### `main.py` (Integration)
- **State**: `grid` (created via `create_grid`), `selected_cell` (initially `None`).
- **Loop**:
    - Call `pixel_to_cell` using `pygame.mouse.get_pos()`.
    - Handle mouse clicks to update `selected_cell`.
    - Call `interface` functions to render the frame.

### 3. Screen Layout Calculation
- **Total Height**: 750px.
- **Top Panel**: 0 to 100px.
- **Coordinate Space**: 100px to 170px (used for column numbers).
- **Grid**: 170px to $170 + (10 \times 36) = 530\text{px}$.
- **Bottom Panel**: $750 - 150 = 600\text{px}$ to 750px.
- **Horizontal Centering**: Grid width is $30 \times 36 = 1080\text{px}$. `GRID_ORIGIN_X` = $(1200 - 1080) // 2 = 60\text{px}$.

### 4. Testing Plan (`tests/test_grid.py`)
- **Grid Creation**: Verify 10x30 size and all `"empty"`.
- **Row Independence**: Ensure changing `grid[0][0]` does not affect `grid[1][0]` (detects shallow copy bug).
- **Bounds Checking**: Test `in_bounds` and `get/set_cell` with valid, out-of-bounds, and negative indices.
- **Coordinate Conversion**:
    - `pixel_to_cell` for top-left, bottom-right, and just-outside edges.
    - Round-trip: `cell_to_pixel` $\rightarrow$ `pixel_to_cell` returns original coordinates.

### 5. Ambiguities and Conflicts
- None identified. The spec is consistent with `DECISIONS.md` and `CLAUDE.md`.

### 6. Risks
- **Shallow Copy Bug**: Using `[[x]*cols]*rows` is a common beginner mistake; the tests are designed to specifically catch this.
- **Coordinate Order**: Confusing `(x, y)` pixels with `(row, col)` grid indices. The plan explicitly notes that $x \rightarrow \text{col}$ and $y \rightarrow \text{row}$.
- **Negative Indexing**: Python lists allow negative indices (e.g., `-1` is the last element). `grid.py` must explicitly block this to maintain grid logic.
