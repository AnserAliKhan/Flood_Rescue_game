# F08: Level Generator (Population Check, Random Placement, Solvability, Seed)

## Goal
Replace the hard-coded TEST_LAYOUT with a generator that builds Level 1, 2 or 3 from a
seed. Counts come from LEVEL_BUILDINGS (D1). Placement is random but reproducible, obeys
spacing rules, and is verified solvable before it is returned. The student must be able to
explain: why a seed makes randomness repeatable, why we retry instead of fixing a bad
layout, and what "solvable" means here.

## Context
F00 to F07 are done. Read CLAUDE.md, docs/DECISIONS.md and the existing files (config.py,
grid.py, entities.py, sandbags.py, pathfinding.py, scoring.py, game.py, interface.py,
main.py) first. Rules that apply here:
- Pure logic must not import pygame. `level_generator.py` is pure logic.
- D1: building counts per level are fixed in config. Population totals must never change.
- D4: each level has a fixed seed in config, so Retry and restarts give the same layout.
- D6: difficulty comes only from more people/buildings (and spread), not from the budget.
- SPEC 5.1: no overlaps, shelter not on a building, everything inside the grid, population
  satisfied, at least one valid solution.
- The sandbag budget is still the temporary TEST_SANDBAG_BUDGET (real budget: F09/F10).

## Scope: files to create / change
- CREATE `level_generator.py`: pure logic, NO pygame import
- CREATE `tests/test_level_generator.py`: pytest tests
- CHANGE `config.py`: seeds, regions, spacing and retry constants
- CHANGE `main.py`: build the level with the generator; temporary debug keys 1/2/3
- Keep TEST_LAYOUT in config.py (older tests use it). Add a comment: no longer used by
  main.py.

Do NOT change game.py, scoring.py, pathfinding.py, flood.py or the F07 behaviour. Do NOT
create a baseline calculator, menu or level progression.

## Requirements

### config.py additions (each with a comment)
- `LEVEL_SEEDS = {1: 101, 2: 202, 3: 303}` (D4; any fixed integers)
- `LEVEL_REGIONS`: per level, the allowed column range (inclusive) for buildings and for
  the shelter, plus an optional row range. Starting values:
  - Level 1: buildings columns 6 to 23, shelter columns 12 to 17
  - Level 2: buildings columns 2 to 27, shelter columns 10 to 19
  - Level 3: buildings columns 0 to 29, shelter columns 8 to 21
  All rows 0 to 9 are allowed in every level.
- `MIN_BUILDING_GAP = 1`: buildings (and the shelter) must not be orthogonal neighbours.
  Comment: diagonal touching is allowed.
- `MAX_PLACEMENT_TRIES = 200` (random tries per building) and `MAX_LEVEL_RESTARTS = 50`
  (whole-layout restarts), with a comment explaining why both exist.

### level_generator.py (pure logic, no pygame)
Keep names simple; the plan may adjust them. Each function gets a docstring with a
one-line example.
- `get_level_composition(level)`: returns the building-count dictionary from
  `LEVEL_BUILDINGS[level]`. Raises `ValueError` for an unknown level, and raises
  `ValueError` if the population does not equal `LEVEL_POPULATION[level]` (never silently
  fixes it).
- `build_placement_order(composition)`: returns a list of building type names, one per
  building (for example `["house", ... "school", ... "hospital"]`), in a fixed order.
- `neighbors_are_free(grid, row, col)`: True if the four orthogonal neighbours (use
  `DIRECTIONS`) are all empty or out of bounds. Used for the spacing rule.
- `is_valid_spot(grid, row, col, col_range, row_range)`: True if the cell is inside the
  grid and the given ranges, is empty, and `neighbors_are_free`.
- `pick_random_spot(grid, rng, col_range, row_range)`: tries up to `MAX_PLACEMENT_TRIES`
  random cells with `rng.randint` and returns the first valid `(row, col)`, or `None`.
- `is_level_solvable(grid, entities)`: the solvability check. Return True only if ALL hold:
  1. The shelter has at least one empty orthogonal neighbour.
  2. Every building has at least one empty orthogonal neighbour.
  3. Flood-fill (recursive or iterative, plan decides) over EMPTY cells only, starting from
     the empty neighbours of the shelter. Every building must have at least one empty
     neighbour that was reached by this fill.
  Meaning: sandbags can reach every building without passing through another building.
  Uses `DIRECTIONS`. Does not modify the grid.
- `generate_level(level, seed=None)`: returns `(grid, entities)`.
  - `seed=None` uses `LEVEL_SEEDS[level]`.
  - Creates `rng = random.Random(seed)`. Never calls the global `random.seed` or global
    `random` functions, so the generator cannot disturb other code.
  - Loop up to `MAX_LEVEL_RESTARTS` times: create a fresh grid, place the shelter with
    `pick_random_spot` inside the shelter region, then place each building (in the
    placement order, so scarce types are not forced last by accident) with
    `place_entity`. If any spot is `None`, restart. After placement, run
    `is_level_solvable`; if False, restart.
  - If all restarts fail, raise `RuntimeError` with a clear message.
  - Before returning, assert the finished level: counts equal composition,
    `total_population` equals `LEVEL_POPULATION[level]`, exactly one shelter. Raise
    `ValueError` if not.
  The result must be identical for the same level and seed (deterministic).

