import pygame
from config import (
    TOP_PANEL_HEIGHT, BOTTOM_PANEL_HEIGHT, GRID_ORIGIN_X, GRID_ORIGIN_Y,
    CELL_SIZE, ROWS, COLS, COLOR_PANEL, COLOR_GRID_LINE, COLOR_TEXT,
    COLOR_HOVER, COLOR_SELECTED, CELL_COLORS, CELL_LABELS,
    LABEL_FONT_SIZE, COLOR_LABEL_TEXT
)

def draw_panels(screen, hover_info, selected_info, pop_info, build_info):
    """
    Draws the top and bottom information panels.
    """
    # Top Panel
    pygame.draw.rect(screen, COLOR_PANEL, (0, 0, 1200, TOP_PANEL_HEIGHT))

    # Top Panel Text
    font = pygame.font.Font(None, 36)
    title_surf = font.render("FLOOD RESCUE", True, COLOR_TEXT)
    screen.blit(title_surf, (20, 20))

    # Population and Buildings info
    stats_text = f"People: {pop_info}  Buildings: {build_info}"
    stats_surf = font.render(stats_text, True, COLOR_TEXT)
    screen.blit(stats_surf, (20, 40))

    # Hover and Selected readout
    info_text = f"Hover: {hover_info}  Selected: {selected_info}"
    info_surf = font.render(info_text, True, COLOR_TEXT)
    screen.blit(info_surf, (20, 60))

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
                # Center the text in the cell
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
    # Define items to show: type name and label
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
        # Draw color square
        color = CELL_COLORS[type_key]
        pygame.draw.rect(screen, color, (start_x + (i * 150), start_y, 20, 20))
        # Draw label
        text_surf = font.render(name, True, COLOR_TEXT)
        screen.blit(text_surf, (start_x + (i * 150) + 30, start_y - 5))
