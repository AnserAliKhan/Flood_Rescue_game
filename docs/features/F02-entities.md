# F02: Entities (House, School, Hospital, Shelter) on a Hard-Coded Test Layout

## Goal
Create the four building types as dictionaries, place them on the grid, and draw them
with distinct colours and labels. Use one fixed, hand-written test layout so every run
looks the same. The random generator comes much later (F08). The student must be able
to explain how an entity dictionary and the grid stay consistent with each other.

## Context
F00 and F01 are done. Read CLAUDE.md, docs/DECISIONS.md and the existing files
(config.py, grid.py, interface.py, main.py) first. Rules that apply here:
- Pure logic must not import pygame.
- The grid is `grid[row][col]`. Rendering reads from data, never duplicates it.
- The shelter has no population and is NOT counted as a building (SPEC 4.4).
- Population values come from `config.POPULATION`. Never hard-code 2, 5 or 8 elsewhere.

## Scope: files to create / change
- CREATE `entities.py`: pure logic, NO pygame import
- CREATE `tests/test_entities.py`: pytest tests
- CHANGE `config.py`: add the test layout and label constants
- CHANGE `interface.py`: draw labels inside building cells, draw a colour legend
- CHANGE `main.py`: load the test layout, show building info in the panels

Do NOT create other modules. No sandbags, pathfinding, scoring, random generation or
level logic.

## Requirements

### Entity data model (a dictionary per entity, in a list)
Each entity is a dictionary with exactly these keys:
- `"id"`: unique integer (0, 1, 2, ...)
- `"type"`: `"house"`, `"school"`, `"hospital"` or `"shelter"`
- `"row"`, `"col"`: its grid position
- `"population"`: from `POPULATION[type]`; the shelter has 0
- `"connected"`: `None` for now. Meaning: "not evaluated yet". Later features set it
  to True or False after the flood. Add a comment explaining this.

The list of all entities is kept in a variable in main.py (named e.g. `entities`).

### Consistency rule
When an entity is placed, the grid cell at its position is set to the entity's type
string (for example `grid[1][3] = "house"`). The grid answers "what is in this cell?"
and the entity list answers "what are the details?". They must never disagree. A test
must verify this for the whole test layout.

### entities.py (pure logic)
Keep names simple; the plan may adjust them.
- `create_entity(entity_id, entity_type, row, col)`: returns the dictionary. Raises
  `ValueError` for an unknown type.
- `place_entity(grid, entities, entity_type, row, col)`: validates, then updates BOTH
  the grid and the entities list, and returns the new entity. Raises `ValueError` if
  the position is out of bounds, the cell is not empty, or a second shelter is added.
  The id is the current length of the list.
- `get_entity_at(entities, row, col)`: returns the entity dictionary at that cell or
  `None`. Use a simple loop.
- `get_entities_by_type(entities, entity_type)`: returns a list.
- `count_buildings(entities)`: returns a dictionary like
  `{"house": 6, "school": 2, "hospital": 1}`. The shelter is not included.
- `total_population(entities)`: sum of all populations (shelter adds 0).
- `build_layout(grid, layout)`: loops over a layout list and calls `place_entity` for
  each item. Returns the entities list.
Each function gets a docstring with a one-line example.

### config.py additions (each with a comment)
- `TEST_LAYOUT`: a list of `(type, row, col)` tuples, exactly:
  - shelter (5, 15)
  - house (1, 3), (2, 10), (7, 5), (8, 14), (3, 22), (7, 25)
  - school (1, 18), (8, 22)
  - hospital (5, 4)
  This matches the Level 2 counts from D1 (6 houses, 2 schools, 1 hospital = 30
  people). Add a comment: temporary layout, replaced by the generator in F08.
- `CELL_LABELS`: dictionary mapping type to the label drawn inside the cell:
  house "H", school "S", hospital "+", shelter "SH". Empty and sandbag have no entry
  or an empty string (sandbag "B" can be added now).
- Font size constants for labels. Any new colour (e.g. label text colour) is defined
  here, and building colours already exist in `CELL_COLORS`.

### interface.py additions
- `draw_cell_labels(screen, grid, font, ...)`: nested loops over the grid. If the cell
  type has a label, draw it centred in the cell. Reads from the grid only.
- `draw_legend(screen, ...)`: in the bottom panel, one small colour square plus a name
  for each of: house, school, hospital, shelter. Built by looping over a list or dict,
  not four copy-pasted blocks.
- Labels must stay readable on every building colour.

### main.py behaviour
- After `create_grid`, call `build_layout(grid, TEST_LAYOUT)` and keep the result.
- The top panel additionally shows: `People: 30  Buildings: 9` (computed with
  `total_population` and `count_buildings`, not typed in).
- When the mouse hovers over a building (use `get_entity_at`), the panel shows its
  details, for example `House #3  people: 2`. Hovering the shelter shows
  `Shelter  people: 0`. Hovering an empty cell shows nothing extra.
- Hover and click from F01 still work. ESC and window close still exit cleanly.

## Acceptance criteria
- [ ] `python main.py` shows 6 houses, 2 schools, 1 hospital and 1 shelter at the exact
      coordinates of TEST_LAYOUT, each with its own colour and label.
- [ ] The shelter is clearly distinguishable from all other buildings.
- [ ] Top panel shows People 30 and Buildings 9, computed from the entity data.
- [ ] Hovering a building shows its type, id and population. Hovering empty cells does not.
- [ ] The legend in the bottom panel lists all four types with matching colours.
- [ ] `entities.py` has no pygame import. No population number (2, 5, 8) is typed outside
      `config.py`.
- [ ] Placing on an occupied cell, out of bounds, or a second shelter raises `ValueError`
      and leaves grid and entities unchanged.
- [ ] `pytest` passes, including F00 and F01 tests.

## Tests (tests/test_entities.py, no pygame window)
1. `create_entity` returns the correct keys and population for each of the four types;
   shelter population is 0; `"connected"` is None.
2. `create_entity` raises `ValueError` for an unknown type.
3. `place_entity` updates both the grid cell and the entities list, and assigns
   sequential ids.
4. `place_entity` raises `ValueError` for: occupied cell, out of bounds (including
   negative row/col), second shelter. After a failure, the grid and list are unchanged.
5. `get_entity_at` finds a placed entity and returns None for an empty cell.
6. After `build_layout(create_grid(ROWS, COLS), TEST_LAYOUT)`:
   - exactly 10 entities, exactly 1 shelter
   - `count_buildings` equals `{"house": 6, "school": 2, "hospital": 1}`
   - `total_population` equals 30
   - no two entities share a position
   - consistency: every entity's grid cell holds its type, and the number of non-empty
     grid cells equals the number of entities
7. Every position in TEST_LAYOUT is inside the grid.

## Python concepts demonstrated
Dictionaries as records, lists of dictionaries, tuples, looping with search
(`get_entity_at`), validation with exceptions (`ValueError`), keeping two data
structures consistent, dictionary lookup for config values, loops that avoid
copy-pasted code.

## Out of scope
Sandbags, placing anything by mouse, random placement, population-combination logic,
levels, pathfinding, connectivity, scoring, game states, flood animation, images.

## End-of-feature report (required)
What was built, important code sections (especially how `place_entity` keeps grid and
list consistent), Python concepts used, how to run and test it, known limitations.
Then STOP.