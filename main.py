import pygame
from elements.base import Element
from elements.button import Button
from elements.inputField import InputField
from elements.window_manager import WindowManager
from elements.panel import Panel 
from menus.mainMenu import main_menu_controller
from elements.keyBinds import KeyBinds
from elements.table import Table, Cell

def build_example_tree(window_manager):
    main_window, first_focus = main_menu_controller(window_manager)
    root = Panel("root", layout_type="vertical",draw_box=False) 
    main_window.draw_box = False  # Make main_window invisible 
    root.add_child(main_window)
    # Add other windows here as needed
    return root, first_focus

def main():
    pygame.init()
    WIDTH, HEIGHT = 820, 480
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Gym Diary GUI v2")
    font = pygame.font.Font(None, 28)  # Initialize font

    # Build tree and manager
    root = Element("root", selectable=False)
    window_manager = WindowManager(root)
    root, current = build_example_tree(window_manager)
    window_manager.root = root

    current.selected = True

    print("\nControls: [→]next, [←]prev, [SPACE]child, [ESC]up/parent, [ENTER] press button, [q]uit\n")

    FPS = 60  # Set your desired refresh rate here
    clock = pygame.time.Clock()
    running = True
    running_flag = [True]  # Use a mutable object so it can be changed in global_keys

    while running_flag[0]:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running_flag[0] = False
            elif event.type == pygame.KEYDOWN:
                # 1. Always send event to selected element first
                handled = current.on_key(event)
                
                # 2. If not handled by element, handle navigation via parent panel/table
                if not handled:
                    parent_container = None
                    node = current.parent
                    
                    # Find the nearest parent that's either Panel or Table
                    while node:
                        if isinstance(node, (Panel, Table)):
                            parent_container = node
                            break
                        node = node.parent

                    if parent_container:
                        layout_type = getattr(parent_container, "layout_type", "vertical")
                        handler = KeyBinds.layout_map.get(layout_type)
                        if handler:
                            new_focus = handler(event, parent_container, current)
                            if new_focus != current:
                                current.selected = False
                                current = new_focus
                                current.selected = True

                # 3. Handle global keys via KeyBinds (these always work)
                current, running_flag = KeyBinds.global_keys(event, current, running_flag)

        screen.fill((0, 0, 0))  # Black background

        # Render the UI tree
        root.render(screen, [root] + current.get_path()[1:], font, 0, 0, screen.get_width(), screen.get_height())

        # switching menus logic
        if "current_focus" in window_manager.context:
            current.selected = False
            current = window_manager.context["current_focus"]
            current.selected = True
            del window_manager.context["current_focus"]

        pygame.display.flip()
        clock.tick(FPS)  # Limit to specified FPS

    pygame.quit()

if __name__ == "__main__":
    main()