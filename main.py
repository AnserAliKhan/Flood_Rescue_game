import pygame
from config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS, ROWS, COLS,
    COLOR_BG, COLOR_HOVER, COLOR_SELECTED, TEST_LAYOUT,
    TEST_SANDBAG_BUDGET, BTN_SANDBAG_RECT, BTN_RESET_RECT,
    BTN_SANDBAG_LABEL, BTN_RESET_LABEL, MESSAGE_TIMEOUT
)
import grid
import interface
import entities
import sandbags

def main():
    # Initialize Pygame
    pygame.init()

    # Set up the window
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Flood Rescue")

    # Game State
    game_grid = grid.create_grid(ROWS, COLS)
    entities_list = entities.build_layout(game_grid, TEST_LAYOUT)
    selected_cell = None

    # Sandbag Tool State
    tool_active = False
    message_text = ""
    message_start_time = 0

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

        # Check for button hovers
        sb_btn_hovered = pygame.Rect(BTN_SANDBAG_RECT).collidepoint(mouse_pos)
        reset_btn_hovered = pygame.Rect(BTN_RESET_RECT).collidepoint(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_s:
                    tool_active = not tool_active
                    message_text = ""
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left click
                    # Priority 1: Buttons
                    if sb_btn_hovered:
                        tool_active = not tool_active
                        message_text = ""
                    elif reset_btn_hovered:
                        sandbags.clear_sandbags(game_grid)
                        message_text = "Grid reset."
                        message_start_time = pygame.time.get_ticks()
                    # Priority 2: Grid
                    elif hovered_cell:
                        if tool_active:
                            try:
                                if game_grid[hovered_cell[0]][hovered_cell[1]] == "sandbag":
                                    sandbags.remove_sandbag(game_grid, hovered_cell[0], hovered_cell[1])
                                else:
                                    sandbags.place_sandbag(game_grid, hovered_cell[0], hovered_cell[1], TEST_SANDBAG_BUDGET)
                                message_text = ""
                            except ValueError as e:
                                message_text = str(e)
                                message_start_time = pygame.time.get_ticks()
                        else:
                            selected_cell = hovered_cell

                elif event.button == 3: # Right click
                    if hovered_cell:
                        try:
                            sandbags.remove_sandbag(game_grid, hovered_cell[0], hovered_cell[1])
                            message_text = ""
                        except ValueError:
                            pass # Right click on non-sandbag does nothing

        # 2. Logic: Determine info for top panel
        pop_total = entities.total_population(entities_list)
        build_counts = entities.count_buildings(entities_list)
        total_buildings = sum(build_counts.values())

        # Sandbag counter
        sb_remaining = sandbags.remaining_sandbags(game_grid, TEST_SANDBAG_BUDGET)
        sb_info = f"Sandbags: {sb_remaining} / {TEST_SANDBAG_BUDGET}"

        # Handle building hover details
        hover_text = "-"
        if hovered_cell:
            entity = entities.get_entity_at(entities_list, hovered_cell[0], hovered_cell[1])
            if entity:
                e_type = entity["type"].capitalize()
                e_id = entity["id"]
                e_pop = entity["population"]
                if e_type == "Shelter":
                    hover_text = f"Shelter  people: {e_pop}"
                else:
                    hover_text = f"{e_type} #{e_id}  people: {e_pop}"
            else:
                hover_text = f"({hovered_cell[0]}, {hovered_cell[1]})"

        selected_text = f"({selected_cell[0]}, {selected_cell[1]})" if selected_cell else "-"

        # Message timer
        if message_text and pygame.time.get_ticks() - message_start_time > MESSAGE_TIMEOUT:
            message_text = ""

        # 3. Rendering
        screen.fill(COLOR_BG)

        # Draw the core game elements
        interface.draw_grid(screen, game_grid)
        interface.draw_cell_labels(screen, game_grid)
        interface.draw_coordinates(screen)

        # Draw highlights
        if hovered_cell:
            interface.draw_highlight(screen, hovered_cell, COLOR_HOVER)
        if selected_cell:
            interface.draw_highlight(screen, selected_cell, COLOR_SELECTED)

        # Draw UI panels
        interface.draw_panels(screen, hover_text, selected_text, pop_total, total_buildings, sb_info)
        interface.draw_legend(screen)

        # Draw Buttons
        btn_font = pygame.font.Font(None, 30)
        interface.draw_button(screen, BTN_SANDBAG_RECT, BTN_SANDBAG_LABEL, btn_font, tool_active, sb_btn_hovered)
        interface.draw_button(screen, BTN_RESET_RECT, BTN_RESET_LABEL, btn_font, False, reset_btn_hovered)

        # Draw Message
        interface.draw_message(screen, message_text, btn_font)

        # Update display
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
