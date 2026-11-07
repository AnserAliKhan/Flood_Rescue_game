import pygame
from config import (
    TOP_PANEL_HEIGHT, BOTTOM_PANEL_HEIGHT, GRID_ORIGIN_X, GRID_ORIGIN_Y,
    CELL_SIZE, ROWS, COLS, COLOR_PANEL, COLOR_GRID_LINE, COLOR_TEXT,
    COLOR_HOVER, COLOR_SELECTED, CELL_COLORS, CELL_LABELS,
    LABEL_FONT_SIZE, COLOR_LABEL_TEXT,
    COLOR_BTN_NORMAL, COLOR_BTN_HOVER, COLOR_BTN_ACTIVE, COLOR_BTN_TEXT,
    COLOR_MSG_TEXT, BTN_SANDBAG_RECT, BTN_RESET_RECT, BTN_CONFIRM_RECT,
    BTN_RETRY_RECT, BTN_CONTINUE_RECT,
    BTN_SANDBAG_LABEL, BTN_RESET_LABEL, BTN_CONFIRM_LABEL,
    BTN_RETRY_LABEL, BTN_CONTINUE_LABEL,
    COLOR_SAFE, COLOR_UNSAFE, COLOR_DIALOG_BG, COLOR_DIMMER,
    DIALOG_RECT, DIALOG_YES_RECT, DIALOG_CANCEL_RECT,
    DIALOG_TITLE
)

def draw_panels(screen, hover_info, selected_info, pop_info, build_info, sandbag_info, phase_name):
    """
    Draws the top and bottom information panels.
    """
    # Top Panel
    pygame.draw.rect(screen, COLOR_PANEL, (0, 0, 1200, TOP_PANEL_HEIGHT))

    font = pygame.font.Font(None, 36)

    # Title and Phase
    title_surf = font.render("FLOOD RESCUE", True, COLOR_TEXT)
    screen.blit(title_surf, (20, 20))

    # Level and Phase display
    # Note: CURRENT_LEVEL is imported from config in main.py, but we can pass it or use a fixed string here
    phase_surf = font.render(f"Phase: {phase_name.capitalize()}", True, COLOR_TEXT)
    screen.blit(phase_surf, (1000, 20))

    # Population and Buildings info
    stats_text = f"People: {pop_info}  Buildings: {build_info}"
    stats_surf = font.render(stats_text, True, COLOR_TEXT)
    screen.blit(stats_surf, (20, 40))

    # Sandbag counter
    sb_surf = font.render(sandbag_info, True, COLOR_TEXT)
    screen.blit(sb_surf, (20, 60))

    # Hover and Selected readout
    info_text = f"Hover: {hover_info}  Selected: {selected_info}"
    info_surf = font.render(info_text, True, COLOR_TEXT)
    screen.blit(info_surf, (20, 80))

    # Bottom Panel
    pygame.draw.rect(screen, COLOR_PANEL, (0, 1200 - BOTTOM_PANEL_HEIGHT, 1200, BOTTOM_PANEL_HEIGHT))

def draw_grid(screen, grid):
    """
    Draws the 2D grid based on its data.
    """
    for row in range(ROWS):
        for col in range(COLS):
            cell_type = grid[row][col]
            colour = CELL_COLORS.get(cell_type, (255, 0, 255))

            x = GRID_ORIGIN_X + (col * CELL_SIZE)
            y = GRID_ORIGIN_Y + (row * CELL_SIZE)

            pygame.draw.rect(screen, colour, (x, y, CELL_SIZE, CELL_SIZE))
            pygame.draw.rect(screen, COLOR_GRID_LINE, (x, y, CELL_SIZE, CELL_SIZE), 1)

