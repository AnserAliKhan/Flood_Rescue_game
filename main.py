import pygame
from config import WINDOW_WIDTH, WINDOW_HEIGHT, FPS

def main():
    # Initialize Pygame
    pygame.init()

    # Set up the window
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Flood Rescue")

    # Define colors
    DARK_BLUE = (20, 20, 40)
    WHITE = (255, 255, 255)

    # Set up font
    font = pygame.font.Font(None, 74)
    text_surface = font.render("FLOOD RESCUE", True, WHITE)
    text_rect = text_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))

    clock = pygame.time.Clock()
    running = True

    while running:
        # 1. Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # 2. Rendering
        screen.fill(DARK_BLUE)
        screen.blit(text_surface, text_rect)

        # Update display
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
