# F12: Polish, Full Test Pass and README

## Goal
Finish the project for submission and demonstration. Remove debug leftovers, tidy the code,
prove every SPEC section 15 test point with a named test, add a random-play fuzz test, write
the README, a demo-notes file and a manual QA checklist. No gameplay changes. The student
must be able to explain each module, every decision that overrides the original spec, and
where each course concept is demonstrated.

## Context
F00 to F11 are done. Read CLAUDE.md, docs/DECISIONS.md, docs/SPEC.md (sections 12, 13, 14
and 15 especially) and every .py file first. Rules:
- No new features, no rule changes, no new modules in the game package. Documentation,
  cleanup and tests only.
- Pure logic modules must not import pygame (check all of them).
- D1 to D7 stay as written. Amended D5 and D7 override SPEC 9 and 10.
- Behaviour must be identical before and after cleanup. Every earlier test must still pass
  unchanged, except where the plan lists a justified edit (for example a deleted constant).

## Scope: files to create / change
- CREATE `tests/test_spec_section15.py`: one test per SPEC 15 item
- CREATE `tests/test_fuzz_playthrough.py`: random-play robustness and invariants
- CREATE `README.md` content (the file exists and is empty)
- CREATE `docs/DEMO_NOTES.md`
- CREATE `docs/QA_CHECKLIST.md`
- CREATE `docs/KNOWN_ISSUES.md` (only the issues that remain after the polish)
- CHANGE `config.py`, `main.py`, `interface.py` and other modules: cleanup only (see below)
- CHANGE `requirements.txt`: only packages the project needs (pygame, pytest, pyflakes)
- CHANGE `.gitignore` if needed

## Requirements

### A. Cleanup (behaviour unchanged)
1. Find every unused constant, import, function and variable (use `python -m pyflakes *.py`
   and a search for each config name). Delete dead code. List each deletion in the report.
2. `TEST_LAYOUT`, `TEST_SANDBAG_BUDGET`, `CURRENT_LEVEL`: delete if unused; if an old test
   still needs one, keep it with a comment saying "tests only".
3. Terminal debug prints (baseline/budget line and any other print) go behind
   `DEBUG_PRINT = False` in config.py. Comment on the flag. `DEBUG_LEVEL_KEYS` stays False.
4. Magic numbers: search main.py and interface.py for literal numbers (positions, sizes,
   timings, colours, font sizes). Move any that remain into config.py with a comment.
5. Fonts: create every `pygame.font.Font` once before the main loop (or in one function
   called once) and pass them in. No font creation inside per-frame code.
6. Every module gets a top-of-file docstring (purpose, whether it imports pygame). Every
   public function has a docstring. Comments explain the "why" for the recursive DFS, the BFS,
   the state machines and the flood timing.
7. Consistent names and messages: one style for constants (UPPER_CASE), functions
   (snake_case). Player-visible messages are constants, not typed inline.
8. Window title is "Flood Rescue". The window closes cleanly from every screen (menu,
   instructions, planning, confirming, flooding, results, summary): no traceback.
9. `assets/images` and `assets/fonts` are empty folders: either remove them, or add a
   `.gitkeep` and mention in the README that no external assets are used. Plan decides.
10. Check that the grid is still exactly 30 x 10 and that all 300 cells are visible at once.

### B. SPEC 14/3.3 visual check (report only, fix only clear defects)
The plan lists, for each of these, whether it is already satisfied or needs a small fix:
legend shows house/school/hospital/shelter (and sandbag if SPEC 3.3 expects it), shelter is
visually unique, sandbag is distinct from every building, safe buildings green and unsafe red
in results, the results panel contains every SPEC 10 item (with amended D5), the sandbag counter
is clearly visible, buttons have hover feedback. Do not redesign anything.

### C. tests/test_spec_section15.py
One test function per SPEC 15 item, named `test_15_01_...` to `test_15_19_...`, each with a
docstring quoting the SPEC item. Each test is short and self-contained (builds its own small
data) and uses config constants for expected values:
1. Grid has exactly 300 cells (10 rows x 30 cols).
2. No building overlaps another (all three generated levels, default seeds, plus 50 seeds).
3. Exactly one shelter per level (all three levels).
4. Population totals are 20 / 30 / 40.
5. The sandbag budget is calculated correctly: equals baseline + SANDBAG_MARGIN, and on a
   hand-made layout the baseline equals a hand-computed value.
6. Sandbags cannot be placed outside the grid (including negative indexes).
7. Sandbags cannot overwrite a house, school, hospital or shelter.
8. Placing a sandbag decreases the remaining count by one.
9. Removing a sandbag increases the remaining count by one.
10. A diagonal neighbour is not connected.
11. A horizontal chain connects.
12. A vertical chain connects.
13. A building connected to the shelter is marked safe (connected True).
14. A disconnected building is marked unsafe (connected False).
15. Population score equals saved people x POINTS_PER_PERSON.
16. Efficiency bonus equals remaining sandbags x weight when everyone is saved, and is 0 when
    anyone is unsaved (amended D5). The test docstring says it follows amended D5, not SPEC 9.2.
17. Three levels increase in difficulty: buildings 7 < 9 < 11, population 20 < 30 < 40,
    hospitals 0 < 1 < 2.
18. Restart retains no old data: after a full level run (confirm, flood, results), a new
    campaign/state/level load has empty results, a fresh grid with no sandbags, entity flags
    None, state keys reset, and the Level 1 layout equals the first time (D4).
19. The flood animation does not affect the score: breakdown computed before any flood function
    runs equals the breakdown after all flood functions have run on the same data, and the
    entity flags and grid are unchanged.

