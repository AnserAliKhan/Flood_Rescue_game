# F05: Scoring (Population Score, Conditional Efficiency Bonus, Breakdown)

## Goal
Turn the connectivity result into numbers: people saved and not saved, buildings
connected per type, sandbags used and remaining, population score, efficiency bonus,
final score, and whether the level is passed. Pure logic with unit tests and no GUI. The
student must be able to explain how every number is derived, why none is stored twice,
and why the efficiency bonus depends on the level being passed.

## Context
F00 to F04 are done. Read CLAUDE.md, docs/DECISIONS.md and the existing files (config.py,
grid.py, entities.py, sandbags.py, pathfinding.py) first. Rules that apply here:
- Pure logic must not import pygame.
- D5 (amended): `population_score = saved_people * POINTS_PER_PERSON`.
  `efficiency_bonus = remaining_sandbags * EFFICIENCY_BONUS_PER_SANDBAG` only when ALL
  people are saved, otherwise 0. Both weights already exist in config.py. Never type 5
  inside scoring.py.
- D7: a level is passed only if ALL people were saved.
- The grid is the single source of truth for sandbags (F03): used sandbags are counted
  from the grid, never from a separate variable.
- The backend result comes first. This feature never touches animation.
- D5 overrides SPEC 9.2. The SPEC example (16 of 20 saved, bonus 5) would now give a bonus
  of 0.

## Scope: files to create / change
- CREATE `scoring.py`: pure logic, NO pygame import
- CREATE `tests/test_scoring.py`: pytest tests
- CHANGE `config.py`: only if a new constant is needed (the plan decides)

Do NOT change main.py or interface.py. No visual change in this feature. Do NOT touch
game states, the results screen, levels or the final game summary.

## Requirements

### Precondition
Scoring reads `entity["connected"]`. Every non-shelter entity must be True or False, so
`evaluate_connectivity` (F04) must have been called first. If any non-shelter entity still
has `connected == None`, the scoring functions raise `ValueError` with a clear message
(for example "Connectivity has not been evaluated"). The shelter is ignored everywhere.

### scoring.py (pure logic, no pygame)
Keep names simple; the plan may adjust them. Each function gets a docstring with a
one-line example.

- `check_evaluated(entities)`: raises `ValueError` if any non-shelter entity has
  `"connected"` equal to None. Called by the functions below.
- `count_saved_people(entities)`: sum of `population` over non-shelter entities with
  `connected == True`.
- `count_unsaved_people(entities)`: sum of `population` over non-shelter entities with
  `connected == False`.
- `count_connected_by_type(entities)`: returns a dictionary such as
  `{"house": 4, "school": 2, "hospital": 1}` counting connected buildings per type. All
  three building types are always present as keys, even when the count is 0. The shelter
  is not included.
- `calculate_population_score(saved_people)`: `saved_people * POINTS_PER_PERSON`.
- `calculate_efficiency_bonus(remaining_sandbags, all_saved)`:
  - if `all_saved` is False, return 0
  - otherwise return `remaining_sandbags * EFFICIENCY_BONUS_PER_SANDBAG`
  - raise `ValueError` if `remaining_sandbags` is negative
- `calculate_final_score(population_score, efficiency_bonus)`: their sum.
- `is_level_passed(entities)`: True only if `count_unsaved_people` is 0 (D7). There must
  be at least one non-shelter entity, otherwise raise `ValueError`.
- `build_score_breakdown(grid, entities, total_budget)`: calls the functions above and
  returns ONE dictionary with exactly these keys:
  - `"total_population"`
  - `"saved_people"`, `"unsaved_people"`
  - `"houses_connected"`, `"schools_connected"`, `"hospitals_connected"`
  - `"sandbags_allocated"` (the total budget), `"sandbags_used"` (counted from the grid
    with `sandbags.count_sandbags`), `"sandbags_remaining"`
  - `"population_score"`, `"efficiency_bonus"`, `"final_score"`
  - `"passed"` (bool, from `is_level_passed`)
  The bonus is computed with `all_saved = passed`. `total_population` comes from
  `entities.total_population`. The function must not modify the grid or the entities.
  There is no separate "bonus awarded" key: `passed` already says it, and a later results
  screen (F06) will use `passed` to explain a bonus of 0.

### Consistency rules (tests must check them)
- `saved_people + unsaved_people == total_population`
- `sandbags_used + sandbags_remaining == sandbags_allocated`
- `final_score == population_score + efficiency_bonus`
- `population_score <= total_population * POINTS_PER_PERSON`
- if `passed` is False then `efficiency_bonus == 0`
- if `passed` is True then `efficiency_bonus == sandbags_remaining * EFFICIENCY_BONUS_PER_SANDBAG`
- `passed` is True exactly when `unsaved_people == 0`

