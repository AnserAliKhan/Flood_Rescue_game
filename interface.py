"""
interface.py - Pygame GUI Rendering and User Interface Components (F12)

Handles all graphical rendering: grid display, cell labels, panels, dialogs,
buttons, animations, and full-screen views (Menu, Instructions, Final Summary).

RULES:
- Zero game logic mutation: rendering functions only read state data.
- All fonts are pre-initialized once via init_fonts() to avoid per-frame allocations.
"""

import pygame
from config import (
    WINDOW_WIDTH, WINDOW_HEIGHT,
    TOP_PANEL_HEIGHT, BOTTOM_PANEL_HEIGHT, GRID_ORIGIN_X, GRID_ORIGIN_Y,
    CELL_SIZE, ROWS, COLS, COLOR_BG, COLOR_PANEL, COLOR_GRID_LINE, COLOR_TEXT,
    CELL_COLORS, CELL_LABELS, LABEL_FONT_SIZE, COLOR_LABEL_TEXT,
    COLOR_BTN_NORMAL, COLOR_BTN_HOVER, COLOR_BTN_ACTIVE, COLOR_BTN_TEXT,
    COLOR_MSG_TEXT, BTN_RETRY_RECT, BTN_CONTINUE_RECT,
    BTN_RETRY_LABEL, BTN_CONTINUE_LABEL,
    COLOR_SAFE, COLOR_UNSAFE, COLOR_DIALOG_BG, COLOR_DIMMER,
    DIALOG_RECT, DIALOG_YES_RECT, DIALOG_CANCEL_RECT,
    DIALOG_TITLE, DIALOG_YES_LABEL, DIALOG_CANCEL_LABEL,
    COLOR_WATER, COLOR_WATER_FRONT,
    MSG_FLOODING_BANNER, MSG_FLOODING_SKIP,
    NUM_LEVELS, LEVEL_NAMES, BTN_PLAY_AGAIN_LABEL,
    SUMMARY_TITLE, SUMMARY_SUBTITLE, SUMMARY_COL_HEADINGS,
    SUMMARY_TABLE_X, SUMMARY_TABLE_Y, SUMMARY_ROW_HEIGHT, SUMMARY_COL_WIDTHS,
    SUMMARY_PLAY_AGAIN_RECT, SUMMARY_MENU_RECT, BTN_MENU_LABEL,
    COLOR_SUMMARY_TITLE, COLOR_SUMMARY_SUBTITLE,
    COLOR_SUMMARY_LINE, COLOR_SUMMARY_HEADER, COLOR_TOTAL_SCORE,
    MENU_TITLE, MENU_TAGLINE, MENU_BUTTONS, MENU_CAPTIONS,
    INSTRUCTIONS_TITLE, INSTRUCTIONS_BACK_RECT, INSTRUCTIONS_BACK_LABEL,
    INSTRUCTIONS_COL1_X, INSTRUCTIONS_COL2_X, INSTRUCTIONS_START_Y,
    INSTRUCTIONS_LINE_HEIGHT, INSTRUCTIONS_SECTION_GAP,
    HEADER_TITLE, PANEL_TITLE_POS, PANEL_LEVEL_POS, PANEL_SCORE_POS, PANEL_PHASE_POS,
    LEGEND_BOX_SIZE, LEGEND_START_X, LEGEND_SPACING,
    MESSAGE_CENTER_POS,
    RESULTS_COL1_X, RESULTS_COL2_X,
    DIALOG_TITLE_POS, DIALOG_SUBTITLE_POS,
    MENU_TITLE_POS, MENU_TAGLINE_POS, INSTRUCTIONS_TITLE_POS,
    SUMMARY_TITLE_POS, SUMMARY_SUBTITLE_POS, SUMMARY_TOTAL_SCORE_POS,
    SUMMARY_PEOPLE_POS, SUMMARY_EFFICIENCY_POS, SUMMARY_COMMENTARY_POS,
    FONT_SIZE_TITLE_LARGE, FONT_SIZE_TITLE_MAIN, FONT_SIZE_SECTION, FONT_SIZE_LARGE,
    FONT_SIZE_BUTTON, FONT_SIZE_BUTTON_LARGE, FONT_SIZE_BODY, FONT_SIZE_HEADING,
    FONT_SIZE_SMALL, FONT_SIZE_INSTRUCTIONS, FONT_SIZE_COORD
)


