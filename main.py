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
    with open("GUI/Distortions/lighting.frag") as f:
        lighting_frag = f.read()
    with open("GUI/Distortions/distortion.frag") as f:
        distortion_frag = f.read()
    with open("GUI/Distortions/barrel.frag") as f:
        barrel_frag = f.read()

    # Create shader programs for each pass
    prog_lighting   = ctx.program(vertex_shader=vertex_shader, fragment_shader=lighting_frag)
    prog_distortion = ctx.program(vertex_shader=vertex_shader, fragment_shader=distortion_frag)
    prog_barrel     = ctx.program(vertex_shader=vertex_shader, fragment_shader=barrel_frag)

    # Initialize some default uniform values
    prog_distortion['time'] = 0.0
    prog_distortion['intensity'] = 0.2
    prog_lighting['time'] = 0.0

    # Fullscreen quad
    vertices = np.array([
        -1.0,  1.0, 0.0, 1.0,
        -1.0, -1.0, 0.0, 0.0,
         1.0,  1.0, 1.0, 1.0,
         1.0, -1.0, 1.0, 0.0
    ], dtype='f4')
    vbo = ctx.buffer(vertices.tobytes())

    vao_lighting   = ctx.simple_vertex_array(prog_lighting,   vbo, 'in_vert', 'in_uv')
    vao_distortion = ctx.simple_vertex_array(prog_distortion, vbo, 'in_vert', 'in_uv')
    vao_barrel     = ctx.simple_vertex_array(prog_barrel,     vbo, 'in_vert', 'in_uv')

    # Create offscreen GUI surface
    gui_surface = pygame.Surface(screen_size)

    # Texture for GUI input
    texture_gui = ctx.texture(screen_size, 3)
    texture_gui.repeat_x = False
    texture_gui.repeat_y = False

    # Create intermediate framebuffers for passes
    tex_pass1 = ctx.texture(screen_size, 3)
    tex_pass2 = ctx.texture(screen_size, 3)
    fbo_pass1 = ctx.framebuffer(color_attachments=[tex_pass1])
    fbo_pass2 = ctx.framebuffer(color_attachments=[tex_pass2])

    # Setup notification system
    notification = Notification(font_size=24, display_time=2.5)

    # Create menu manager
    manager = MenuManager(gui_surface, notification)

    # Instantiate all menus
    main_menu = MainMenu(gui_surface, manager)
    session_menu = SessionMenu(gui_surface, manager)
    program_menu = ProgramMenu(gui_surface, manager)
    stats_menu = StatsMenu(gui_surface, manager)
    
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
        texture_gui.write(gui_rgb.tobytes())

        current_time = pygame.time.get_ticks() / 1000.0

        # === Pass 1: Lighting ===
        fbo_pass2.use()
        ctx.clear()
        tex_pass1.use()
        prog_lighting['time'].value = current_time
        if manager.focus_manager.current_focus:
            fx, fy = manager.focus_manager.current_focus.x, manager.focus_manager.current_focus.y
            fw, fh = manager.focus_manager.current_focus.width, manager.focus_manager.current_focus.height
            # Normalize
            prog_lighting['focus_pos'].value = (fx / screen_size[0], fy / screen_size[1])
            prog_lighting['focus_size'].value = (fw / screen_size[0], fh / screen_size[1])
        else:
            prog_lighting['focus_size'].value = (0.0, 0.0)
        vao_lighting.render(moderngl.TRIANGLE_STRIP)

        # === Pass 2: Distortions ===
        fbo_pass1.use()
        ctx.clear()
        texture_gui.use()
        prog_distortion['time'].value = current_time
        vao_distortion.render(moderngl.TRIANGLE_STRIP)

        # === Pass 3: CRT barrel distortion ===
        ctx.screen.use()
        ctx.clear()
        tex_pass2.use()
        vao_barrel.render(moderngl.TRIANGLE_STRIP)

        # === Swap buffers ===
        pygame.display.flip()
        clock.tick(12)

    pygame.quit()

if __name__ == "__main__":
    main()