## Acceptance criteria
- [ ] `scoring.py` has no pygame import. `main.py` and `interface.py` are unchanged.
- [ ] No literal 5 appears in scoring.py. The weights come from config.py.
- [ ] Calling any scoring function before connectivity is evaluated raises `ValueError`.
- [ ] Everyone saved, with 5 sandbags left, gives a bonus of
      `5 * EFFICIENCY_BONUS_PER_SANDBAG`. The test uses the config constant, not a
      typed-in number.
- [ ] Even one unsaved person gives a bonus of exactly 0, however many sandbags remain.
- [ ] The old SPEC example (20 people, 16 saved, budget 20, 15 used) now gives population
      score 80, bonus 0, final score 80, `passed` False.
- [ ] A player who builds nothing gets bonus 0.
- [ ] Changing `EFFICIENCY_BONUS_PER_SANDBAG` in config.py changes the bonus with no other
      edit (a test patches the constant, for example with `monkeypatch`).
- [ ] `build_score_breakdown` does not change the grid or any entity.
- [ ] `pytest` passes, including the F00 to F04 tests.

## Tests (tests/test_scoring.py, no pygame window)
Build small grids with `create_grid` and `place_entity`, set sandbags by direct cell
assignment or `place_sandbag`, and call `evaluate_connectivity` before scoring. Use
TEST_LAYOUT only where stated.
1. `check_evaluated` raises `ValueError` on a fresh layout (all None) and passes after
   `evaluate_connectivity`. A fresh layout passed to `build_score_breakdown` also raises.
2. Nobody connected (no sandbags): saved 0, unsaved equals the total population, all
   three connected counts 0, `passed` False, bonus 0, final score 0.
3. Everybody connected: saved equals total population, unsaved 0, `passed` True, and the
   bonus equals remaining sandbags times the weight.
4. Partial: some houses connected and some not gives the correct saved and unsaved totals,
   computed by hand in the test, with `passed` False and bonus 0.
5. A school and a hospital connected, a house not: `count_connected_by_type` and the saved
   people reflect the right populations (taken from `POPULATION`).
6. `count_connected_by_type` always contains all three keys, including types with 0.
7. The shelter never adds people or a connected count, even though it is reachable.
8. `calculate_population_score(0)` is 0 and `calculate_population_score(16)` is
   `16 * POINTS_PER_PERSON`.
9. `calculate_efficiency_bonus(5, True)` is `5 * EFFICIENCY_BONUS_PER_SANDBAG`,
   `calculate_efficiency_bonus(5, False)` is 0, `calculate_efficiency_bonus(0, True)` is 0,
   and a negative remaining count raises `ValueError`.
10. The old SPEC example (20 people, 16 saved, budget 20, 15 used) through
    `build_score_breakdown`: population score 80, bonus 0, final 80, `passed` False.
11. A passing example: everyone saved, budget 20, 15 used: bonus is
    `5 * EFFICIENCY_BONUS_PER_SANDBAG` and final score is population score plus bonus.
12. Build-nothing exploit: a layout with no sandbags and a far-away shelter gives bonus 0
    and a final score of 0, even though all sandbags remain.
13. All seven consistency rules hold for at least four different layouts and sandbag
    counts, including at least one passed and one failed level.
14. Sandbags used is counted from the grid: placing 3 sandbags gives `sandbags_used == 3`,
    and removing one gives 2.
15. A placed-but-disconnected sandbag counts as USED but saves no one.
16. `monkeypatch` changes `EFFICIENCY_BONUS_PER_SANDBAG` and `POINTS_PER_PERSON` and the
    score responds. (If monkeypatching a module-level import does not work, the plan may
    read the constants through the config module instead.)
17. `build_score_breakdown` leaves the grid and the entities exactly as they were
    (compare copies made before the call).
18. Level 1, 2 and 3 style layouts (hand-made, building counts from `LEVEL_BUILDINGS`):
    when everyone is saved, the population score equals 100, 150 and 200.
19. Edge case: removing the last sandbag that saved one building flips a passed level to
    failed, and the bonus drops from positive to 0 after re-evaluating.
20. `is_level_passed` raises `ValueError` for a list that contains only the shelter.

## Python concepts demonstrated
Functions with parameters and return values, conditional logic inside a calculation
(the bonus condition), dictionaries as result records, loops with conditionals (summing),
validation with exceptions, constants in a config file, deriving values instead of
storing them, tests of arithmetic invariants, monkeypatching a constant.

## Out of scope
Any GUI or results screen (F06), including the message that explains a bonus of 0, game
state changes, flood animation, per-level score storage, the final game summary and
"overall sandbag efficiency" across three levels (F10), the baseline sandbag calculation,
retry or continue buttons, levels.

## End-of-feature report (required)
What was built, important code sections (especially `build_score_breakdown` and
`calculate_efficiency_bonus`, and how each number is derived), Python concepts used, how
to run and test it, known limitations (mention that a failed attempt can only ever score
the population score, and that F06 must explain this to the player), then STOP.