# F10: Three Levels, Retry/Continue Flow, Final Summary

## Goal
Turn the single playable level into the full three-level game. Continue loads the next
generated level, Retry replays the same one, and after Level 3 a final summary shows the
scores of all levels, the total score, people saved and overall sandbag efficiency, with a
PLAY AGAIN button. The student must be able to explain: why progress is kept in a separate
`campaign` dictionary, why a score is recorded only on Continue, and how restarting
returns the game to exactly the same Level 1 (seeds, D4).

## Context
F00 to F09 are done. Read CLAUDE.md, docs/DECISIONS.md (amended D5, D7) and the existing
files (config.py, grid.py, entities.py, sandbags.py, pathfinding.py, scoring.py,
level_generator.py, baseline.py, flood.py, game.py, interface.py, main.py) first. Rules:
- Pure logic must not import pygame. `campaign.py` and `game.py` are pure logic.
- D1: building counts and populations per level are fixed. D4: fixed seeds, so Retry and
  Restart give identical layouts. D2: budget = baseline + SANDBAG_MARGIN for all levels.
  D6: difficulty only from more people/buildings. D7: Continue only if all people saved.
- D5 (amended): the bonus is 0 unless all people are saved. A recorded level is always a
  passed level, so recorded levels always have saved == total population.
