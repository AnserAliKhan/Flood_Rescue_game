# F11: Main Menu and Instructions Screen

## Goal
Add the entry screens from SPEC section 11: a main menu (Start Game, Instructions, Exit)
and an instructions screen with a Back button. Add a MAIN MENU button to the final summary.
The student must be able to explain: why screens (menu/instructions/game) are a separate
state machine from game phases, why the instruction text is built from config constants,
and how Start Game and Play Again both reuse the one level-loading function.

## Context
F00 to F10 are done. Read CLAUDE.md, docs/DECISIONS.md and the existing files (config.py,
campaign.py, game.py, interface.py, main.py, tests/test_interface_smoke.py) first. Rules:
- Pure logic must not import pygame. `screens.py` is pure logic.
- The game phase table (`ALLOWED_TRANSITIONS`, F10) must NOT change. `summary` keeps no
  outgoing transitions. Leaving the summary means creating a fresh state/campaign, as with
  Play Again.
- D4: Start Game and Play Again give the identical Level 1 layout (same seeds).
- F10 has ONE level-loading function in main.py. Start Game must use it, not copy it.
- Drawing code is not covered by normal tests, so this feature extends the headless smoke
  tests and requires a clean `pyflakes`.

## Scope: files to create / change
- CREATE `screens.py`: pure logic, NO pygame import
- CREATE `tests/test_screens.py`: pytest tests
- CHANGE `config.py`: screen names, screen transition table, button rectangles and captions,
  instruction text constants, layout numbers
- CHANGE `interface.py`: `draw_menu`, `draw_instructions`, and a second button on the summary
- CHANGE `main.py`: app screen routing, menu/instructions/summary button handling, Exit
- CHANGE `tests/test_interface_smoke.py`: new drawing smoke tests

Do NOT change game.py, campaign.py, scoring.py, flood.py, baseline.py, level_generator.py or
the game phase transition table. No sound, no settings screen, no saved data, no menu
button during play.

## Requirements

### config.py additions (each with a comment)
- Screen names: `SCREEN_MENU = "menu"`, `SCREEN_INSTRUCTIONS = "instructions"`,
  `SCREEN_GAME = "game"`.
- `ALLOWED_SCREEN_TRANSITIONS`:
  ```
  "menu":         ["instructions", "game"],
  "instructions": ["menu"],
  "game":         ["menu"],
  ```
  Comment: Exit is not a screen. It ends the program. "game to menu" is only allowed from
  the summary phase (checked separately).
- Menu button rectangles in a dictionary `MENU_BUTTONS = {"start": (...), "instructions":
  (...), "exit": (...)}` and captions `MENU_CAPTIONS` ("START GAME", "INSTRUCTIONS", "EXIT").
  Suggested layout (the plan must confirm the numbers): three buttons, 360 x 64 px, centred
  horizontally, with 24 px gaps, starting around y = 340.
- `INSTRUCTIONS_BACK_RECT` and caption "BACK".
- Summary buttons: `SUMMARY_PLAY_AGAIN_RECT` (the existing PLAY AGAIN rectangle, moved) and
  `SUMMARY_MENU_RECT` (new, caption "MAIN MENU") side by side, centred as a pair, no overlap.
  The plan must show the numbers and prove everything fits in 1200 x 750.
