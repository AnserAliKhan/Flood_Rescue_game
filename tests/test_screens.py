"""
Unit tests for screens.py (Feature F11).
Pure logic tests: zero Pygame dependencies.
"""

import pytest
import config
from config import (
    SCREEN_MENU, SCREEN_INSTRUCTIONS, SCREEN_GAME,
    ALLOWED_SCREEN_TRANSITIONS, MENU_BUTTONS, INSTRUCTIONS_BACK_RECT,
    SUMMARY_PLAY_AGAIN_RECT, SUMMARY_MENU_RECT,
    PHASE_PLANNING, PHASE_CONFIRMING, PHASE_FLOODING, PHASE_RESULTS, PHASE_SUMMARY
)
import screens
import campaign


# ---- Test 1: create_app_state ----

def test_create_app_state():
    """create_app_state has exactly the key 'screen' and starts on 'menu'."""
    app = screens.create_app_state()
    assert isinstance(app, dict)
    assert list(app.keys()) == ["screen"]
    assert app["screen"] == SCREEN_MENU


# ---- Test 2: Legal Transitions ----

def test_legal_transitions():
    """Legal transitions succeed and update app['screen']."""
    app = screens.create_app_state()

    # menu -> instructions
    screens.change_screen(app, SCREEN_INSTRUCTIONS)
    assert app["screen"] == SCREEN_INSTRUCTIONS

    # instructions -> menu
    screens.change_screen(app, SCREEN_MENU)
    assert app["screen"] == SCREEN_MENU

    # menu -> game
    screens.change_screen(app, SCREEN_GAME)
    assert app["screen"] == SCREEN_GAME

    # game -> menu
    screens.change_screen(app, SCREEN_MENU)
    assert app["screen"] == SCREEN_MENU


# ---- Test 3: Illegal Transitions ----

def test_illegal_transitions():
    """Illegal transitions raise ValueError and leave app unchanged."""
    app = screens.create_app_state()

    # menu -> menu (cannot transition to self)
    with pytest.raises(ValueError):
        screens.change_screen(app, SCREEN_MENU)
    assert app["screen"] == SCREEN_MENU

    # menu -> unknown
    with pytest.raises(ValueError):
        screens.change_screen(app, "unknown_screen")
    assert app["screen"] == SCREEN_MENU

    # instructions -> game (not allowed directly)
    screens.change_screen(app, SCREEN_INSTRUCTIONS)
    with pytest.raises(ValueError):
        screens.change_screen(app, SCREEN_GAME)
    assert app["screen"] == SCREEN_INSTRUCTIONS

    # game -> instructions (not allowed directly)
    screens.change_screen(app, SCREEN_MENU)
    screens.change_screen(app, SCREEN_GAME)
    with pytest.raises(ValueError):
        screens.change_screen(app, SCREEN_INSTRUCTIONS)
    assert app["screen"] == SCREEN_GAME


# ---- Test 4: Transition Table Defined Constants ----

def test_all_transition_screens_defined():
    """Every screen in ALLOWED_SCREEN_TRANSITIONS (keys and targets) is a defined constant."""
    valid_screens = {SCREEN_MENU, SCREEN_INSTRUCTIONS, SCREEN_GAME}
    for src, targets in ALLOWED_SCREEN_TRANSITIONS.items():
        assert src in valid_screens, f"Source '{src}' not recognized"
        for tgt in targets:
            assert tgt in valid_screens, f"Target '{tgt}' from '{src}' not recognized"


# ---- Test 5: can_return_to_menu Predicate ----

def test_can_return_to_menu():
    """can_return_to_menu is True only for phase 'summary', and False for all other phases and None."""
    assert screens.can_return_to_menu({"phase": PHASE_SUMMARY}) is True
    assert screens.can_return_to_menu({"phase": PHASE_PLANNING}) is False
    assert screens.can_return_to_menu({"phase": PHASE_CONFIRMING}) is False
    assert screens.can_return_to_menu({"phase": PHASE_FLOODING}) is False
    assert screens.can_return_to_menu({"phase": PHASE_RESULTS}) is False
    assert screens.can_return_to_menu(None) is False
    assert screens.can_return_to_menu({}) is False


