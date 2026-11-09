"""
main.py - Entry Point for Flood Rescue (F12)

Initializes Pygame, coordinates screen states and campaign flows,
handles user input events, and drives the per-frame rendering loop.
"""

import pygame
from config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS, ROWS, COLS,
    COLOR_BG, COLOR_HOVER, COLOR_SELECTED,
    BTN_SANDBAG_RECT, BTN_RESET_RECT,
    BTN_CONFIRM_RECT, BTN_RETRY_RECT, BTN_CONTINUE_RECT,
    BTN_SANDBAG_LABEL, BTN_RESET_LABEL, BTN_CONFIRM_LABEL,
    BTN_RETRY_LABEL, BTN_CONTINUE_LABEL, BTN_SUMMARY_LABEL,
    SUMMARY_PLAY_AGAIN_RECT, SUMMARY_MENU_RECT,
    DIALOG_YES_RECT, DIALOG_CANCEL_RECT,
    MESSAGE_TIMEOUT, LEVEL_NAMES, DEBUG_LEVEL_KEYS, DEBUG_PRINT,
    FLOOD_STEP_MS, FLOOD_END_HOLD_MS,
    PHASE_PLANNING, PHASE_CONFIRMING, PHASE_FLOODING, PHASE_RESULTS, PHASE_SUMMARY,
    SCREEN_MENU, SCREEN_INSTRUCTIONS, SCREEN_GAME,
    MENU_BUTTON_START, MENU_BUTTON_INSTRUCTIONS, MENU_BUTTON_EXIT,
    MENU_BUTTONS, INSTRUCTIONS_BACK_RECT,
    WINDOW_TITLE, MSG_GRID_RESET, MSG_NEW_CAMPAIGN,
    RESULTS_BONUS_MSG_POS, MOUSE_BTN_LEFT, MOUSE_BTN_RIGHT
)
import grid
import interface
import entities
import sandbags
import game
import flood
import campaign
import screens


def load_level(level_num):
    """
    Prepares a fresh level: builds grid and entities, computes baseline and budget,
    and initializes a fresh game state.
    """
    grid_data, entities_data, baseline_val, budget = campaign.prepare_level(level_num)
    new_state = game.create_game_state()
    if DEBUG_PRINT:
        print(f"Level {level_num}: baseline {baseline_val}, budget {budget}")
    return grid_data, entities_data, budget, new_state