### main.py behaviour
- At start: `grid, entities = generate_level(CURRENT_LEVEL)`. TEST_LAYOUT is no longer used
  by main.py.
- Temporary debug: in the PLANNING phase only, pressing 1, 2 or 3 sets the level, calls
  `generate_level` for it, creates a fresh game state, clears the selection and message.
  The top panel's level number must follow the chosen level. Add a comment: "temporary,
  replaced by real level flow in F10". Keys do nothing in confirming, flooding or results.
- Retry (F06) still keeps the same entities and positions. It must NOT call the generator.
- The sandbag budget stays `TEST_SANDBAG_BUDGET`.
- Everything from F01 to F07 still works.

## Acceptance criteria
- [ ] Starting the game shows a generated Level 1: 5 houses, 2 schools, 0 hospitals, 1
      shelter (People 20, Buildings 7 in the top panel).
- [ ] Pressing 2 shows 6 houses, 2 schools, 1 hospital (People 30, Buildings 9). Pressing 3
      shows 7 / 2 / 2 (People 40, Buildings 11).
- [ ] Starting the program twice shows the identical Level 1 layout (same seed).
- [ ] Pressing 1, 2, 3, 1 again shows the same Level 1 layout the second time.
- [ ] No two buildings touch orthogonally, and nothing overlaps.
- [ ] Level 1 buildings stay within its column range and Level 3 spreads across more of the
      grid.
- [ ] Retry keeps the same layout (generator not called).
- [ ] The debug keys do nothing outside planning.
- [ ] `level_generator.py` has no pygame import and never uses the global `random` state.
- [ ] `pytest` passes, including all earlier tests.

## Tests (tests/test_level_generator.py, no pygame window)
1. `get_level_composition` returns the D1 counts for levels 1, 2 and 3. It raises
   `ValueError` for level 0 and level 4.
2. `get_level_composition` raises `ValueError` if `monkeypatch` changes
   `LEVEL_POPULATION` so it no longer matches.
3. For each level, `generate_level` returns exactly 300 cells, exact counts from
   `LEVEL_BUILDINGS`, `total_population` equal to 20 / 30 / 40, exactly one shelter, and the
   `(2 x houses) + (5 x schools) + (8 x hospitals)` formula (using `POPULATION`).
4. Consistency: every entity's grid cell holds its type and the number of non-empty cells
   equals the number of entities (same rule as F02).
5. No two entities share a cell and none is out of bounds.
6. Spacing: no building or shelter has an orthogonal neighbour that is another entity.
7. Region: for each level, all buildings are inside the level's building column range and the
   shelter is inside its shelter range.
8. Determinism: the same level and seed twice give identical entity lists. Different seeds
   (for example 1 and 2) give different layouts for at least one level.
9. `seed=None` equals the seed in `LEVEL_SEEDS`.
10. Global random state is untouched: call `random.seed(5)`, record `random.random()`, reset the
    seed, call `generate_level`, then `random.random()` returns the same value.
11. Stress test: for each level, generate with at least 200 different seeds (for example
    0 to 199). Every result passes tests 3 to 6 and `is_level_solvable`. No `RuntimeError`.
12. `neighbors_are_free`: True for an isolated cell, False next to a building, True on a
    corner when the neighbours inside the grid are empty.
13. `is_level_solvable` is True for a simple hand-made layout. It is False when the shelter
    has no empty neighbour (surrounded by buildings or edges). It is False when a building
    has no empty neighbour. It is False when a building is enclosed by a ring that the empty
    fill from the shelter cannot reach (hand-made grid; for example a building inside a
    closed ring of other buildings).
14. `is_level_solvable` and `generate_level` pieces do not modify a grid passed in
    (compare copies).
15. `RuntimeError` path: with `monkeypatch` setting `MAX_LEVEL_RESTARTS` to 1 and an
    impossible region (for example a one-column region for many buildings), `generate_level`
    raises `RuntimeError`.
16. Difficulty progression: building counts are 7 < 9 < 11, total population 20 < 30 < 40,
    and hospital count strictly increases from level 2 to 3 (level 1 has none).
17. The generated level works with earlier features: `evaluate_connectivity` with no sandbags
    sets only buildings touching the shelter to connected. By the spacing rule that is none,
    so every building is False. `build_score_breakdown` then gives saved 0.

## Python concepts demonstrated
Random number generation with a seeded `random.Random` object, reproducibility, loops with
retry limits, validation, nested data (dictionaries of dictionaries in config), recursion or
a stack for the flood-fill, composing small functions, stress testing, monkeypatching.

## Out of scope
The sandbag baseline calculation (F09), the real budget, level progression and the
final summary (F10), menu (F11), any change to scoring, flood or game phases, a "best
route" display, difficulty rating of a generated layout.

## End-of-feature report (required)
What was built, important code sections (especially `generate_level` and why it retries,
and `is_level_solvable`), why a seeded `random.Random` is used instead of `random.seed`,
Python concepts used, how to run and test it, known limitations (for example the 40
sandbag test budget may be too small or too large for some layouts until F09, and the
debug keys are temporary), then STOP.