# ---- Test 6: button_at Hit Testing ----

def test_button_at_hit_testing():
    """button_at tests interior points, gaps, bounds, top-left inclusive, bottom-right exclusive."""
    # Test centers of menu buttons
    for name, (bx, by, bw, bh) in MENU_BUTTONS.items():
        mid_x = bx + bw // 2
        mid_y = by + bh // 2
        assert screens.button_at(MENU_BUTTONS, mid_x, mid_y) == name

        # Boundary rules:
        # Top-left corner is inside
        assert screens.button_at(MENU_BUTTONS, bx, by) == name
        # Bottom-right corner (bx + bw, by + bh) is outside
        assert screens.button_at(MENU_BUTTONS, bx + bw, by + bh) is None
        # Right boundary is outside
        assert screens.button_at(MENU_BUTTONS, bx + bw, mid_y) is None
        # Bottom boundary is outside
        assert screens.button_at(MENU_BUTTONS, mid_x, by + bh) is None
        # Point just inside bottom-right
        assert screens.button_at(MENU_BUTTONS, bx + bw - 1, by + bh - 1) == name

    # Point in vertical gap between button 1 and 2
    b1_bottom = MENU_BUTTONS["start"][1] + MENU_BUTTONS["start"][3]
    b2_top = MENU_BUTTONS["instructions"][1]
    gap_y = (b1_bottom + b2_top) // 2
    assert screens.button_at(MENU_BUTTONS, 600, gap_y) is None

    # Points outside window
    assert screens.button_at(MENU_BUTTONS, -10, -10) is None
    assert screens.button_at(MENU_BUTTONS, 1300, 800) is None


# ---- Test 7: Button Layout Bounds and Non-Overlap ----

def test_button_layouts_fit_and_no_overlap():
    """Buttons fit inside (1200, 750) window without overlapping."""
    w_width, w_height = 1200, 750

    def rect_inside(r):
        x, y, w, h = r
        return 0 <= x and 0 <= y and (x + w) <= w_width and (y + h) <= w_height

    def rects_overlap(r1, r2):
        x1, y1, w1, h1 = r1
        x2, y2, w2, h2 = r2
        return not (x1 + w1 <= x2 or x2 + w2 <= x1 or y1 + h1 <= y2 or y2 + h2 <= y1)

    # 1. Menu buttons fit inside window
    for name, r in MENU_BUTTONS.items():
        assert rect_inside(r), f"Menu button '{name}' exceeds window boundaries: {r}"

    # 2. No menu buttons overlap each other
    btn_items = list(MENU_BUTTONS.items())
    for i in range(len(btn_items)):
        for j in range(i + 1, len(btn_items)):
            n1, r1 = btn_items[i]
            n2, r2 = btn_items[j]
            assert not rects_overlap(r1, r2), f"Menu buttons '{n1}' and '{n2}' overlap!"

    # 3. Instruction BACK button inside window
    assert rect_inside(INSTRUCTIONS_BACK_RECT)

    # 4. Summary dual buttons inside window and non-overlapping
    assert rect_inside(SUMMARY_PLAY_AGAIN_RECT)
    assert rect_inside(SUMMARY_MENU_RECT)
    assert not rects_overlap(SUMMARY_PLAY_AGAIN_RECT, SUMMARY_MENU_RECT)


# ---- Test 8: Instruction Sections Count and Formatting ----

def test_build_instruction_sections_count_and_placeholders():
    """build_instruction_sections returns 6 non-empty sections with no unfilled placeholders."""
    sections = screens.build_instruction_sections()
    assert len(sections) == 6

    for title, lines in sections:
        assert isinstance(title, str) and len(title) > 0
        assert isinstance(lines, list) and len(lines) > 0
        for line in lines:
            assert "{" not in line and "}" not in line, f"Unfilled placeholder in line: {line}"


