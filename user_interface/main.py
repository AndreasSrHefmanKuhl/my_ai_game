import pygame
from config.states import GameStateManager
from config.database import init_db


def main():
    """
        The primary entry point for the Schaolin Vania application.

        This function performs the following setup and loop operations:
        1. Initializes the Pygame engine and the local SQLite database.
        2. Configures the main display window (800x600 resolution).
        3. Instantiates the GameStateManager to handle scene transitions.
        4. Runs the core application loop, which:
            - Calculates delta time (dt) for framerate-independent movement.
            - Processes system events (like quitting the window).
            - Delegates logic updates and rendering to the state manager.
            - Updates the physical display at a target of 60 frames per second.
        """

    pygame.init()
    init_db()  #

    display = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Schaolin Vania")

    # Initialize the Manager
    manager = GameStateManager(display)
    clock = pygame.time.Clock()

    while True:
        dt = clock.tick(60) / 1000.0
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                return


        manager.update(dt, events)
        manager.draw()

        pygame.display.update()


if __name__ == "__main__":
    main()