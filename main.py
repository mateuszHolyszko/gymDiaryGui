import pygame
from GUI.MenuManager import MenuManager
from GUI.menus.MainMenu import MainMenu
from GUI.menus.SessionMenu import SessionMenu
from GUI.menus.ProgramMenu import ProgramMenu
from GUI.menus.StatsMenu import StatsMenu

def main():
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Gym Diary")
    clock = pygame.time.Clock()

    # Create menu manager
    manager = MenuManager(screen)
    
    # Register all menus with string names
    manager.register_menu("MainMenu", MainMenu)
    manager.register_menu("SessionMenu", SessionMenu)
    manager.register_menu("ProgramMenu", ProgramMenu)
    manager.register_menu("StatsMenu", StatsMenu)
    
    # Start with main menu
    manager.switch_to("MainMenu")

    # Main game loop
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Handle menu navigation keys globally
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Optional: Add back navigation logic if needed
                    pass
            
            # Pass all events to menu manager
            manager.handle_event(event)
        
        # Clear screen
        screen.fill((0, 0, 0))  # Black background
        
        # Render current menu
        if manager.current_menu:
            manager.current_menu.render(screen)
        
        pygame.display.flip()
        clock.tick(60)  # 60 FPS

    pygame.quit()

if __name__ == "__main__":
    main()