def main():
    # Initialize Pygame
    pygame.init()

    # Set up the window
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)

    # Initialize fonts ONCE at application startup (F12)
    fonts = interface.init_fonts()

    # Application Screen State (starts on menu, no level loaded yet)
    app = screens.create_app_state()

    # Gameplay and Campaign State (initialized upon Start Game)
    camp = None
    game_grid = None
    entities_list = None
    total_budget = 0
    state = None
    selected_cell = None

    # Flood Animation State
    flood_start_ms = 0
    flood_steps = []

    # Tool and Message State
    tool_active = False
    message_text = ""
    message_start_time = 0

    # Per-frame interaction and hover defaults
    hovered_menu_btn = None
    back_btn_hovered = False
    hovered_cell = None
    sb_btn_hovered = False
    reset_btn_hovered = False
    confirm_btn_hovered = False
    retry_btn_hovered = False
    cont_btn_hovered = False
    yes_btn_hovered = False
    cancel_btn_hovered = False
    play_again_btn_hovered = False
    menu_btn_hovered = False

    clock = pygame.time.Clock()
    running = True

    while running:
        mouse_pos = pygame.mouse.get_pos()

        # Reset per-frame interaction and hover defaults
        hovered_menu_btn = None
        back_btn_hovered = False
        hovered_cell = None
        sb_btn_hovered = False
        reset_btn_hovered = False
        confirm_btn_hovered = False
        retry_btn_hovered = False
        cont_btn_hovered = False
        yes_btn_hovered = False
        cancel_btn_hovered = False
        play_again_btn_hovered = False
        menu_btn_hovered = False

        # ==============================================================
        # 1. EVENT HANDLING ROUTED BY SCREEN
        # ==============================================================

        if app["screen"] == SCREEN_MENU:
            hovered_menu_btn = screens.button_at(MENU_BUTTONS, mouse_pos[0], mouse_pos[1])

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == MOUSE_BTN_LEFT:
                    if hovered_menu_btn == MENU_BUTTON_START:
                        try:
                            camp = campaign.create_campaign(start_level=1)
                            game_grid, entities_list, total_budget, state = load_level(camp["level"])
                            selected_cell = None
                            tool_active = False
                            flood_start_ms = 0
                            flood_steps = []
                            message_text = ""
                            screens.change_screen(app, SCREEN_GAME)
                        except ValueError as e:
                            message_text = str(e)
                            message_start_time = pygame.time.get_ticks()
                    elif hovered_menu_btn == MENU_BUTTON_INSTRUCTIONS:
                        try:
                            screens.change_screen(app, SCREEN_INSTRUCTIONS)
                        except ValueError:
                            pass
                    elif hovered_menu_btn == MENU_BUTTON_EXIT:
                        running = False

        elif app["screen"] == SCREEN_INSTRUCTIONS:
            back_btn_hovered = pygame.Rect(INSTRUCTIONS_BACK_RECT).collidepoint(mouse_pos)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        try:
                            screens.change_screen(app, SCREEN_MENU)
                        except ValueError:
                            pass
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == MOUSE_BTN_LEFT:
                    if back_btn_hovered:
                        try:
                            screens.change_screen(app, SCREEN_MENU)
                        except ValueError:
                            pass

        elif app["screen"] == SCREEN_GAME and state is not None:
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
            play_again_btn_hovered = pygame.Rect(SUMMARY_PLAY_AGAIN_RECT).collidepoint(mouse_pos)
            menu_btn_hovered = pygame.Rect(SUMMARY_MENU_RECT).collidepoint(mouse_pos)

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
                    if event.button == MOUSE_BTN_LEFT:
                        if state["phase"] == PHASE_PLANNING:
                            if sb_btn_hovered:
                                tool_active = not tool_active
                                message_text = ""
                            elif reset_btn_hovered:
                                sandbags.clear_sandbags(game_grid)
                                message_text = MSG_GRID_RESET
                                message_start_time = pygame.time.get_ticks()
                            elif confirm_btn_hovered:
                                game.request_confirmation(state)
                                tool_active = False
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
                                    flood_start_ms = pygame.time.get_ticks()
                                    flood_steps = flood.compute_flood_steps(game_grid, state["safe_cells"])
                                except ValueError as e:
                                    message_text = str(e)
                                    message_start_time = pygame.time.get_ticks()
                            elif cancel_btn_hovered:
                                game.cancel_confirmation(state)
                                message_text = ""

                        elif state["phase"] == PHASE_FLOODING:
                            try:
                                game.finish_flood(state)
                            except ValueError as e:
                                message_text = str(e)
                                message_start_time = pygame.time.get_ticks()

                        elif state["phase"] == PHASE_RESULTS:
                            if retry_btn_hovered:
                                game.retry_level(state, game_grid, entities_list)
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
                                message_text = MSG_NEW_CAMPAIGN
                                message_start_time = pygame.time.get_ticks()
                            elif menu_btn_hovered:
                                if screens.can_return_to_menu(state):
                                    try:
                                        screens.change_screen(app, SCREEN_MENU)
                                        camp = None
                                        game_grid = None
                                        entities_list = None
                                        total_budget = 0
                                        state = None
                                        selected_cell = None
                                        tool_active = False
                                        flood_start_ms = 0
                                        flood_steps = []
                                        message_text = ""
                                    except ValueError as e:
                                        message_text = str(e)
                                        message_start_time = pygame.time.get_ticks()

                    elif event.button == MOUSE_BTN_RIGHT:
                        if state["phase"] == PHASE_PLANNING and hovered_cell:
                            try:
                                sandbags.remove_sandbag(game_grid, hovered_cell[0], hovered_cell[1])
                                message_text = ""
                            except ValueError:
                                pass

        # ==============================================================
        # 2. GAME LOGIC (Active during SCREEN_GAME)
        # ==============================================================

        flooded_now = set()
        front_col = -1

        if app["screen"] == SCREEN_GAME and state is not None:
            if state["phase"] == PHASE_FLOODING:
                elapsed = pygame.time.get_ticks() - flood_start_ms
                steps_done = flood.current_step(elapsed, FLOOD_STEP_MS)
                flooded_now = flood.cells_flooded_at(flood_steps, steps_done)
                front_col = steps_done - 1 if steps_done > 0 else -1

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
            sb_remaining = sandbags.remaining_sandbags(game_grid, total_budget)
            sb_info = f"Sandbags: {sb_remaining} / {total_budget}"

            # Building hover details
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

            selected_text = f"({selected_cell[0], selected_cell[1]})" if selected_cell else "-"

        # Message timeout
        if message_text and pygame.time.get_ticks() - message_start_time > MESSAGE_TIMEOUT:
            message_text = ""

        # ==============================================================
        # 3. RENDERING ROUTED BY SCREEN (Uses cached fonts)
        # ==============================================================

        if app["screen"] == SCREEN_MENU:
            interface.draw_menu(
                screen, hovered_menu_btn,
                fonts["title_large"], fonts["button"], fonts["button_large"]
            )

        elif app["screen"] == SCREEN_INSTRUCTIONS:
            sections = screens.build_instruction_sections()
            interface.draw_instructions(
                screen, sections, back_btn_hovered,
                fonts["title_main"], fonts["heading"], fonts["instructions"], fonts["button"]
            )

        elif app["screen"] == SCREEN_GAME and state is not None:
            if state["phase"] == PHASE_SUMMARY:
                summary_data = campaign.build_final_summary(camp)
                interface.draw_final_summary(
                    screen, summary_data,
                    fonts["title_main"], fonts["body"], fonts["large"],
                    play_again_hovered=play_again_btn_hovered,
                    menu_hovered=menu_btn_hovered
                )
            else:
                # 1. Background
                screen.fill(COLOR_BG)

                # 2. Grid cells
                interface.draw_grid(screen, game_grid)

                # 3. Cell labels
                interface.draw_cell_labels(screen, game_grid, fonts["cell"])

                # 4. Water and highlights
                if state["phase"] == PHASE_FLOODING:
                    interface.draw_flood(screen, flooded_now, front_col)
                    interface.draw_flooded_buildings(screen, entities_list, flooded_now)
                elif state["phase"] == PHASE_RESULTS:
                    all_flooded = flood.get_flooded_cells(game_grid, state["safe_cells"])
                    interface.draw_flood(screen, all_flooded, -1)
                    interface.draw_safe_unsafe(screen, entities_list)

                # 5. Coordinates
                interface.draw_coordinates(screen, fonts["coord"])

                # 6. Highlights (planning only)
                if state["phase"] == PHASE_PLANNING:
                    if hovered_cell:
                        interface.draw_highlight(screen, hovered_cell, COLOR_HOVER)
                    if selected_cell:
                        interface.draw_highlight(screen, selected_cell, COLOR_SELECTED)

                # 7. UI Top Panel
                running_score = sum(r["final_score"] for r in camp["level_results"].values())
                interface.draw_panels(
                    screen, hover_text, selected_text, pop_total, total_buildings,
                    sb_info, state["phase"], camp["level"], running_score,
                    fonts["section"]
                )

                # 8. Bottom Panel / Controls
                btn_font = fonts["button"]
                if state["phase"] == PHASE_PLANNING:
                    interface.draw_legend(screen, btn_font)
                    interface.draw_button(screen, BTN_SANDBAG_RECT, BTN_SANDBAG_LABEL, btn_font, tool_active, sb_btn_hovered)
                    interface.draw_button(screen, BTN_RESET_RECT, BTN_RESET_LABEL, btn_font, tool_active, reset_btn_hovered)
                    interface.draw_button(screen, BTN_CONFIRM_RECT, BTN_CONFIRM_LABEL, btn_font, False, confirm_btn_hovered)

                elif state["phase"] == PHASE_FLOODING:
                    interface.draw_flood_banner(screen, fonts["button_large"], fonts["small"])

                elif state["phase"] == PHASE_RESULTS:
                    breakdown = state["breakdown"]
                    can_cont = game.can_continue(state)
                    bonus_msg = game.bonus_explanation(breakdown)
                    cont_caption = BTN_SUMMARY_LABEL if campaign.is_last_level(camp) else BTN_CONTINUE_LABEL

                    interface.draw_results_panel(screen, breakdown, can_cont, fonts["body"], camp["level"], continue_label=cont_caption)
                    interface.draw_button(screen, BTN_RETRY_RECT, BTN_RETRY_LABEL, btn_font, False, retry_btn_hovered)
                    if can_cont:
                        interface.draw_button(screen, BTN_CONTINUE_RECT, cont_caption, btn_font, False, cont_btn_hovered)

                    if not breakdown["passed"]:
                        msg_surf = fonts["small"].render(bonus_msg, True, interface.COLOR_MSG_TEXT)
                        msg_rect = msg_surf.get_rect(center=RESULTS_BONUS_MSG_POS)
                        screen.blit(msg_surf, msg_rect)

                # 9. Confirmation Dialog
                if state["phase"] == PHASE_CONFIRMING:
                    sb_rem = sandbags.remaining_sandbags(game_grid, total_budget)
                    interface.draw_confirm_dialog(screen, sb_rem, btn_font)

                # 10. Feedback Message
                interface.draw_message(screen, message_text, btn_font)

        # Update display
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