### D. tests/test_fuzz_playthrough.py
For each level and seeds 0 to 99 (fixed), with `random.Random(seed)`:
- Generate the level and budget. Place a random number of random legal sandbags (random cells,
  ignore rejected placements via `try/except ValueError`, never exceed the budget).
- Run the full flow: `create_game_state`, `request_confirmation`, `confirm_routes`,
  `finish_flood` and read the breakdown.
- Assert these invariants: no unexpected exception; `saved + unsaved == total_population`;
  `used + remaining == allocated`; `final == population_score + bonus`; bonus is 0 when not
  passed; `passed` equals (`unsaved == 0`); the grid cell count is 300; building cells are
  unchanged; every non-shelter flag is True or False; the flooded set and the safe set do not
  overlap and together cover all 300 cells.
- Then `retry_level` and assert the board is clean and the layout identical.
- Also fuzz the baseline route: placing it passes every time with exactly SANDBAG_MARGIN left.
The test must run in a few seconds.

### E. README.md
Written for a university instructor and for the student. Sections:
1. Title and one-paragraph description.
2. Requirements and installation (Python version, venv, `pip install -r requirements.txt`),
   Windows and Mac/Linux commands.
3. How to run the game and how to run the tests (`pytest -v`, `python -m pyflakes *.py`).
4. How to play (short, matches the in-game instructions) and the scoring formulas.
5. Project structure: the real file tree with one line per module, marking which modules are
   pure logic (no pygame) and which use pygame.
6. Architecture overview: the two state machines (screens, phases), the grid as single source
   of truth, "backend first, animation second", and the seeded level generator.
7. Algorithms: recursive DFS connectivity (why recursion, base cases, depth safety), greedy
   shortest-path baseline (BFS, why it is an upper bound, shared sections counted once), seeded
   random generation with retries.
8. Course concept map: a table of concept (variables, conditionals, loops and nested loops,
   2D lists, dictionaries, functions, recursion, algorithms, random, validation, modular
   programming) to the file and function that demonstrates it.
9. Design decisions that override the original specification: D1 to D7 each in one or two lines,
   plus a list of SPEC items they replace (for example 8.1 relay rule, 9.2 bonus example,
   "level population combinations", per-level margins).
10. Testing: how many tests, what they cover, and a table mapping SPEC 15 items 1 to 19 to the
    test names in tests/test_spec_section15.py.
11. Known limitations (link to docs/KNOWN_ISSUES.md) and credits (Python, Pygame).
The numbers in the README (test count, baseline and budget table for the three default seeds,
the 525 reference score) must come from actually running the code, not from memory. The
README states the date and the Python and Pygame versions used.

### F. docs/DEMO_NOTES.md
A viva cheat sheet in plain language:
- A 2-minute demo script (menu, instructions, Level 1 play, flood, results, retry, continue).
- For each concept in the SPEC 13 list: file, function, and a 2 to 3 sentence explanation.
- A step-by-step trace of `dfs_visit` on a small example (about 6 cells) written for explaining
  aloud, plus why a visited set prevents infinite loops.
- A worked example of the baseline algorithm showing how a shared trunk is counted once.
- A list of 10 questions an instructor might ask, each with a short answer and the file to
  open.

### G. docs/QA_CHECKLIST.md
A checkbox list the student runs by hand: the menu and instructions screens, each acceptance
criterion from F01 to F11 that is visible on screen (grid, hover coordinates, building labels,
sandbag place/remove/limit, dialog, flood, skip, results numbers, retry, continue only when
everyone is saved, summary, play again, main menu, exit), plus checks for resizing/closing,
and a "run it three times and compare Level 1" step. Each item has an empty box and a space
for notes.

### H. docs/KNOWN_ISSUES.md
Only genuine remaining issues, each with: description, impact, and the reason it was left.
Include the design limitations that remain by choice (for example the simple left-to-right flood,
the baseline being an upper bound, no menu button during play, no save/resume).

## Acceptance criteria
- [ ] `pytest -v` passes. The report gives the total count and the count per file.
- [ ] `python -m pyflakes *.py tests/*.py` reports nothing.
- [ ] `tests/test_spec_section15.py` has exactly 19 tests, named by SPEC item number.
- [ ] The fuzz test runs all levels and seeds with no exception and all invariants holding.
- [ ] With the default settings the terminal shows no debug prints while playing.
- [ ] `grep` or search shows no `pygame` import in any pure logic module.
- [ ] No `pygame.font.Font(...)` call inside any function that runs every frame.
- [ ] No literal layout/timing/colour numbers remain in main.py and interface.py (list any
      justified exceptions in the report).
- [ ] README has all 11 sections and its numbers match a real run.
- [ ] DEMO_NOTES.md, QA_CHECKLIST.md and KNOWN_ISSUES.md exist.
- [ ] A fresh clone works: new venv, `pip install -r requirements.txt`, `pytest`, `python
      main.py` (the plan describes how this is checked, for example in a temporary folder).
- [ ] Game behaviour is identical to F11 (the manual QA checklist passes).

## Python concepts demonstrated
Whole-project integration, constants and configuration, documentation and docstrings,
test traceability, property-style invariant testing with seeded random data, code review and
dead-code removal, reproducible installation.

## Out of scope
New gameplay, new screens, new levels, sound, images or fonts, saving, difficulty tuning,
algorithm changes, refactoring that changes behaviour, packaging as an executable.

## End-of-feature report (required)
What was cleaned (list every deletion and every constant moved), the pytest result with counts
per file, the pyflakes result, the SPEC 14/3.3 check table, the README numbers and where they
came from, any bug found and how it was fixed or logged, Python concepts used, how to run and
test everything, then STOP.