# Module-level font cache
_CACHED_FONTS = None


def init_fonts():
    """
    Initializes and returns all fonts used across the interface in a dictionary.
    Call once at application startup after pygame.init().
    """
    global _CACHED_FONTS
    _CACHED_FONTS = {
        "title_large": pygame.font.Font(None, FONT_SIZE_TITLE_LARGE),
        "title_main": pygame.font.Font(None, FONT_SIZE_TITLE_MAIN),
        "section": pygame.font.Font(None, FONT_SIZE_SECTION),
        "large": pygame.font.Font(None, FONT_SIZE_LARGE),
        "button": pygame.font.Font(None, FONT_SIZE_BUTTON),
        "button_large": pygame.font.Font(None, FONT_SIZE_BUTTON_LARGE),
        "body": pygame.font.Font(None, FONT_SIZE_BODY),
        "heading": pygame.font.Font(None, FONT_SIZE_HEADING),
        "small": pygame.font.Font(None, FONT_SIZE_SMALL),
        "instructions": pygame.font.Font(None, FONT_SIZE_INSTRUCTIONS),
        "coord": pygame.font.Font(None, FONT_SIZE_COORD),
        "cell": pygame.font.Font(None, LABEL_FONT_SIZE),
    }
    return _CACHED_FONTS


def _get_font(key):
    """Internal helper to retrieve cached font or create fallback if cache is empty."""
    if _CACHED_FONTS is None:
        init_fonts()
    return _CACHED_FONTS.get(key)


def draw_panels(screen, hover_info, selected_info, pop_info, build_info, sandbag_info, phase_name, current_level=1, campaign_score=0, font=None):
    """
    Draws the top information panel with campaign progress, population, and sandbag stats.
    """
    pygame.draw.rect(screen, COLOR_PANEL, (0, 0, WINDOW_WIDTH, TOP_PANEL_HEIGHT))

    active_font = font if font is not None else _get_font("section")

    # Title, Level Progress, Running Score, and Phase
    title_surf = active_font.render(HEADER_TITLE, True, COLOR_TEXT)
    screen.blit(title_surf, PANEL_TITLE_POS)

    level_name = LEVEL_NAMES.get(current_level, "")
    level_surf = active_font.render(f"Level {current_level} / {NUM_LEVELS} - {level_name}", True, COLOR_TEXT)
    screen.blit(level_surf, PANEL_LEVEL_POS)

    score_surf = active_font.render(f"Score so far: {campaign_score}", True, COLOR_TEXT)
    screen.blit(score_surf, PANEL_SCORE_POS)

    phase_surf = active_font.render(f"Phase: {phase_name.capitalize()}", True, COLOR_TEXT)
    screen.blit(phase_surf, PANEL_PHASE_POS)

    # Population and Buildings info
    stats_text = f"People: {pop_info}  Buildings: {build_info}"
    stats_surf = active_font.render(stats_text, True, COLOR_TEXT)
    screen.blit(stats_surf, (20, 60))

    # Sandbag counter
    sb_surf = active_font.render(sandbag_info, True, COLOR_TEXT)
    screen.blit(sb_surf, (430, 60))

    # Hover and Selected readout
    info_text = f"Hover: {hover_info}  Selected: {selected_info}"
    info_surf = active_font.render(info_text, True, COLOR_TEXT)
    screen.blit(info_surf, (800, 60))

    # Bottom Panel background
    pygame.draw.rect(screen, COLOR_PANEL, (0, WINDOW_HEIGHT - BOTTOM_PANEL_HEIGHT, WINDOW_WIDTH, BOTTOM_PANEL_HEIGHT))


def draw_grid(screen, grid_data):
    """
    Renders all 300 cells of the 30 x 10 grid with cell background colors and gridlines.
    """
    for row in range(ROWS):
        for col in range(COLS):
            cell_type = grid_data[row][col]
            colour = CELL_COLORS.get(cell_type, (255, 0, 255))

            x = GRID_ORIGIN_X + (col * CELL_SIZE)
            y = GRID_ORIGIN_Y + (row * CELL_SIZE)

            pygame.draw.rect(screen, colour, (x, y, CELL_SIZE, CELL_SIZE))
            pygame.draw.rect(screen, COLOR_GRID_LINE, (x, y, CELL_SIZE, CELL_SIZE), 1)


