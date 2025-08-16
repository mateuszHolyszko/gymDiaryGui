import pygame
import numpy as np
import moderngl
from pygame.locals import DOUBLEBUF, OPENGL

from GUI.MenuManager import MenuManager
from GUI.style import StyleManager
from GUI.menus.MainMenu import MainMenu
from GUI.menus.SessionMenu import SessionMenu
from GUI.menus.ProgramMenu import ProgramMenu
from GUI.menus.StatsMenu import StatsMenu
from GUI.menus.MockLoadingMenu import MockLoadingMenu
from GUI.Notifications import Notification
from GUI.ScrollingTableVertical import ScrollingTableVertical

from workout_db_r.Database import Database
from workout_db_r.Query import Query

def main():
    # Init database and query tool passed to manager
    db = Database() 
    query = Query(db)


    # Initialize pygame with OpenGL support
    pygame.init()
    screen_size = (800, 480)
    pygame.display.set_mode(screen_size, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Modular Activity Tracker")
    clock = pygame.time.Clock()

    # === Setup moderngl context and shaders ===
    ctx = moderngl.create_context()

    # Create offscreen GUI surface
    gui_surface = pygame.Surface(screen_size)
    # Seperate framebuffer for 3D elements
    tex_3d = ctx.texture(screen_size, components=4)  # RGBA
    tex_3d.repeat_x = False
    tex_3d.repeat_y = False
    depth_3d = ctx.depth_renderbuffer(screen_size)
    fbo_3d = ctx.framebuffer(color_attachments=[tex_3d], depth_attachment=depth_3d)

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

    # Texture for GUI input
    texture_gui = ctx.texture(screen_size, 3)
    texture_gui.repeat_x = False
    texture_gui.repeat_y = False

    # Composite pass (combining 3d framebuffer with pygame screen in gpu)
    with open("GUI\\ThreeDee\\shaders\\composite.vert") as f:
        composite_vert = f.read()
    with open("GUI\\ThreeDee\\shaders\\composite.frag") as f:
        composite_frag = f.read()
    prog_composite = ctx.program(vertex_shader=composite_vert, fragment_shader=composite_frag)
    vao_composite = ctx.simple_vertex_array(prog_composite, vbo, 'in_vert', 'in_uv')

    # Create intermediate framebuffers for passes
    tex_pass1 = ctx.texture(screen_size, 3)
    tex_pass2 = ctx.texture(screen_size, 3)
    tex_pass3 = ctx.texture(screen_size, 3)
    fbo_pass1 = ctx.framebuffer(color_attachments=[tex_pass1])
    fbo_pass2 = ctx.framebuffer(color_attachments=[tex_pass2])
    fbo_pass3 = ctx.framebuffer(color_attachments=[tex_pass3])

    # Setup notification system
    notification = Notification(font_size=24, display_time=2.5)

    # Create menu manager
    manager = MenuManager(gui_surface,query,notification,ctx,fbo_3d,tex_3d)

    # Instantiate all menus
    loading_menu = MockLoadingMenu(gui_surface,manager)
    main_menu = MainMenu(gui_surface, manager)
    session_menu = SessionMenu(gui_surface, manager)
    program_menu = ProgramMenu(gui_surface, manager)
    stats_menu = StatsMenu(gui_surface, manager)
    
    # Register all menus with string names (pass instances)
    manager.register_menu("LoadingMenu", loading_menu)
    manager.register_menu("MainMenu", main_menu)
    manager.register_menu("SessionMenu", session_menu)
    manager.register_menu("ProgramMenu", program_menu)
    manager.register_menu("StatsMenu", stats_menu)

    # Start with main menu
    manager.switch_to("LoadingMenu")
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
        gui_surface.fill(StyleManager.DARK.bg_color)
        if manager.current_menu:
            manager.current_menu.render2d(gui_surface)
        notification.render(gui_surface)

        # === Convert surface to texture ===
        gui_rgb = pygame.surfarray.pixels3d(gui_surface).copy().swapaxes(0, 1)
        texture_gui.write(gui_rgb.tobytes())

        # === Render 3D into fbo_3d ===
        if manager.current_menu:
            manager.current_menu.render3d()

        current_time = pygame.time.get_ticks() / 1000.0

        # === Composite GUI and 3D into first post-process texture ===
        fbo_pass1.use()
        ctx.viewport = (0, 0, screen_size[0], screen_size[1])
        ctx.clear()
        texture_gui.use(0)
        tex_3d.use(1)
        prog_composite['tex_gui'] = 0
        prog_composite['tex_3d'] = 1
        display3d_elem = manager.current_menu.get_display3d_element()
        if display3d_elem is not None:
            prog_composite['elem_pos'].value = (
                display3d_elem.x / screen_size[0],
                display3d_elem.y / screen_size[1]
            )
            prog_composite['elem_size'].value = (
                display3d_elem.width / screen_size[0],
                display3d_elem.height / screen_size[1]
            )
        vao_composite.render(moderngl.TRIANGLE_STRIP)

        

        # === Pass 1: Distortions ===
        fbo_pass2.use()
        ctx.clear()
        tex_pass1.use(0)
        prog_distortion['time'].value = current_time
        vao_distortion.render(moderngl.TRIANGLE_STRIP)

        # === Pass 2: Lighting (now after distortion) ===
        fbo_pass3.use()
        ctx.clear()
        tex_pass2.use(0)
        prog_lighting['time'].value = current_time

        if manager.focus_manager.current_focus:                
            fx, fy = manager.focus_manager.current_focus.x, manager.focus_manager.current_focus.y
            # if its scrolling table, needs to translate y to viewport pos
            if isinstance(manager.focus_manager.current_focus.parent_panel, ScrollingTableVertical):
                fy = fy - manager.focus_manager.current_focus.parent_panel.scroll_offset
            fw, fh = manager.focus_manager.current_focus.width, manager.focus_manager.current_focus.height
            prog_lighting['focus_pos'].value = (fx / screen_size[0], fy / screen_size[1])
            prog_lighting['focus_size'].value = (fw / screen_size[0], fh / screen_size[1])

            # NEW: parent panel bounds
            px = manager.focus_manager.current_focus.parent_panel.x
            py = manager.focus_manager.current_focus.parent_panel.y
            pw = manager.focus_manager.current_focus.parent_panel.width
            ph = manager.focus_manager.current_focus.parent_panel.height
            prog_lighting['clip_pos'].value  = (px / screen_size[0], py / screen_size[1])
            prog_lighting['clip_size'].value = (pw / screen_size[0], ph / screen_size[1])
        else:
            prog_lighting['focus_size'].value = (0.0, 0.0)
            prog_lighting['clip_size'].value  = (0.0, 0.0)

        vao_lighting.render(moderngl.TRIANGLE_STRIP)

        bg = StyleManager.DARK.bg_color
        bg_normalized = (bg[0]/255.0, bg[1]/255.0, bg[2]/255.0)

        # === Pass 3: CRT barrel distortion ===
        ctx.screen.use()
        ctx.clear()
        tex_pass3.use(0)
        vao_barrel.render(moderngl.TRIANGLE_STRIP)

        # === Swap buffers ===
        pygame.display.flip()
        clock.tick(12)

    pygame.quit()

if __name__ == "__main__":
    main()