- Backend first: results come from the stored breakdown. Drawing never recalculates.
- This feature replaces the temporary level keys from F08 ("replaced by real level flow in
  F10").

## Scope: files to create / change
- CREATE `campaign.py`: pure logic, NO pygame import
- CREATE `tests/test_campaign.py`: pytest tests
- CREATE `tests/test_interface_smoke.py`: headless drawing smoke tests
- CHANGE `config.py`: summary phase, transition table, level names, button and text
  constants, debug flag
- CHANGE `game.py`: `show_summary`, updated rules for the new phase
- CHANGE `tests/test_game.py`: update the affected tests (listed below)
- CHANGE `interface.py`: Continue caption, level and progress readout, final summary screen
- CHANGE `main.py`: use the campaign, load levels, Continue and Restart handling

Do NOT create other modules. No main menu, instructions screen, saved high scores, sound,
new level designs or changes to the generator, baseline, scoring or flood logic.

## Requirements

### config.py additions (each with a comment)
- `PHASE_SUMMARY = "summary"` and `NUM_LEVELS` (derived from `LEVEL_BUILDINGS`, not typed).
- Updated `ALLOWED_TRANSITIONS`:
  ```
  "planning":   ["confirming"],
  "confirming": ["planning", "flooding"],
  "flooding":   ["results"],
  "results":    ["planning", "summary"],
  "summary":    [],
  ```
  Comment: leaving the summary is done by creating a new state (Play Again). F11 will add
  a way back to the menu.
- `LEVEL_NAMES = {1: "Easy", 2: "Medium", 3: "Hard"}`
- `DEBUG_LEVEL_KEYS = False` (comment: temporary developer aid, keys 1/2/3 in planning).
- Captions: "CONTINUE TO NEXT LEVEL" (already exists), "VIEW FINAL SUMMARY", "PLAY AGAIN".
  Texts: summary title, column headings, the line describing the efficiency figure, level
  intro message template, "Game complete" text.
- Summary layout: the PLAY AGAIN button rectangle and table position/size numbers. The plan
  must show the numbers and prove that nothing overlaps and everything fits the 1200 x 750
  window.
- Colours for summary table lines, totals and highlights (reuse existing where possible).
- `CURRENT_LEVEL` is no longer used by main.py (the level comes from the campaign). Keep it
  only if an older test needs it, with a comment.

### campaign.py (pure logic, no pygame)
Keep names simple; the plan may adjust them. Each function gets a docstring with a
one-line example.
- `create_campaign(start_level=1)`: returns a dictionary with exactly the keys `"level"`
  (the current level) and `"level_results"` (a dictionary: level number to the stored
  breakdown; empty at the start). Raises `ValueError` for a level outside 1..NUM_LEVELS.
- `prepare_level(level)`: calls `generate_level(level)`, then `calculate_baseline_sandbags`
  and `calculate_sandbag_budget`. Returns `(grid, entities, baseline, total_budget)`.
  Raises `ValueError` for an unknown level.
- `is_last_level(campaign)`: True when `campaign["level"] == NUM_LEVELS`.
- `is_campaign_complete(campaign)`: True when every level 1..NUM_LEVELS has a stored result.
- `record_level_result(campaign, breakdown)`: stores a COPY of the breakdown under the
  current level. Raises `ValueError` if `breakdown["passed"]` is not True, or if that level
  already has a result.
- `complete_level(campaign, state)`: called when the player clicks Continue.
  - Raises `ValueError` unless `game.can_continue(state)` is True. On any error, the
    campaign is left unchanged.
  - Records the level result (from `state["breakdown"]`).
  - If it was the last level, returns `"summary"` (the level number stays the same).
  - Otherwise increases `campaign["level"]` by 1 and returns `"next_level"`.
  It does NOT change `state` and does NOT load levels.
- `build_final_summary(campaign)`: returns a dictionary with exactly these keys:
  - `"rows"`: a list with one dictionary per RECORDED level, in level order, each with
    `"level"`, `"saved_people"`, `"total_population"`, `"sandbags_used"`,
    `"sandbags_allocated"`, `"population_score"`, `"efficiency_bonus"`, `"final_score"`
  - `"total_score"`: sum of the rows' final scores
  - `"total_people_saved"`, `"total_population"`
  - `"sandbags_allocated"`, `"sandbags_used"`, `"sandbags_remaining"` (all summed)
  - `"efficiency_percent"`: `100 * sandbags_remaining / sandbags_allocated`, rounded to one
    decimal; 0.0 when nothing is recorded (no division by zero)
  - `"levels_completed"`: how many levels are recorded
  Works for a partial campaign (used by the debug keys). Does not modify the campaign.

### game.py changes
- `show_summary(state)`: only valid in the results phase and only if
  `state["breakdown"]["passed"]` is True (else `ValueError`, state unchanged). Changes the
  phase to summary. Nothing else changes.
- `is_editing_allowed` and `can_continue` are False in the summary phase.
- `create_game_state()` is unchanged (keys `"phase"`, `"breakdown"`, `"safe_cells"`).
- `retry_level` is unchanged and still only valid in results.

### interface.py changes (Pygame only, never modifies game data)
- The top panel shows `Level 2 / 3 - Medium`, taken from the campaign level, and a running
  `Score so far: N` (the sum of recorded levels). The existing readouts stay.
- `draw_results_panel` receives the Continue caption: "CONTINUE TO NEXT LEVEL" on levels
  1 and 2, "VIEW FINAL SUMMARY" on the last level. The level number in the panel comes from
  the campaign, not from a constant.
- `draw_final_summary(screen, summary, font_large, font_small, ...)`: a full-window screen
  (the grid and bottom panel are not drawn in this phase) with: title, a table with one row
  per recorded level (people saved / total, sandbags used / allocated, population score,
  bonus, level score), then TOTAL SCORE (largest text), total people saved, overall sandbag
  efficiency as a percentage, and the PLAY AGAIN button. Table rows are drawn with a loop.
- Buttons reuse `draw_button`. No copy-pasted blocks.

### main.py behaviour
- Create `campaign = create_campaign()` once. Write one function (or one block) that loads
  a level: `prepare_level(campaign["level"])`, sets `grid`, `entities`, `total_budget`,
  creates a fresh `state`, clears the selection, the message, `tool_active` and the flood
  variables, prints `Level N: baseline X, budget Y` (temporary debug output), and shows the
  level intro message. Start of game, Continue and Play Again all use it. No duplicated
  loading code.
- Results phase, Continue (only visible when allowed): call `complete_level`.
  - Returns `"next_level"`: load the next level.
  - Returns `"summary"`: call `show_summary(state)`.
- Retry still uses `retry_level` and never calls the generator, never touches the campaign.
- Summary phase: draw only the summary screen. PLAY AGAIN creates a new campaign, loads
  Level 1 (identical layout to the first run, D4) and starts planning. ESC exits. No grid
  input.
- If `DEBUG_LEVEL_KEYS` is True, keys 1/2/3 in the planning phase start a fresh campaign at
  that level and load it. If False, those keys do nothing. They never act in other phases.
- Wrap campaign and game calls in try/except for `ValueError` and show the message instead
  of crashing.
- Everything from F01 to F09 outside these changes behaves as before.

## Acceptance criteria
- [ ] The game starts on Level 1 - Easy. The top panel shows `Level 1 / 3 - Easy`.
- [ ] Winning a level (everyone saved) shows CONTINUE and RETRY. Failing shows only RETRY.
- [ ] Continue on Level 1 loads Level 2 (People 30, Buildings 9) with a fresh board, a fresh
      budget (its own baseline + 5), and no water, no red or green highlights.
- [ ] Continue on Level 2 loads Level 3 (People 40, Buildings 11).
- [ ] On Level 3 the Continue button reads VIEW FINAL SUMMARY and opens the summary.
- [ ] The summary lists three levels, their scores, the total, people saved (total 90 in a
      normal full run) and the overall sandbag efficiency percentage. Every number comes from
      the stored results.
- [ ] A perfect baseline route on all three levels gives level scores of
      `population + margin x weight` each and a total of 525 with the current constants.
- [ ] Retrying a failed level keeps the same layout and budget and does not change the
      recorded scores. Retrying a passed level and then failing it does not remove a score
      (nothing is recorded until Continue).
- [ ] PLAY AGAIN starts Level 1 with the same layout as the first time and empty scores.
- [ ] With `DEBUG_LEVEL_KEYS = False` the keys 1/2/3 do nothing.
- [ ] `campaign.py` and `game.py` have no pygame import.
- [ ] `pytest` passes, including all earlier tests, and `python -m pyflakes *.py` (or
      equivalent) reports no undefined names.

## Tests (tests/test_campaign.py, no pygame window)
Use `prepare_level` and the baseline route (from `calculate_baseline_route`) for end-to-end
tests. Hand-compute expected totals using config constants.
1. `create_campaign` has exactly the keys `"level"` and `"level_results"`, level 1, and empty
   results. `create_campaign(0)` and `create_campaign(4)` raise `ValueError`.
2. `prepare_level` for levels 1, 2, 3: budget equals baseline plus `SANDBAG_MARGIN`, entity
   counts match `LEVEL_BUILDINGS`, population 20 / 30 / 40. Levels 0 and 4 raise `ValueError`.
3. `prepare_level` is deterministic: the same level twice gives identical entity lists and
   the same baseline and budget.
4. Difficulty: buildings 7 < 9 < 11 and population 20 < 30 < 40 across `prepare_level`.
5. `record_level_result` stores a copy: changing the original breakdown afterwards does not
   change the stored one.
6. `record_level_result` raises `ValueError` for a breakdown with `passed` False, and for a
   level that already has a result. The campaign is unchanged after an error.
7. `complete_level` on a passed results state of level 1 returns `"next_level"`, the level
   becomes 2 and level 1's result is stored.
8. `complete_level` on level 3 returns `"summary"`, the level stays 3 and the result is stored.
9. `complete_level` raises `ValueError` (campaign unchanged) when the state is in planning,
   confirming, flooding or summary, and when the level was not passed.
10. `is_last_level` and `is_campaign_complete` give the right answers at each stage.
11. `build_final_summary` for a full campaign: totals match hand-computed sums (people 90,
    total population 90, population scores 100 + 150 + 200, bonuses from the margin and
    weight), rows are in level order, and efficiency equals
    `round(100 * remaining / allocated, 1)`.
12. `build_final_summary` for a partial campaign (only level 1 recorded) works, and for an
    empty campaign returns zeros with `efficiency_percent == 0.0` and no exception. It does
    not modify the campaign.
13. Full headless playthrough: for each level, `prepare_level`, place every baseline route cell
    with `place_sandbag` (using the level's budget), then `create_game_state`,
    `request_confirmation`, `confirm_routes`, `finish_flood`, `complete_level`, and for the last
    level `show_summary`. Every level passes with `sandbags_remaining == SANDBAG_MARGIN`. The
    final total score equals
    `450 + 3 x SANDBAG_MARGIN x EFFICIENCY_BONUS_PER_SANDBAG` (written using config constants).
14. Fail-then-retry: a level confirmed with no sandbags fails, `complete_level` raises, Retry
    returns to planning with the same entities and budget, and the campaign is unchanged.
15. Pass, then retry, then fail: nothing was recorded after the first pass because Continue was
    not clicked, and the campaign has no result for that level.
16. Restart: a new `create_campaign` is independent of the old one (changing the old dictionary
    does not change the new one), and `prepare_level(1)` after a restart returns the same layout
    as the first time.
17. `monkeypatch` changes `SANDBAG_MARGIN` and the budgets follow.

## Tests: changes to tests/test_game.py
The plan must list the exact tests that change. Expected:
- Legal transitions: results to summary is legal. Summary to anything is illegal. Planning,
  confirming and flooding to summary are illegal.
- Every phase in `ALLOWED_TRANSITIONS` (keys and targets) is a defined constant (includes summary).
- `is_editing_allowed` and `can_continue` are False in the summary phase.
New tests:
- `show_summary` outside results raises `ValueError`. In results with `passed` False it raises
  `ValueError` and the state is unchanged. In results with `passed` True it changes the phase to
  summary and nothing else.
- `retry_level` from the summary phase raises `ValueError`.

## Tests (tests/test_interface_smoke.py, headless)
Set `os.environ["SDL_VIDEODRIVER"] = "dummy"` before importing pygame. Create a dummy
`pygame.Surface` of the window size and the fonts. Call the real drawing functions with real data
and assert only that nothing raises (no `NameError`, `KeyError`, `TypeError`):
1. Planning with some sandbags placed.
2. The confirmation dialog.
3. The flooding phase, at the start, the middle and the end of the sweep.
4. Results for a passed breakdown and for a failed one.
5. The final summary for a full campaign, a partial one and an empty one.
6. Every `config` name that `interface.py` and `main.py` use exists (for example, import both
   modules and check that `pyflakes` is clean, or parse their imports).
If the plan finds that a function cannot be tested without refactoring it, it must say so and not
rewrite it silently.

## Python concepts demonstrated
Dictionaries as game progress, state machine extension by editing a lookup table, composing pure
functions into a game flow, aggregating data with loops, percentage calculation with rounding and
a zero-division guard, copying data to protect it, deterministic restarts through seeds, end-to-end
testing, headless smoke testing of drawing code.

## Out of scope
Main menu, instructions screen and the "main menu" button (F11), saved high scores or files, a
level select screen, per-level attempt counters, sound, animations on the summary, any change to
the generator, baseline, scoring, flood or connectivity logic, difficulty tuning.

## End-of-feature report (required)
What was built, important code sections (especially `complete_level`, `build_final_summary` and the
level-loading function), the full game flow as a short diagram in text, Python concepts used, how
to run and test it (including how to enable `DEBUG_LEVEL_KEYS`), which F06/F07 tests were changed
and why, results of `pytest -v` and `pyflakes`, known limitations (the menu is missing, debug
output prints to the terminal, the summary has no way back except Play Again), then STOP.