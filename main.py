import pygame
from config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS, ROWS, COLS,
    COLOR_BG, COLOR_HOVER, COLOR_SELECTED
)
import grid
import interface

def main():
    # Initialize Pygame
    pygame.init()

    # Set up the window
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Flood Rescue")

    # Game State
    game_grid = grid.create_grid(ROWS, COLS)
    selected_cell = None

    clock = pygame.time.Clock()
    running = True

    while running:
        # 1. Event Handling
        mouse_pos = pygame.mouse.get_pos()

        # Convert mouse position to grid cell
        hovered_cell = grid.pixel_to_cell(
            mouse_pos[0], mouse_pos[1],
            interface.GRID_ORIGIN_X, interface.GRID_ORIGIN_Y,
            interface.CELL_SIZE, ROWS, COLS
        )

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left click
                    if hovered_cell:
                        selected_cell = hovered_cell

        # 2. Rendering
        screen.fill(COLOR_BG)

        # Draw the core game elements
        interface.draw_grid(screen, game_grid)
        interface.draw_coordinates(screen)

        # Draw highlights
        if hovered_cell:
            interface.draw_highlight(screen, hovered_cell, COLOR_HOVER)
        if selected_cell:
            interface.draw_highlight(screen, selected_cell, COLOR_SELECTED)

        # Draw UI panels
        hover_text = f"({hovered_cell[0]}, {hovered_cell[1]})" if hovered_cell else "-"
        selected_text = f"({selected_cell[0]}, {selected_cell[1]})" if selected_cell else "-"
        interface.draw_panels(screen, hover_text, selected_text)

        # Update display
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