# ---- Test 9: Instruction Content Values ----

def test_build_instruction_sections_values():
    """The built text contains string versions of scoring and population constants."""
    sections = screens.build_instruction_sections()
    all_text = " ".join(" ".join(lines) for _, lines in sections)

    assert str(config.POINTS_PER_PERSON) in all_text
    assert str(config.SANDBAG_MARGIN) in all_text
    assert str(config.EFFICIENCY_BONUS_PER_SANDBAG) in all_text
    assert str(config.POPULATION[config.CELL_HOUSE]) in all_text
    assert str(config.POPULATION[config.CELL_SCHOOL]) in all_text
    assert str(config.POPULATION[config.CELL_HOSPITAL]) in all_text


# ---- Test 10: Dynamic Updating with Monkeypatch ----

def test_build_instruction_sections_monkeypatch(monkeypatch):
    """monkeypatch changes config values, and build_instruction_sections reflects changes."""
    monkeypatch.setattr(config, "POINTS_PER_PERSON", 99)
    monkeypatch.setattr(config, "SANDBAG_MARGIN", 17)
    monkeypatch.setattr(config, "EFFICIENCY_BONUS_PER_SANDBAG", 42)

    sections = screens.build_instruction_sections()
    all_text = " ".join(" ".join(lines) for _, lines in sections)

    assert "99 points" in all_text
    assert "17 margin" in all_text
    assert "42 points bonus" in all_text


# ---- Test 11: Error on Unknown Placeholder ----

def test_build_instruction_sections_unknown_placeholder(monkeypatch):
    """A template with an unknown placeholder raises ValueError."""
    bad_template = [("Test", ["This has an {unknown_placeholder}."])]
    monkeypatch.setattr(config, "INSTRUCTION_SECTIONS_TEMPLATES", bad_template)

    with pytest.raises(ValueError):
        screens.build_instruction_sections()


# ---- Test 12: Screen Flow Sequence ----

def test_screen_flow_sequence():
    """The full screen flow with create_app_state and change_screen works as expected."""
    app = screens.create_app_state()
    assert app["screen"] == SCREEN_MENU

    screens.change_screen(app, SCREEN_GAME)
    assert app["screen"] == SCREEN_GAME

    screens.change_screen(app, SCREEN_MENU)
    assert app["screen"] == SCREEN_MENU

    screens.change_screen(app, SCREEN_INSTRUCTIONS)
    assert app["screen"] == SCREEN_INSTRUCTIONS

    screens.change_screen(app, SCREEN_MENU)
    assert app["screen"] == SCREEN_MENU


# ---- Test 13: Deterministic Restart from Menu ----

def test_game_restart_deterministic_clean_state():
    """
    Menu to game to summary to menu to game gives the exact same Level 1 layout
    and a fresh campaign with empty recorded results.
    """
    # First launch
    camp1 = campaign.create_campaign(start_level=1)
    grid1, ents1, base1, bud1 = campaign.prepare_level(1)

    # Simulate campaign run and final summary
    campaign.record_level_result(camp1, {
        "passed": True,
        "saved_people": 20, "total_population": 20, "sandbags_used": 24,
        "sandbags_allocated": 29, "population_score": 100, "efficiency_bonus": 25,
        "final_score": 125
    })
    assert len(camp1["level_results"]) == 1

    # Second launch (after returning to menu)
    camp2 = campaign.create_campaign(start_level=1)
    grid2, ents2, base2, bud2 = campaign.prepare_level(1)

    # Verify identical layout and budget
    assert grid1 == grid2
    assert ents1 == ents2
    assert base1 == base2
    assert bud1 == bud2

    # Verify clean results in new campaign
    assert len(camp2["level_results"]) == 0
    assert camp2["level"] == 1

