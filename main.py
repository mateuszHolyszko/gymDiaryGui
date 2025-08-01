import pygame
from GUI.MenuManager import MenuManager
from GUI.menus.MainMenu import MainMenu
from GUI.menus.SessionMenu import SessionMenu
from GUI.menus.ProgramMenu import ProgramMenu
from GUI.menus.StatsMenu import StatsMenu
from GUI.menus.Form import Form
from GUI.Notifications import Notification

def main():
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Gym Diary")
    clock = pygame.time.Clock()

    # Create notification system
    notification = Notification(font_size=24, display_time=2.5)

    # Create menu manager
    manager = MenuManager(screen,notification)
    
    # Instantiate all menus
    main_menu = MainMenu(screen, manager)
    session_menu = SessionMenu(screen, manager)
    program_menu = ProgramMenu(screen, manager)
    stats_menu = StatsMenu(screen, manager)
    form_menu = Form(screen, manager)
    
    # Register all menus with string names (pass instances)
    manager.register_menu("MainMenu", main_menu)
    manager.register_menu("SessionMenu", session_menu)
    manager.register_menu("ProgramMenu", program_menu)
    manager.register_menu("StatsMenu", stats_menu)
    manager.register_menu("Form", form_menu)
    
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
        
        # Render notification (if active)
        notification.render(screen)
        
        pygame.display.flip()
        clock.tick(30)  # 30 FPS

    pygame.quit()

if __name__ == "__main__":
    main()