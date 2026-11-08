import pygame
from config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS, ROWS, COLS,
    COLOR_BG, COLOR_HOVER, COLOR_SELECTED,
    BTN_SANDBAG_RECT, BTN_RESET_RECT,
    BTN_CONFIRM_RECT, BTN_RETRY_RECT, BTN_CONTINUE_RECT,
    BTN_SANDBAG_LABEL, BTN_RESET_LABEL, BTN_CONFIRM_LABEL,
    BTN_RETRY_LABEL, BTN_CONTINUE_LABEL, BTN_SUMMARY_LABEL,
    BTN_PLAY_AGAIN_LABEL, BTN_PLAY_AGAIN_RECT,
    DIALOG_RECT, DIALOG_YES_RECT, DIALOG_CANCEL_RECT,
    MESSAGE_TIMEOUT, NUM_LEVELS, LEVEL_NAMES, DEBUG_LEVEL_KEYS,
    FLOOD_STEP_MS, FLOOD_END_HOLD_MS,
    PHASE_PLANNING, PHASE_CONFIRMING, PHASE_FLOODING, PHASE_RESULTS, PHASE_SUMMARY
)
import grid
import interface
import entities
import sandbags
import game
import flood
import campaign


def load_level(level_num):
    """
    Prepares a fresh level: builds grid and entities, computes baseline and budget,
    and initializes a fresh game state.
    """
    grid_data, entities_data, baseline_val, budget = campaign.prepare_level(level_num)
    new_state = game.create_game_state()
    # Temporary terminal debug output per F09/F10 spec
    print(f"Level {level_num}: baseline {baseline_val}, budget {budget}")
    return grid_data, entities_data, budget, new_state


