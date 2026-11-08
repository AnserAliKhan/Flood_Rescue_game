"""
Headless smoke tests for interface.py and main.py rendering routines.
Sets SDL_VIDEODRIVER='dummy' so tests run headlessly in all environments.
Verifies that no drawing call raises NameError, KeyError, or TypeError.
"""
import os
os.environ["SDL_VIDEODRIVER"] = "dummy"

import pygame
import pytest
import config
from config import (
    ROWS, COLS, CELL_EMPTY, CELL_SANDBAG, CELL_SHELTER, CELL_HOUSE,
    BTN_SANDBAG_RECT, BTN_SANDBAG_LABEL, BTN_RESET_RECT, BTN_RESET_LABEL,
    BTN_CONFIRM_RECT, BTN_CONFIRM_LABEL, BTN_CONTINUE_LABEL, BTN_SUMMARY_LABEL,
    COLOR_HOVER, COLOR_SELECTED
)
from grid import create_grid
from entities import place_entity
import interface
import campaign


@pytest.fixture(scope="module")
def screen():
    """Initializes pygame headlessly and returns a 1200x750 surface."""
    pygame.init()
    surf = pygame.display.set_mode((1200, 750))
    yield surf
    pygame.quit()


# ---- Smoke Test 1: Planning phase with placed sandbags ----

def test_smoke_planning_phase(screen):
    """Draws all planning phase visual components without error."""
    grid = create_grid(ROWS, COLS)
    grid[0][0] = CELL_SHELTER
    grid[0][1] = CELL_SANDBAG
    grid[0][2] = CELL_HOUSE

    interface.draw_grid(screen, grid)
    interface.draw_cell_labels(screen, grid)
    interface.draw_coordinates(screen)
    interface.draw_highlight(screen, (0, 1), COLOR_HOVER)
    interface.draw_highlight(screen, (0, 2), COLOR_SELECTED)

    interface.draw_panels(
        screen, hover_info="House #0", selected_info="(0, 2)",
        pop_info=20, build_info=7, sandbag_info="Sandbags: 25 / 29",
        phase_name="planning", current_level=1, campaign_score=0
    )

    interface.draw_legend(screen)
    btn_font = pygame.font.Font(None, 30)
    interface.draw_button(screen, BTN_SANDBAG_RECT, BTN_SANDBAG_LABEL, btn_font, True, False)
    interface.draw_button(screen, BTN_RESET_RECT, BTN_RESET_LABEL, btn_font, False, True)
    interface.draw_button(screen, BTN_CONFIRM_RECT, BTN_CONFIRM_LABEL, btn_font, False, False)
    interface.draw_message(screen, "Testing feedback message", btn_font)


# ---- Smoke Test 2: Confirmation dialog ----

def test_smoke_confirm_dialog(screen):
    """Draws the confirmation dialog without error."""
    font = pygame.font.Font(None, 30)
    interface.draw_confirm_dialog(screen, remaining=5, font=font)


# ---- Smoke Test 3: Flooding animation (start, middle, end) ----

def test_smoke_flood_animation(screen):
    """Draws the flood sweep at step 0, 15, and 30 without error."""
    grid = create_grid(ROWS, COLS)
    entities = []
    place_entity(grid, entities, CELL_SHELTER, 5, 15)
    place_entity(grid, entities, CELL_HOUSE, 5, 20)

    font = pygame.font.Font(None, 32)
    interface.draw_flood_banner(screen, font)

    # Step 0: no flooded cells
    interface.draw_flood(screen, set(), -1)
    interface.draw_flooded_buildings(screen, entities, set())

    # Step 15: wave reached column 15
    mid_flooded = {(r, c) for r in range(ROWS) for c in range(15)}
    interface.draw_flood(screen, mid_flooded, 14)
    interface.draw_flooded_buildings(screen, entities, mid_flooded)

    # Step 30: wave completed
    all_flooded = {(r, c) for r in range(ROWS) for c in range(COLS)}
    interface.draw_flood(screen, all_flooded, 29)
    interface.draw_flooded_buildings(screen, entities, all_flooded)


# ---- Smoke Test 4: Results panel (passed and failed) ----