def draw_cell_labels(screen, grid_data, font=None):
    """
    Renders identifying letters (H, S, +, SH, B) centered inside each non-empty cell.
    """
    active_font = font if font is not None else _get_font("cell")
    for row in range(ROWS):
        for col in range(COLS):
            cell_type = grid_data[row][col]
            label = CELL_LABELS.get(cell_type, "")
            if label:
                text_surf = active_font.render(label, True, COLOR_LABEL_TEXT)
                x = GRID_ORIGIN_X + (col * CELL_SIZE) + (CELL_SIZE // 2) - (text_surf.get_width() // 2)
                y = GRID_ORIGIN_Y + (row * CELL_SIZE) + (CELL_SIZE // 2) - (text_surf.get_height() // 2)
                screen.blit(text_surf, (x, y))


def draw_coordinates(screen, font=None):
    """
    Draws column (0..29) and row (0..9) coordinate numbers around the grid perimeter.
    """
    active_font = font if font is not None else _get_font("coord")
    for col in range(COLS):
        x = GRID_ORIGIN_X + (col * CELL_SIZE) + (CELL_SIZE // 2) - 5
        y = GRID_ORIGIN_Y - 20
        surf = active_font.render(str(col), True, COLOR_TEXT)
        screen.blit(surf, (x, y))
    for row in range(ROWS):
        x = GRID_ORIGIN_X - 20
        y = GRID_ORIGIN_Y + (row * CELL_SIZE) + (CELL_SIZE // 2) - 5
        surf = active_font.render(str(row), True, COLOR_TEXT)
        screen.blit(surf, (x, y))


def draw_highlight(screen, cell, color):
    """
    Draws a border highlight around a specified (row, col) grid cell.
    """
    if cell is None:
        return
    row, col = cell
    x = GRID_ORIGIN_X + (col * CELL_SIZE)
    y = GRID_ORIGIN_Y + (row * CELL_SIZE)
    pygame.draw.rect(screen, color, (x, y, CELL_SIZE, CELL_SIZE), 3)


def draw_legend(screen, font=None):
    """
    Draws the colored entity legend in the bottom control panel.
    """
    legend_items = [
        ("House", "house"),
        ("School", "school"),
        ("Hospital", "hospital"),
        ("Shelter", "shelter")
    ]
    active_font = font if font is not None else _get_font("button")
    start_x = LEGEND_START_X
    start_y = WINDOW_HEIGHT - BOTTOM_PANEL_HEIGHT + 25

    for i, (name, type_key) in enumerate(legend_items):
        color = CELL_COLORS[type_key]
        item_x = start_x + (i * LEGEND_SPACING)
        pygame.draw.rect(screen, color, (item_x, start_y, LEGEND_BOX_SIZE, LEGEND_BOX_SIZE))
        pygame.draw.rect(screen, COLOR_GRID_LINE, (item_x, start_y, LEGEND_BOX_SIZE, LEGEND_BOX_SIZE), 1)
        text_surf = active_font.render(name, True, COLOR_TEXT)
        screen.blit(text_surf, (item_x + LEGEND_BOX_SIZE + 8, start_y - 2))


def draw_button(screen, rect, text, font, active=False, hovered=False):
    """
    Renders an interactive button with normal, active, or hovered styling.
    """
    color = COLOR_BTN_NORMAL
    if active:
        color = COLOR_BTN_ACTIVE
    elif hovered:
        color = COLOR_BTN_HOVER

    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, COLOR_GRID_LINE, rect, 2)

    text_surf = font.render(text, True, COLOR_BTN_TEXT)
    text_rect = text_surf.get_rect(center=(rect[0] + rect[2] // 2, rect[1] + rect[3] // 2))
    screen.blit(text_surf, text_rect)


def draw_message(screen, text, font):
    """
    Draws a transient player feedback message centered in the bottom panel.
    """
    if not text:
        return
    text_surf = font.render(text, True, COLOR_MSG_TEXT)
    text_rect = text_surf.get_rect(center=(MESSAGE_CENTER_POS[0], WINDOW_HEIGHT - BOTTOM_PANEL_HEIGHT // 2))
    screen.blit(text_surf, text_rect)


def draw_safe_unsafe(screen, entities):
    """
    Results phase: outlines connected buildings in green (safe) and disconnected in red (unsafe).
    """
    for e in entities:
        if e["type"] == "shelter":
            continue

        row, col = e["row"], e["col"]
        x = GRID_ORIGIN_X + (col * CELL_SIZE)
        y = GRID_ORIGIN_Y + (row * CELL_SIZE)

        color = COLOR_SAFE if e["connected"] else COLOR_UNSAFE
        pygame.draw.rect(screen, color, (x, y, CELL_SIZE, CELL_SIZE), 4)


def draw_confirm_dialog(screen, remaining, font):
    """
    Renders the modal confirmation dialog with dark semi-transparent backdrop.
    """
    # 1. Dimmer overlay
    overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
    overlay.fill(COLOR_DIMMER)
    screen.blit(overlay, (0, 0))

    # 2. Dialog box
    pygame.draw.rect(screen, COLOR_DIALOG_BG, DIALOG_RECT)
    pygame.draw.rect(screen, COLOR_GRID_LINE, DIALOG_RECT, 2)

    # 3. Title
    title_surf = font.render(DIALOG_TITLE, True, COLOR_TEXT)
    title_rect = title_surf.get_rect(center=DIALOG_TITLE_POS)
    screen.blit(title_surf, title_rect)

    # 4. Sandbags left text
    info_text = f"Sandbags left: {remaining}"
    info_surf = font.render(info_text, True, COLOR_TEXT)
    info_rect = info_surf.get_rect(center=DIALOG_SUBTITLE_POS)
    screen.blit(info_surf, info_rect)

    # 5. Buttons
    draw_button(screen, DIALOG_YES_RECT, DIALOG_YES_LABEL, font, False, False)
    draw_button(screen, DIALOG_CANCEL_RECT, DIALOG_CANCEL_LABEL, font, False, False)


def draw_results_panel(screen, breakdown, can_continue, font, current_level=1, continue_label=BTN_CONTINUE_LABEL):
    """
    Draws a detailed score and evacuation breakdown in the bottom panel during Results phase.
    """
    pygame.draw.rect(screen, COLOR_PANEL, (0, WINDOW_HEIGHT - BOTTOM_PANEL_HEIGHT, WINDOW_WIDTH, BOTTOM_PANEL_HEIGHT))

    start_x = RESULTS_COL1_X
    start_y = WINDOW_HEIGHT - BOTTOM_PANEL_HEIGHT + 15

    lines = [
        (f"Level {current_level}: {'PASSED' if breakdown['passed'] else 'FAILED'}", f"Total Population: {breakdown['total_population']}"),
        (f"People Saved: {breakdown['saved_people']}", f"Unsaved: {breakdown['unsaved_people']}"),
        (f"Connected: H:{breakdown['houses_connected']} S:{breakdown['schools_connected']} +:{breakdown['hospitals_connected']}", f"Sandbags: {breakdown['sandbags_used']} used / {breakdown['sandbags_allocated']} total ({breakdown['sandbags_remaining']} left)"),
        (f"Pop Score: {breakdown['population_score']}", f"Bonus: {breakdown['efficiency_bonus']}  |  FINAL SCORE: {breakdown['final_score']}")
    ]

    y_offset = 0
    for left, right in lines:
        l_surf = font.render(left, True, COLOR_TEXT)
        screen.blit(l_surf, (start_x, start_y + y_offset))
        if right:
            r_surf = font.render(right, True, COLOR_TEXT)
            screen.blit(r_surf, (RESULTS_COL2_X, start_y + y_offset))
        y_offset += 24

    # Buttons
    draw_button(screen, BTN_RETRY_RECT, BTN_RETRY_LABEL, font, False, False)
    if can_continue:
        draw_button(screen, BTN_CONTINUE_RECT, continue_label, font, False, False)


def draw_flood(screen, flooded_cells, front_col):
    """
    Renders semi-transparent water overlay on all flooded cells.
    Uses a reusable cell-sized surface for 60 FPS performance.
    """
    water_cell = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)

    for row, col in flooded_cells:
        if col == front_col:
            water_cell.fill(COLOR_WATER_FRONT)
        else:
            water_cell.fill(COLOR_WATER)

        x = GRID_ORIGIN_X + (col * CELL_SIZE)
        y = GRID_ORIGIN_Y + (row * CELL_SIZE)
        screen.blit(water_cell, (x, y))


def draw_flooded_buildings(screen, entities, flooded_cells):
    """
    Highlights non-shelter buildings with red outlines if reached by floodwaters.
    """
    for e in entities:
        if e["type"] == "shelter":
            continue

        pos = (e["row"], e["col"])
        if pos in flooded_cells:
            x = GRID_ORIGIN_X + (pos[1] * CELL_SIZE)
            y = GRID_ORIGIN_Y + (pos[0] * CELL_SIZE)
            pygame.draw.rect(screen, COLOR_UNSAFE, (x, y, CELL_SIZE, CELL_SIZE), 4)


def draw_flood_banner(screen, font, skip_font=None):
    """
    Draws the flooding banner and skip instructions in the bottom panel.
    """
    pygame.draw.rect(screen, COLOR_PANEL, (0, WINDOW_HEIGHT - BOTTOM_PANEL_HEIGHT, WINDOW_WIDTH, BOTTOM_PANEL_HEIGHT))

    banner_surf = font.render(MSG_FLOODING_BANNER, True, COLOR_TEXT)
    banner_rect = banner_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - BOTTOM_PANEL_HEIGHT + 45))
    screen.blit(banner_surf, banner_rect)

    active_skip_font = skip_font if skip_font is not None else _get_font("small")
    skip_surf = active_skip_font.render(MSG_FLOODING_SKIP, True, COLOR_MSG_TEXT)
    skip_rect = skip_surf.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - BOTTOM_PANEL_HEIGHT + 85))
    screen.blit(skip_surf, skip_rect)


def draw_final_summary(screen, summary, font_title, font_table, font_large, play_again_hovered=False, menu_hovered=False):
    """
    Renders the full-screen end-game summary screen with tabular breakdown and dual buttons.
    """
    screen.fill(COLOR_BG)

    title_surf = font_title.render(SUMMARY_TITLE, True, COLOR_SUMMARY_TITLE)
    title_rect = title_surf.get_rect(center=SUMMARY_TITLE_POS)
    screen.blit(title_surf, title_rect)

    subtitle_surf = font_table.render(SUMMARY_SUBTITLE, True, COLOR_SUMMARY_SUBTITLE)
    subtitle_rect = subtitle_surf.get_rect(center=SUMMARY_SUBTITLE_POS)
    screen.blit(subtitle_surf, subtitle_rect)

    table_width = sum(SUMMARY_COL_WIDTHS)
    pygame.draw.line(screen, COLOR_SUMMARY_LINE, (SUMMARY_TABLE_X, 145), (SUMMARY_TABLE_X + table_width, 145), 2)

    curr_x = SUMMARY_TABLE_X
    for i, heading in enumerate(SUMMARY_COL_HEADINGS):
        col_w = SUMMARY_COL_WIDTHS[i]
        h_surf = font_table.render(heading, True, COLOR_SUMMARY_HEADER)
        h_rect = h_surf.get_rect(center=(curr_x + col_w // 2, SUMMARY_TABLE_Y + 15))
        screen.blit(h_surf, h_rect)
        curr_x += col_w

    pygame.draw.line(screen, COLOR_SUMMARY_LINE, (SUMMARY_TABLE_X, SUMMARY_TABLE_Y + 35), (SUMMARY_TABLE_X + table_width, SUMMARY_TABLE_Y + 35), 1)

    for row_idx, r in enumerate(summary["rows"]):
        row_y = 205 + row_idx * SUMMARY_ROW_HEIGHT
        curr_x = SUMMARY_TABLE_X

        level_name = LEVEL_NAMES.get(r["level"], "")
        row_texts = [
            f"Lvl {r['level']} - {level_name}",
            f"{r['saved_people']} / {r['total_population']}",
            f"{r['sandbags_used']} / {r['sandbags_allocated']}",
            f"{r['population_score']}",
            f"{r['efficiency_bonus']}",
            f"{r['final_score']}"
        ]

        for col_idx, cell_text in enumerate(row_texts):
            col_w = SUMMARY_COL_WIDTHS[col_idx]
            cell_surf = font_table.render(cell_text, True, COLOR_TEXT)
            cell_rect = cell_surf.get_rect(center=(curr_x + col_w // 2, row_y + 15))
            screen.blit(cell_surf, cell_rect)
            curr_x += col_w

    pygame.draw.line(screen, COLOR_SUMMARY_LINE, (SUMMARY_TABLE_X, 342), (SUMMARY_TABLE_X + table_width, 342), 2)

    total_surf = font_large.render(f"TOTAL SCORE: {summary['total_score']}", True, COLOR_TOTAL_SCORE)
    total_rect = total_surf.get_rect(center=SUMMARY_TOTAL_SCORE_POS)
    screen.blit(total_surf, total_rect)

    people_font = _get_font("button_large")
    people_surf = people_font.render(f"People Saved: {summary['total_people_saved']} / {summary['total_population']}", True, COLOR_TEXT)
    people_rect = people_surf.get_rect(center=SUMMARY_PEOPLE_POS)
    screen.blit(people_surf, people_rect)

    eff_font = _get_font("body")
    eff_surf = eff_font.render(
        f"Sandbags Conserved: {summary['sandbags_remaining']} / {summary['sandbags_allocated']}  ({summary['efficiency_percent']}% efficiency)",
        True, COLOR_SUMMARY_SUBTITLE
    )
    eff_rect = eff_surf.get_rect(center=SUMMARY_EFFICIENCY_POS)
    screen.blit(eff_surf, eff_rect)

    note_font = _get_font("small")
    if summary["efficiency_percent"] >= 20.0:
        eff_note = "Outstanding performance! Maximum efficiency demonstrated."
    elif summary["efficiency_percent"] > 0.0:
        eff_note = "Great job! Sandbag network connected all civilians safely."
    else:
        eff_note = "Evacuation succeeded, though all available sandbags were used."

    note_surf = note_font.render(eff_note, True, COLOR_TEXT)
    note_rect = note_surf.get_rect(center=SUMMARY_COMMENTARY_POS)
    screen.blit(note_surf, note_rect)

    btn_font = _get_font("button_large")
    draw_button(screen, SUMMARY_PLAY_AGAIN_RECT, BTN_PLAY_AGAIN_LABEL, btn_font, False, play_again_hovered)
    draw_button(screen, SUMMARY_MENU_RECT, BTN_MENU_LABEL, btn_font, False, menu_hovered)


def draw_menu(screen, hovered_btn_name, font_title, font_tagline, font_btn):
    """
    Renders the full-screen Main Menu with Title, Tagline, and 3 Navigation Buttons.
    """
    screen.fill(COLOR_BG)

    title_surf = font_title.render(MENU_TITLE, True, COLOR_SUMMARY_TITLE)
    title_rect = title_surf.get_rect(center=MENU_TITLE_POS)
    screen.blit(title_surf, title_rect)

    tagline_surf = font_tagline.render(MENU_TAGLINE, True, COLOR_SUMMARY_SUBTITLE)
    tagline_rect = tagline_surf.get_rect(center=MENU_TAGLINE_POS)
    screen.blit(tagline_surf, tagline_rect)

    for btn_name, rect in MENU_BUTTONS.items():
        label = MENU_CAPTIONS.get(btn_name, "")
        is_hovered = (btn_name == hovered_btn_name)
        draw_button(screen, rect, label, font_btn, False, is_hovered)


def draw_instructions(screen, sections, back_hovered, font_title, font_heading, font_body, font_btn):
    """
    Renders the full-screen Instructions screen arranged into two columns with a Back button.
    """
    screen.fill(COLOR_BG)

    title_surf = font_title.render(INSTRUCTIONS_TITLE, True, COLOR_SUMMARY_TITLE)
    title_rect = title_surf.get_rect(center=INSTRUCTIONS_TITLE_POS)
    screen.blit(title_surf, title_rect)

    col1_sections = sections[:3]
    col2_sections = sections[3:]

    for col_idx, col_sects in enumerate([col1_sections, col2_sections]):
        col_x = INSTRUCTIONS_COL1_X if col_idx == 0 else INSTRUCTIONS_COL2_X
        curr_y = INSTRUCTIONS_START_Y

        for title, lines in col_sects:
            h_surf = font_heading.render(title, True, COLOR_SUMMARY_HEADER)
            screen.blit(h_surf, (col_x, curr_y))
            curr_y += 26

            for line in lines:
                line_surf = font_body.render(line, True, COLOR_TEXT)
                screen.blit(line_surf, (col_x, curr_y))
                curr_y += INSTRUCTIONS_LINE_HEIGHT

            curr_y += INSTRUCTIONS_SECTION_GAP

    draw_button(screen, INSTRUCTIONS_BACK_RECT, INSTRUCTIONS_BACK_LABEL, font_btn, False, back_hovered)