- Text constants: menu title ("FLOOD RESCUE"), a tagline (for example "Build routes. Save
  everyone."), instructions title, and the instruction content (see below).
- Colours: menu background, title colour, hover/normal button colours (reuse the existing
  button colours where possible).

### Instruction content (config.py, text templates)
Defined as a list of sections. Each section is a title and a list of short line templates,
for example `("How to play", ["1. Press S or click SANDBAG TOOL.", ...])`. Templates may
contain placeholders such as `{points}`, `{margin}`, `{bonus}`. The sections to include:
1. **Goal**: connect every building to the green shelter with sandbags before the flood.
2. **How to play**: S key or the tool button; left click an empty cell to place; click or
   right-click a sandbag to remove it; RESET clears all sandbags; CONFIRM starts the flood.
3. **Rules**: sandbags connect up, down, left, right only (never diagonal); buildings link
   directly to each other and to the shelter, so a building touching the network needs no
   sandbags; sandbags cannot be placed on buildings or the shelter.
4. **People**: house 2, school 5, hospital 8 (the numbers come from `POPULATION`, not typed).
5. **Scoring**: `{points}` points per person saved; leftover sandbags earn `{bonus}` points
   each, but ONLY if everyone is saved.
6. **Levels**: three levels with more people each time; the sandbag budget is a minimum plus
   `{margin}` extra; CONTINUE appears only if everyone was saved; otherwise retry.
Every line must be short enough for one column (the smoke test checks this).

### screens.py (pure logic, no pygame)
Keep names simple; the plan may adjust them. Each function gets a docstring with a one-line
example.
- `create_app_state()`: returns `{"screen": "menu"}` (exactly this one key).
- `change_screen(app, new_screen)`: checks `ALLOWED_SCREEN_TRANSITIONS`. Raises `ValueError`
  for an illegal or unknown screen and leaves `app` unchanged. Otherwise sets the screen.
- `can_return_to_menu(state)`: True only when the game phase is `summary`. `state` is the
  F06 game state dictionary.
- `button_at(buttons, x, y)`: `buttons` is a dictionary name -> `(x, y, w, h)`. Returns the
  name of the button containing the point, or `None`. Checks the point against the rectangle
  with comparisons (no pygame). Edges: the left and top edges are inside, the right and
  bottom edges are outside.
- `build_instruction_sections()`: returns a list of `(title, [lines])` with all placeholders
  filled from config (`POINTS_PER_PERSON`, `EFFICIENCY_BONUS_PER_SANDBAG`, `SANDBAG_MARGIN`,
  `POPULATION`). Reads the config values when called (not at import time), so a test can
  change them. Raises `ValueError` if a placeholder is left unfilled.

### interface.py additions (Pygame only, never modifies game data)
- `draw_menu(screen, hovered, font_title, font_button, font_small)`: full-window menu: title,
  tagline, three buttons from `MENU_BUTTONS` drawn with a loop and `draw_button`. The hovered
  button looks hovered. The grid and panels are NOT drawn.
- `draw_instructions(screen, sections, hovered, fonts...)`: full-window screen: title, the
  sections laid out in two columns using loops, and the BACK button.
- `draw_final_summary` (F10) draws two buttons, PLAY AGAIN and MAIN MENU, with hover states.
  Table and totals are unchanged.
- No game rules here, and no recalculation of anything.

### main.py behaviour
- Create `app = create_app_state()`. The program starts on the menu. No level is generated
  until Start Game is clicked.
- Event and drawing routing by `app["screen"]`:
  - **menu**: hover and click use `button_at(MENU_BUTTONS, ...)`.
    START GAME loads Level 1 with a new campaign using the F10 loading function, then
    `change_screen(app, "game")`. INSTRUCTIONS goes to the instructions screen. EXIT quits
    cleanly (`pygame.quit()`, no traceback). ESC also exits.
  - **instructions**: BACK or ESC returns to the menu.
  - **game**: exactly the F10 behaviour. In the summary phase, PLAY AGAIN works as in F10, and
    MAIN MENU (allowed only if `can_return_to_menu(state)`) discards the campaign and sets the
    screen to menu. ESC in the game behaves exactly as before.
- Starting the game from the menu twice (menu, game, summary, menu, game) always gives the
  identical Level 1 layout and a clean state, empty scores and no leftover flood or water.
- `DEBUG_LEVEL_KEYS` keys act only on the game screen in the planning phase.
- Wrap screens/campaign calls in try/except for `ValueError` and show a message instead of
  crashing (on the game screen) or ignore it safely (on the menu).
- All F01 to F10 behaviour inside the game screen is unchanged.

## Acceptance criteria
- [ ] The program opens on the main menu with three buttons: START GAME, INSTRUCTIONS, EXIT.
- [ ] Hovering a button changes its look.
- [ ] START GAME opens Level 1 - Easy, identical to earlier runs.
- [ ] INSTRUCTIONS shows all six sections, and every line is fully inside its column. BACK and
      ESC return to the menu.
- [ ] The instructions show the correct numbers from config (5 points per person, 5 per
      leftover sandbag, margin 5, populations 2/5/8).
- [ ] EXIT closes the program with no error. ESC on the menu does the same.
- [ ] After finishing Level 3, the summary shows PLAY AGAIN and MAIN MENU without overlap.
- [ ] MAIN MENU returns to the menu. START GAME then gives a fresh Level 1 with scores cleared
      and no water or highlights.
- [ ] Nothing in the game phase transition table changed, and no old game tests were edited
      (except if an import or constant name required it, which the plan must list).
- [ ] `screens.py` has no pygame import.
- [ ] `pytest` passes and `python -m pyflakes *.py` reports no problems.

## Tests (tests/test_screens.py, no pygame window)
1. `create_app_state` has exactly the key `"screen"` and starts on `"menu"`.
2. Legal changes work: menu to instructions, instructions to menu, menu to game, game to menu.
3. Illegal changes raise `ValueError` and leave `app` unchanged: instructions to game, menu to
   menu, game to instructions, an unknown screen name.
4. Every screen in `ALLOWED_SCREEN_TRANSITIONS` (keys and targets) is a defined constant.
5. `can_return_to_menu` is True only for phase `summary`, and False for planning, confirming,
   flooding and results.
6. `button_at` returns the right name for a point in the middle of each menu button, `None` for
   points between buttons and outside the window, includes the top-left pixel of a button,
   and excludes the pixel just beyond the bottom-right.
7. The menu buttons and the instruction BACK rectangle are inside the window, and no two menu
   buttons overlap. The two summary buttons are inside the window and do not overlap.
8. `build_instruction_sections` returns 6 sections, none empty, with no `{` or `}` left in any
   line.
9. The built text contains `str(POINTS_PER_PERSON)`, `str(SANDBAG_MARGIN)`,
   `str(EFFICIENCY_BONUS_PER_SANDBAG)` and the three `POPULATION` values.
10. `monkeypatch` changes `POINTS_PER_PERSON`, `SANDBAG_MARGIN` and the bonus weight, and the
    built text follows.
11. A template with an unknown placeholder (inserted with `monkeypatch`) raises `ValueError`.
12. The full screen flow with `create_app_state` and `change_screen` (menu, game, menu,
    instructions, menu) works.
13. Menu to game to summary to menu to game gives the same first-level layout as the first time
    (use `campaign.create_campaign` and `campaign.prepare_level`) and a fresh campaign with no
    stored results.

## Tests: additions to tests/test_interface_smoke.py (headless, SDL dummy driver)
1. `draw_menu` runs for no hover and for each of the three hover states.
2. `draw_instructions` runs with the real sections, with and without BACK hover.
3. Every instruction line, rendered with the font that `draw_instructions` uses, is narrower
   than the column width. (Fail with the offending line if not.)
4. `draw_final_summary` runs for full, partial and empty campaigns with both buttons and
   hover states.
5. All F10 smoke tests still pass.
If a function can't be tested without refactoring, the plan must say so and not rewrite it
silently.

## Python concepts demonstrated
Two independent state machines (screens and phases), lookup tables, string templates with
`str.format`, dictionaries of rectangles, hit-testing with comparisons, reusing one
level-loading function, event routing with conditionals, drawing from data with loops, clean
program exit, headless testing of drawing code.

## Out of scope
A menu button or ESC-to-menu during play, saving or resuming, high scores, a settings screen,
sound, animation on the menu, a credits