def test_smoke_results_panel(screen):
    """Draws results panel for passed (levels 1-2 vs level 3) and failed breakdowns."""
    font = pygame.font.Font(None, 28)

    # 1. Passed breakdown on Level 1 (Continue to Next Level)
    breakdown_passed = {
        "passed": True,
        "saved_people": 20, "unsaved_people": 0, "total_population": 20,
        "houses_connected": 5, "schools_connected": 2, "hospitals_connected": 0,
        "sandbags_allocated": 29, "sandbags_used": 24, "sandbags_remaining": 5,
        "population_score": 100, "efficiency_bonus": 25, "final_score": 125
    }
    interface.draw_results_panel(
        screen, breakdown_passed, can_continue=True, font=font,
        current_level=1, continue_label=BTN_CONTINUE_LABEL
    )

    # 2. Passed breakdown on Level 3 (View Final Summary)
    interface.draw_results_panel(
        screen, breakdown_passed, can_continue=True, font=font,
        current_level=3, continue_label=BTN_SUMMARY_LABEL
    )

    # 3. Failed breakdown (Cannot continue)
    breakdown_failed = {
        "passed": False,
        "saved_people": 10, "unsaved_people": 10, "total_population": 20,
        "houses_connected": 2, "schools_connected": 1, "hospitals_connected": 0,
        "sandbags_allocated": 29, "sandbags_used": 15, "sandbags_remaining": 14,
        "population_score": 50, "efficiency_bonus": 0, "final_score": 50
    }
    interface.draw_results_panel(
        screen, breakdown_failed, can_continue=False, font=font,
        current_level=1
    )


# ---- Smoke Test 5: Final summary screen (full, partial, empty) ----

def test_smoke_final_summary(screen):
    """Draws final summary screen for full, partial, and empty campaigns without error."""
    font_title = pygame.font.Font(None, 42)
    font_table = pygame.font.Font(None, 28)
    font_large = pygame.font.Font(None, 56)

    # 1. Full 3-level campaign
    c_full = campaign.create_campaign()
    c_full["level_results"] = {
        1: {"saved_people": 20, "total_population": 20, "sandbags_used": 24, "sandbags_allocated": 29, "population_score": 100, "efficiency_bonus": 25, "final_score": 125},
        2: {"saved_people": 30, "total_population": 30, "sandbags_used": 34, "sandbags_allocated": 39, "population_score": 150, "efficiency_bonus": 25, "final_score": 175},
        3: {"saved_people": 40, "total_population": 40, "sandbags_used": 35, "sandbags_allocated": 40, "population_score": 200, "efficiency_bonus": 25, "final_score": 225}
    }
    s_full = campaign.build_final_summary(c_full)
    interface.draw_final_summary(screen, s_full, font_title, font_table, font_large, play_again_hovered=True)
    interface.draw_final_summary(screen, s_full, font_title, font_table, font_large, play_again_hovered=False)

    # 2. Partial campaign (Level 1 only)
    c_part = campaign.create_campaign()
    c_part["level_results"] = {
        1: {"saved_people": 20, "total_population": 20, "sandbags_used": 24, "sandbags_allocated": 29, "population_score": 100, "efficiency_bonus": 25, "final_score": 125}
    }
    s_part = campaign.build_final_summary(c_part)
    interface.draw_final_summary(screen, s_part, font_title, font_table, font_large)

    # 3. Empty campaign
    c_empty = campaign.create_campaign()
    s_empty = campaign.build_final_summary(c_empty)
    interface.draw_final_summary(screen, s_empty, font_title, font_table, font_large)


# ---- Smoke Test 6: Audit config symbols referenced by interface and main ----

def test_smoke_config_symbols_exist():
    """Audits that every symbol imported from config by interface.py and main.py actually exists."""
    import symtable
    import builtins
    import importlib

    for mod_name in ("interface", "main"):
        mod = importlib.import_module(mod_name)
        with open(f"{mod_name}.py", "r") as f:
            src = f.read()
        top = symtable.symtable(src, f"{mod_name}.py", "exec")

        def walk(table):
            for s in table.get_symbols():
                if s.is_global() and not s.is_declared_global():
                    name = s.get_name()
                    if not hasattr(builtins, name) and name not in mod.__dict__:
                        pytest.fail(f"Undefined global in {mod_name}.py: {name}")
            for child in table.get_children():
                walk(child)

        walk(top)

