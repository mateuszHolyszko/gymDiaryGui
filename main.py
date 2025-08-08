import pygame
import numpy as np
import moderngl
from pathlib import Path
from pygame.locals import DOUBLEBUF, OPENGL

from GUI.MenuManager import MenuManager
from GUI.menus.MainMenu import MainMenu
from GUI.menus.SessionMenu import SessionMenu
from GUI.menus.ProgramMenu import ProgramMenu
from GUI.menus.StatsMenu import StatsMenu
from GUI.menus.FormYesNo import Form
from GUI.Notifications import Notification

def main():
    # Initialize pygame with OpenGL support
    pygame.init()
    screen_size = (800, 480)
    pygame.display.set_mode(screen_size, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Gym Diary")
    clock = pygame.time.Clock()

    # === Setup moderngl context and shaders ===
    ctx = moderngl.create_context()

    # Load shaders from files
    with open("GUI/Distortions/distortion.vert") as f:
        vertex_shader = f.read()
    with open("GUI/Distortions/distortion.frag") as f:
        fragment_shader = f.read()

    prog = ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)
    prog['time'] = 0.0
    prog['intensity'] = 0.3  # Default distortion level
    

    # Fullscreen quad
    vertices = np.array([
        -1.0,  1.0, 0.0, 1.0,
        -1.0, -1.0, 0.0, 0.0,
         1.0,  1.0, 1.0, 1.0,
         1.0, -1.0, 1.0, 0.0
    ], dtype='f4')

    vbo = ctx.buffer(vertices.tobytes())
    vao = ctx.simple_vertex_array(prog, vbo, 'in_vert', 'in_uv')

    # Create offscreen GUI surface
    gui_surface = pygame.Surface(screen_size)

    # Texture for shader input
    texture = ctx.texture(screen_size, 3)
    texture.repeat_x = False
    texture.repeat_y = False

    # Setup notification system
    notification = Notification(font_size=24, display_time=2.5)

    # Create menu manager
    manager = MenuManager(gui_surface, notification)

    # Instantiate all menus
    main_menu = MainMenu(gui_surface, manager)
    session_menu = SessionMenu(gui_surface, manager)
    program_menu = ProgramMenu(gui_surface, manager)
    stats_menu = StatsMenu(gui_surface, manager)
    form_menu = Form(gui_surface, manager)
    
    # Register all menus with string names (pass instances)
    manager.register_menu("MainMenu", main_menu)
    manager.register_menu("SessionMenu", session_menu)
    manager.register_menu("ProgramMenu", program_menu)
    manager.register_menu("StatsMenu", stats_menu)

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

        # === Draw GUI to offscreen surface ===
        gui_surface.fill((0, 0, 0))
        if manager.current_menu:
            manager.current_menu.render(gui_surface)
        notification.render(gui_surface)

        # === Convert surface to texture ===
        gui_rgb = pygame.surfarray.pixels3d(gui_surface).copy().swapaxes(0, 1)
        texture.write(gui_rgb.tobytes())

        # === Run shader ===
        ctx.clear()
        texture.use()
        prog['time'].value = pygame.time.get_ticks() / 1000.0
        vao.render(moderngl.TRIANGLE_STRIP)

        # === Swap buffers ===
        pygame.display.flip()
        clock.tick(12)

    pygame.quit()

if __name__ == "__main__":
    main()