def draw_cell_labels(screen, grid):
    """
    Draws labels inside building cells.
    """
    font = pygame.font.Font(None, LABEL_FONT_SIZE)
    for row in range(ROWS):
        for col in range(COLS):
            cell_type = grid[row][col]
            label = CELL_LABELS.get(cell_type, "")
            if label:
                text_surf = font.render(label, True, COLOR_LABEL_TEXT)
                x = GRID_ORIGIN_X + (col * CELL_SIZE) + (CELL_SIZE // 2) - (text_surf.get_width() // 2)
                y = GRID_ORIGIN_Y + (row * CELL_SIZE) + (CELL_SIZE // 2) - (text_surf.get_height() // 2)
                screen.blit(text_surf, (x, y))

def draw_coordinates(screen):
    """
    Draws column and row numbers around the grid.
    """
    font = pygame.font.Font(None, 20)
    for col in range(COLS):
        x = GRID_ORIGIN_X + (col * CELL_SIZE) + (CELL_SIZE // 2) - 5
        y = GRID_ORIGIN_Y - 20
        surf = font.render(str(col), True, COLOR_TEXT)
        screen.blit(surf, (x, y))
    for row in range(ROWS):
        x = GRID_ORIGIN_X - 20
        y = GRID_ORIGIN_Y + (row * CELL_SIZE) + (CELL_SIZE // 2) - 5
        surf = font.render(str(row), True, COLOR_TEXT)
        screen.blit(surf, (x, y))

def draw_highlight(screen, cell, color):
    """
    Draws a highlight border around a specific (row, col) cell.
    """
    if cell is None:
        return
    row, col = cell
    x = GRID_ORIGIN_X + (col * CELL_SIZE)
    y = GRID_ORIGIN_Y + (row * CELL_SIZE)
    pygame.draw.rect(screen, color, (x, y, CELL_SIZE, CELL_SIZE), 3)

def draw_legend(screen):
    """
    Draws a color legend in the bottom panel.
    """
    legend_items = [
        ("House", "house"),
        ("School", "school"),
        ("Hospital", "hospital"),
        ("Shelter", "shelter")
    ]
    font = pygame.font.Font(None, 30)
    start_x = 50
    start_y = 1200 - BOTTOM_PANEL_HEIGHT + 30
    for i, (name, type_key) in enumerate(legend_items):
        color = CELL_COLORS[type_key]
        pygame.draw.rect(screen, color, (start_x + (i * 150), start_y, 20, 20))
        text_surf = font.render(name, True, COLOR_TEXT)
        screen.blit(text_surf, (start_x + (i * 150) + 30, start_y - 5))

def draw_button(screen, rect, text, font, active, hovered):
    """
    Draws a button with state-based coloring.
    """
    color = COLOR_BTN_NORMAL
    if active:
        color = COLOR_BTN_ACTIVE
    elif hovered:
        color = COLOR_BTN_HOVER

    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, COLOR_GRID_LINE, rect, 2)

    text_surf = font.render(text, True, COLOR_BTN_TEXT)
    text_rect = text_surf.get_rect(center=(rect[0] + rect[2]//2, rect[1] + rect[3]//2))
    screen.blit(text_surf, text_rect)

def draw_message(screen, text, font):
    """
    Draws a feedback message in the bottom panel.
    """
    if not text:
        return
    text_surf = font.render(text, True, COLOR_MSG_TEXT)
    text_rect = text_surf.get_rect(center=(600, 1200 - BOTTOM_PANEL_HEIGHT // 2))
    screen.blit(text_surf, text_rect)

def draw_safe_unsafe(screen, entities):
    """
    Results phase: outlines buildings green if connected, red if not.
    """
    font = pygame.font.Font(None, 24)
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
    Draws a dimmed overlay and a centered confirmation box.
    """
    # 1. Dimmer overlay
    overlay = pygame.Surface((1200, 750), pygame.SRCALPHA)
    overlay.fill(COLOR_DIMMER)
    screen.blit(overlay, (0, 0))

    # 2. Dialog box
    pygame.draw.rect(screen, COLOR_DIALOG_BG, DIALOG_RECT)
    pygame.draw.rect(screen, COLOR_GRID_LINE, DIALOG_RECT, 2)

    # Title
    title_surf = font.render(DIALOG_TITLE, True, COLOR_TEXT)
    title_rect = title_surf.get_rect(center=(600, 250 + 50))
    screen.blit(title_surf, title_rect)

    # Sandbags left text
    info_text = f"Sandbags left: {remaining}"
    info_surf = font.render(info_text, True, COLOR_TEXT)
    info_rect = info_surf.get_rect(center=(600, 250 + 100))
    screen.blit(info_surf, info_rect)

    # Buttons
    # YES
    pygame.draw.rect(screen, COLOR_BTN_NORMAL, DIALOG_YES_RECT)
    yes_surf = font.render(DIALOG_YES_LABEL, True, COLOR_BTN_TEXT)
    yes_rect = yes_surf.get_rect(center=(DIALOG_YES_RECT[0] + 60, DIALOG_YES_RECT[1] + 25))
    screen.blit(yes_surf, yes_rect)

    # CANCEL
    pygame.draw.rect(screen, COLOR_BTN_NORMAL, DIALOG_CANCEL_RECT)
    cancel_surf = font.render(DIALOG_CANCEL_LABEL, True, COLOR_BTN_TEXT)
    cancel_rect = cancel_surf.get_rect(center=(DIALOG_CANCEL_RECT[0] + 60, DIALOG_CANCEL_RECT[1] + 25))
    screen.blit(cancel_surf, cancel_rect)

def draw_results_panel(screen, breakdown, can_continue, font):
    """
    Draws a detailed breakdown in the bottom panel.
    """
    # Bottom Panel BG
    pygame.draw.rect(screen, COLOR_PANEL, (0, 1200 - BOTTOM_PANEL_HEIGHT, 1200, BOTTOM_PANEL_HEIGHT))

    # Data layout (columns)
    col_width = 200
    start_x = 50
    start_y = 1200 - BOTTOM_PANEL_HEIGHT + 30

    # Row 1: Basic Stats
    lines = [
        (f"Level: {config.CURRENT_LEVEL}", f"Pop: {breakdown['total_population']}"),
        (f"Saved: {breakdown['saved_people']}", f"Unsaved: {breakdown['unsaved_people']}"),
        (f"H: {breakdown['houses_connected']} S: {breakdown['schools_connected']} Hosp: {breakdown['hospitals_connected']}", ""),
        (f"Budget: {breakdown['sandbags_allocated']} Used: {breakdown['sandbags_used']} Rem: {breakdown['sandbags_remaining']}", ""),
        (f"Pop Score: {breakdown['population_score']} Bonus: {breakdown['efficiency_bonus']}", f"FINAL: {breakdown['final_score']}"),
    ]

    for i, (left, right) in enumerate(lines):
        # Left side
        l_surf = font.render(left, True, COLOR_TEXT)
        screen.blit(l_surf, (start_x + (i % 2)*200 if i < 2 else start_x, start_y + (i // 2)*30)) # a bit simplified
        # This rendering is tricky, let's just use a simpler list

    # Re-doing the lines for clarity
    y_offset = 0
    for i, (left, right) in enumerate(lines):
        l_surf = font.render(left, True, COLOR_TEXT)
        screen.blit(l_surf, (start_x, start_y + y_offset))
        if right:
            r_surf = font.render(right, True, COLOR_TEXT)
            screen.blit(r_surf, (start_x + 300, start_y + y_offset))
        y_offset += 25

    # Bonus explanation if failed
    if not breakdown["passed"]:
        # We call the game.bonus_explanation in main, so we just draw it here
        # Actually, let's pass it as an argument to be pure
        pass

    # Buttons
    # RETRY
    pygame.draw.rect(screen, COLOR_BTN_NORMAL, BTN_RETRY_RECT)
    retry_surf = font.render(BTN_RETRY_LABEL, True, COLOR_BTN_TEXT)
    retry_rect = retry_surf.get_rect(center=(BTN_RETRY_RECT[0] + 100, BTN_RETRY_RECT[1] + 25))
    screen.blit(retry_surf, retry_rect)

    # CONTINUE
    if can_continue:
        pygame.draw.rect(screen, COLOR_BTN_NORMAL, BTN_CONTINUE_RECT)
        cont_surf = font.render(BTN_CONTINUE_LABEL, True, COLOR_BTN_TEXT)
        cont_rect = cont_surf.get_rect(center=(BTN_CONTINUE_RECT[0] + 100, BTN_CONTINUE_RECT[1] + 25))
        screen.blit(cont_surf, cont_rect)
