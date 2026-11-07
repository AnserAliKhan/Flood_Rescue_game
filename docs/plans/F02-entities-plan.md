# Plan: F02 Entities (House, School, Hospital, Shelter)

## Context
This feature introduces the building entities into the game. While the grid handles "what" is in a cell, the entity model provides the "details" (ID, population, connection status). We will implement a hard-coded test layout based on Level 2 specifications to verify the data model and rendering before moving to random generation.

## Proposed Implementation

### 1. Files to Create or Change

- **`config.py` (CHANGE)**: Add the `TEST_LAYOUT` coordinates, `CELL_LABELS` dictionary, and font/color constants for labels and the legend.
- **`entities.py` (CREATE)**: Pure logic module to manage entity dictionaries and maintain consistency with the grid. No Pygame imports.
- **`interface.py` (CHANGE)**: Add functions to draw cell labels (H, S, +, SH) and a color legend in the bottom panel.
- **`main.py` (CHANGE)**: Initialize the entity list using the test layout, update the top panel with population/building counts, and implement building-specific hover details.
- **`tests/test_entities.py` (CREATE)**: Pytest suite to validate entity creation, placement constraints, and grid-entity consistency.

### 2. Constants and Functions

#### `config.py` (Additions)
- `TEST_LAYOUT`: List of `(type, row, col)` tuples for 1 shelter, 6 houses, 2 schools, and 1 hospital.
- `CELL_LABELS`: `{"house": "H", "school": "S", "hospital": "+", "shelter": "SH", "sandbag": "B"}`.
- `LABEL_FONT_SIZE`: Constant for cell labels.
- `COLOR_LABEL_TEXT`: RGB tuple for building labels.

#### `entities.py` (Pure Logic)
- `create_entity(entity_id, entity_type, row, col) -> dict`: Creates a dictionary with keys: `id`, `type`, `row`, `col`, `population` (from `config.POPULATION`), and `connected` (initialized to `None`).
- `place_entity(grid, entities, entity_type, row, col) -> dict`: 
    - Validates: bounds check, cell must be `"empty"`, only one shelter allowed.
    - Actions: Updates `grid[row][col] = entity_type` AND appends the new entity to the `entities` list.
    - Returns the new entity. Raises `ValueError` on failure.
- `get_entity_at(entities, row, col) -> dict | None`: Loops through `entities` to find one matching the position.
- `get_entities_by_type(entities, entity_type) -> list`: Filtered list of entities.
- `count_buildings(entities) -> dict`: Returns counts of houses, schools, hospitals (excluding shelter).
- `total_population(entities) -> int`: Sum of populations of all entities.
- `build_layout(grid, layout) -> list`: Helper that iterates through a layout list, calling `place_entity` for each, and returns the final entities list.

#### `interface.py` (Pygame Rendering)
- `draw_cell_labels(screen, grid, font)`: Iterates over the grid; if a cell type has a label in `CELL_LABELS`, it is drawn centered in the cell.
- `draw_legend(screen)`: Loops through building types and draws a color square + name in the bottom panel.

#### `main.py` (Integration)
- **State**: `entities` list (result of `build_layout`).
- **Loop Update**: 
    - Use `entities.total_population()` and `entities.count_buildings()` for the top panel.
    - If `hovered_cell` matches an entity via `get_entity_at`, display `Type #ID people: Pop` in the top panel.

### 3. Consistency Management
The `place_entity` function is the single point of truth for updates:
1.  **Validation First**: It checks if the position is valid and empty *before* making any changes.
2.  **Atomic Update**: If valid, it updates the grid cell and the entities list simultaneously.
3.  **Failure Handling**: If a `ValueError` is raised, neither the grid nor the list is modified, ensuring they never drift apart.

### 4. Testing Plan (`tests/test_entities.py`)
- **Entity Creation**: Check keys and population values (Shelter=0).
- **Placement Validation**:
    - Success: Grid cell updated and entity added to list.
    - Failure (Occupied): Attempting to place on a non-empty cell raises `ValueError` and changes nothing.
    - Failure (Bounds): Out of bounds/negative indices raise `ValueError`.
    - Failure (Shelter): Attempting to place a second shelter raises `ValueError`.
- **Layout Consistency**: After `build_layout`, verify that:
    - Number of non-empty grid cells == length of entities list.
    - Every entity's position in the list matches the type in the grid.
- **Metrics**: Verify `total_population` is 30 and `count_buildings` matches D1 for the test layout.

### 5. Ambiguities and Conflicts
- None identified. The spec aligns with `DECISIONS.md` and `CLAUDE.md`.

### 6. Risks
- **Performance**: `get_entity_at` uses a linear loop. For a small number of buildings (~10), this is acceptable and keeps the code beginner-friendly.
- **Data Redundancy**: Storing position in both the grid and the entity dictionary creates redundancy. This is a design choice for ease of access; the tests will ensure they stay synced.