def main():
    # Initialize Pygame
    pygame.init()

    # Set up the window
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Flood Rescue")

    # Campaign state (F10)
    camp = campaign.create_campaign(start_level=1)

    # Game State: Load the initial level
    game_grid, entities_list, total_budget, state = load_level(camp["level"])
    selected_cell = None

    # Flood Animation State (lives in main.py, NOT in game state)
    flood_start_ms = 0
    flood_steps = []

    # Tool and Message State
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
        confirm_btn_hovered = pygame.Rect(BTN_CONFIRM_RECT).collidepoint(mouse_pos)
        retry_btn_hovered = pygame.Rect(BTN_RETRY_RECT).collidepoint(mouse_pos)
        cont_btn_hovered = pygame.Rect(BTN_CONTINUE_RECT).collidepoint(mouse_pos)
        yes_btn_hovered = pygame.Rect(DIALOG_YES_RECT).collidepoint(mouse_pos)
        cancel_btn_hovered = pygame.Rect(DIALOG_CANCEL_RECT).collidepoint(mouse_pos)
        play_again_btn_hovered = pygame.Rect(BTN_PLAY_AGAIN_RECT).collidepoint(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if state["phase"] == PHASE_CONFIRMING:
                        game.cancel_confirmation(state)
                        message_text = ""
                    else:
                        running = False
                elif event.key == pygame.K_SPACE:
                    # F07: SPACE during flooding skips directly to results
                    if state["phase"] == PHASE_FLOODING:
                        try:
                            game.finish_flood(state)
                        except ValueError as e:
                            message_text = str(e)
                            message_start_time = pygame.time.get_ticks()
                elif event.key == pygame.K_s:
                    if game.is_editing_allowed(state):
                        tool_active = not tool_active
                        message_text = ""
                elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                    # Debug keys (active only when DEBUG_LEVEL_KEYS is True and in planning phase)
                    if DEBUG_LEVEL_KEYS and state["phase"] == PHASE_PLANNING:
                        level_map = {pygame.K_1: 1, pygame.K_2: 2, pygame.K_3: 3}
                        target_lvl = level_map[event.key]
                        camp = campaign.create_campaign(start_level=target_lvl)
                        game_grid, entities_list, total_budget, state = load_level(camp["level"])
                        selected_cell = None
                        tool_active = False
                        flood_start_ms = 0
                        flood_steps = []
                        message_text = f"Loaded Level {camp['level']} - {LEVEL_NAMES.get(camp['level'], '')}"
                        message_start_time = pygame.time.get_ticks()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left click
                    # ROUTING BY PHASE
                    if state["phase"] == PHASE_PLANNING:
                        if sb_btn_hovered:
                            tool_active = not tool_active
                            message_text = ""
                        elif reset_btn_hovered:
                            sandbags.clear_sandbags(game_grid)
                            message_text = "Grid reset."
                            message_start_time = pygame.time.get_ticks()
                        elif confirm_btn_hovered:
                            game.request_confirmation(state)
                            tool_active = False # Tool off when dialog opens
                            message_text = ""
                        elif hovered_cell:
                            if tool_active:
                                try:
                                    if game_grid[hovered_cell[0]][hovered_cell[1]] == "sandbag":
                                        sandbags.remove_sandbag(game_grid, hovered_cell[0], hovered_cell[1])
                                    else:
                                        sandbags.place_sandbag(game_grid, hovered_cell[0], hovered_cell[1], total_budget)
                                    message_text = ""
                                except ValueError as e:
                                    message_text = str(e)
                                    message_start_time = pygame.time.get_ticks()
                            else:
                                selected_cell = hovered_cell

                    elif state["phase"] == PHASE_CONFIRMING:
                        if yes_btn_hovered:
                            try:
                                game.confirm_routes(state, game_grid, entities_list, total_budget)
                                message_text = ""
                                # F07: start flood animation timer and compute steps ONCE
                                flood_start_ms = pygame.time.get_ticks()
                                flood_steps = flood.compute_flood_steps(game_grid, state["safe_cells"])
                            except ValueError as e:
                                message_text = str(e)
                                message_start_time = pygame.time.get_ticks()
                        elif cancel_btn_hovered:
                            game.cancel_confirmation(state)
                            message_text = ""

                    elif state["phase"] == PHASE_FLOODING:
                        # F07: Any left-click during flooding skips directly to results
                        try:
                            game.finish_flood(state)
                        except ValueError as e:
                            message_text = str(e)
                            message_start_time = pygame.time.get_ticks()

                    elif state["phase"] == PHASE_RESULTS:
                        if retry_btn_hovered:
                            game.retry_level(state, game_grid, entities_list)
                            # Reset flood animation variables
                            flood_start_ms = 0
                            flood_steps = []
                            message_text = ""
                        elif cont_btn_hovered and game.can_continue(state):
                            try:
                                outcome = campaign.complete_level(camp, state)
                                if outcome == "next_level":
                                    game_grid, entities_list, total_budget, state = load_level(camp["level"])
                                    selected_cell = None
                                    tool_active = False
                                    flood_start_ms = 0
                                    flood_steps = []
                                    message_text = f"Loaded Level {camp['level']} - {LEVEL_NAMES.get(camp['level'], '')}"
                                    message_start_time = pygame.time.get_ticks()
                                elif outcome == "summary":
                                    game.show_summary(state)
                                    message_text = ""
                            except ValueError as e:
                                message_text = str(e)
                                message_start_time = pygame.time.get_ticks()

                    elif state["phase"] == PHASE_SUMMARY:
                        if play_again_btn_hovered:
                            camp = campaign.create_campaign(start_level=1)
                            game_grid, entities_list, total_budget, state = load_level(camp["level"])
                            selected_cell = None
                            tool_active = False
                            flood_start_ms = 0
                            flood_steps = []
                            message_text = "New campaign started!"
                            message_start_time = pygame.time.get_ticks()

                elif event.button == 3: # Right click
                    if state["phase"] == PHASE_PLANNING and hovered_cell:
                        try:
                            sandbags.remove_sandbag(game_grid, hovered_cell[0], hovered_cell[1])
                            message_text = ""
                        except ValueError:
                            pass

        # 2. Logic: Flooding Animation Progress
        flooded_now = set()
        front_col = -1
        if state["phase"] == PHASE_FLOODING:
            elapsed = pygame.time.get_ticks() - flood_start_ms
            steps_done = flood.current_step(elapsed, FLOOD_STEP_MS)
            flooded_now = flood.cells_flooded_at(flood_steps, steps_done)
            front_col = steps_done - 1 if steps_done > 0 else -1

            # Check if animation is finished (sweep + end hold)
            if flood.is_flood_finished(elapsed, FLOOD_STEP_MS, COLS, FLOOD_END_HOLD_MS):
                try:
                    game.finish_flood(state)
                except ValueError as e:
                    message_text = str(e)
                    message_start_time = pygame.time.get_ticks()

        # Top panel info
        pop_total = entities.total_population(entities_list)
        build_counts = entities.count_buildings(entities_list)
        total_buildings = sum(build_counts.values())

        # Sandbag counter
        sb_remaining = sandbags.remaining_sandbags(game_grid, total_budget)
        sb_info = f"Sandbags: {sb_remaining} / {total_budget}"

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
            else: hover_text = f"({hovered_cell[0]}, {hovered_cell[1]})"

        selected_text = f"({selected_cell[0], selected_cell[1]})" if selected_cell else "-"

        # Message timer
        if message_text and pygame.time.get_ticks() - message_start_time > MESSAGE_TIMEOUT:
            message_text = ""

        # 3. Rendering
        if state["phase"] == PHASE_SUMMARY:
            # Full-window Final Summary screen (grid and panels not drawn)
            summary_data = campaign.build_final_summary(camp)
            font_title = pygame.font.Font(None, 42)
            font_table = pygame.font.Font(None, 28)
            font_large = pygame.font.Font(None, 56)
            interface.draw_final_summary(screen, summary_data, font_title, font_table, font_large, play_again_hovered=play_again_btn_hovered)

        else:
            # Standard gameplay rendering — DRAW ORDER:
            # 1. Background
            screen.fill(COLOR_BG)

            # 2. Grid cells
            interface.draw_grid(screen, game_grid)

            # 3. Cell labels (letters H, S, +, SH, B)
            interface.draw_cell_labels(screen, game_grid)

            # 4. Water and building highlights:
            # - In flooding phase: partial water wave + red tint on flooded unconnected buildings
            # - In results phase: full water + green (safe) / red (unsafe) highlights
            if state["phase"] == PHASE_FLOODING:
                interface.draw_flood(screen, flooded_now, front_col)
                interface.draw_flooded_buildings(screen, entities_list, flooded_now)
            elif state["phase"] == PHASE_RESULTS:
                all_flooded = flood.get_flooded_cells(game_grid, state["safe_cells"])
                interface.draw_flood(screen, all_flooded, -1)
                interface.draw_safe_unsafe(screen, entities_list)

            # 5. Coordinates (row/col numbers)
            interface.draw_coordinates(screen)

            # 6. Highlights (only during planning)
            if state["phase"] == PHASE_PLANNING:
                if hovered_cell:
                    interface.draw_highlight(screen, hovered_cell, COLOR_HOVER)
                if selected_cell:
                    interface.draw_highlight(screen, selected_cell, COLOR_SELECTED)

            # 7. UI Top Panel (includes level progress and running campaign score)
            running_score = sum(r["final_score"] for r in camp["level_results"].values())
            interface.draw_panels(
                screen, hover_text, selected_text, pop_total, total_buildings,
                sb_info, state["phase"], camp["level"], running_score
            )

            # 8. Bottom Panel / Phase-specific Controls:
            btn_font = pygame.font.Font(None, 30)

            if state["phase"] == PHASE_PLANNING:
                interface.draw_legend(screen)
                interface.draw_button(screen, BTN_SANDBAG_RECT, BTN_SANDBAG_LABEL, btn_font, tool_active, sb_btn_hovered)
                interface.draw_button(screen, BTN_RESET_RECT, BTN_RESET_LABEL, btn_font, tool_active, reset_btn_hovered)
                interface.draw_button(screen, BTN_CONFIRM_RECT, BTN_CONFIRM_LABEL, btn_font, False, confirm_btn_hovered)

            elif state["phase"] == PHASE_FLOODING:
                interface.draw_flood_banner(screen, pygame.font.Font(None, 32))

            elif state["phase"] == PHASE_RESULTS:
                breakdown = state["breakdown"]
                can_cont = game.can_continue(state)
                bonus_msg = game.bonus_explanation(breakdown)

                # Dynamic caption: Continue on L1/L2, View Final Summary on L3
                cont_caption = BTN_SUMMARY_LABEL if campaign.is_last_level(camp) else BTN_CONTINUE_LABEL

                # Redraw background for results panel
                pygame.draw.rect(screen, interface.COLOR_PANEL, (0, 1200 - interface.BOTTOM_PANEL_HEIGHT, 1200, interface.BOTTOM_PANEL_HEIGHT))

                # Draw detailed breakdown text
                interface.draw_results_panel(screen, breakdown, can_cont, pygame.font.Font(None, 28), camp["level"], continue_label=cont_caption)

                # Draw Results Buttons
                interface.draw_button(screen, BTN_RETRY_RECT, BTN_RETRY_LABEL, btn_font, False, retry_btn_hovered)
                if can_cont:
                    interface.draw_button(screen, BTN_CONTINUE_RECT, cont_caption, btn_font, False, cont_btn_hovered)

                # Draw bonus message if failed
                if not breakdown["passed"]:
                    msg_surf = pygame.font.Font(None, 24).render(bonus_msg, True, interface.COLOR_MSG_TEXT)
                    msg_rect = msg_surf.get_rect(center=(600, 1200 - 100))
                    screen.blit(msg_surf, msg_rect)

            # 9. Confirmation Dialog (if in confirming phase)
            if state["phase"] == PHASE_CONFIRMING:
                sb_rem = sandbags.remaining_sandbags(game_grid, total_budget)
                interface.draw_confirm_dialog(screen, sb_rem, pygame.font.Font(None, 30))

            # 10. Draw Feedback Message
            interface.draw_message(screen, message_text, btn_font)

        # Update display
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
