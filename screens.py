"""
screens.py - Screen State Machine and Instructions Logic (F11)

Pure logic module: manages high-level application screen state (menu, instructions, game),
screen transitions, button coordinate hit-testing, and dynamic instruction text generation.

RULES:
- Zero Pygame imports.
- Purely deterministic and safe for automated unit testing.
"""

import config
from config import (
    SCREEN_MENU, ALLOWED_SCREEN_TRANSITIONS, PHASE_SUMMARY
)


def create_app_state():
    """
    Creates and returns the initial application screen state.

    Example:
        app = create_app_state()  # -> {"screen": "menu"}
    """
    return {"screen": SCREEN_MENU}


def change_screen(app, new_screen):
    """
    Transitions the application to new_screen if allowed by ALLOWED_SCREEN_TRANSITIONS.
    Raises ValueError for an illegal transition or unknown screen, leaving app unchanged.

    Example:
        change_screen(app, "game")  # updates app["screen"] to "game"
    """
    current = app.get("screen")
    allowed = ALLOWED_SCREEN_TRANSITIONS.get(current, [])
    if new_screen not in allowed:
        raise ValueError(
            f"Cannot transition from screen '{current}' to '{new_screen}'. "
            f"Allowed next screens: {allowed}"
        )
    app["screen"] = new_screen


def can_return_to_menu(game_state):
    """
    Checks whether returning to the Main Menu from the game is permitted.
    Allowed ONLY when the game state exists and is currently in the 'summary' phase.

    Example:
        can_return_to_menu({"phase": "summary"})  # -> True
    """
    if not game_state or not isinstance(game_state, dict):
        return False
    return game_state.get("phase") == PHASE_SUMMARY


def button_at(buttons, x, y):
    """
    Hit-tests a point (x, y) against a dictionary of name -> (bx, by, bw, bh).
    Returns the name of the button containing the point, or None.
    Rule: Left and top edges are inside; right and bottom edges are outside:
          bx <= x < bx + bw and by <= y < by + bh.

    Example:
        button_at({"start": (10, 10, 100, 50)}, 50, 20)  # -> "start"
    """
    for name, (bx, by, bw, bh) in buttons.items():
        if bx <= x < bx + bw and by <= y < by + bh:
            return name
    return None


def build_instruction_sections():
    """
    Reads instruction templates and substitutes live game rules and values from config.
    Substitutions are resolved dynamically when called so monkeypatched configs work.
    Raises ValueError if an unknown placeholder is encountered or unfilled braces remain.

    Example:
        sections = build_instruction_sections()  # -> [("Goal", [...]), ...]
    """
    # Dynamic values read at call time
    placeholders = {
        "points": config.POINTS_PER_PERSON,
        "bonus": config.EFFICIENCY_BONUS_PER_SANDBAG,
        "margin": config.SANDBAG_MARGIN,
        "house_pop": config.POPULATION.get(config.CELL_HOUSE, 2),
        "school_pop": config.POPULATION.get(config.CELL_SCHOOL, 5),
        "hospital_pop": config.POPULATION.get(config.CELL_HOSPITAL, 8),
    }

    sections = []
    for title, template_lines in config.INSTRUCTION_SECTIONS_TEMPLATES:
        rendered_lines = []
        for line in template_lines:
            try:
                rendered = line.format(**placeholders)
            except (KeyError, ValueError, IndexError) as err:
                raise ValueError(f"Failed to substitute placeholder in instruction line '{line}': {err}")

            if "{" in rendered or "}" in rendered:
                raise ValueError(f"Unfilled placeholder remaining in instruction line: '{rendered}'")

            rendered_lines.append(rendered)
        sections.append((title, rendered_lines))

    return sections

