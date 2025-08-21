import pygame
import numpy as np
import moderngl
from pygame.locals import DOUBLEBUF, OPENGL

from GUI.MenuManager import MenuManager
from GUI.style import StyleManager
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

    # === Setup moderngl context for OpenGL ES 2.0 ===
    ctx = moderngl.create_context(require=200)  # Use 300 for better compatibility with ES 2.0
    
    # Alternative: try context creation with specific backend if needed
    #ctx = moderngl.create_context(standalone=True, backend='egl')
    
    # Create offscreen GUI surface
    gui_surface = pygame.Surface(screen_size)
    
    # Separate framebuffer for 3D elements - use RGBA format
    tex_3d = ctx.texture(screen_size, 4)  # RGBA
    tex_3d.repeat_x = False
    tex_3d.repeat_y = False
    depth_3d = ctx.depth_renderbuffer(screen_size)
    fbo_3d = ctx.framebuffer(color_attachments=[tex_3d], depth_attachment=depth_3d)

    # Load GLSL 1.20 shaders from files
    with open("GUI/Distortions/distortion.vert") as f:
        vertex_shader = f.read()
    with open("GUI/Distortions/lighting.frag") as f:  # Use ES 2.0 version
        lighting_frag = f.read()
    with open("GUI/Distortions/distortion.frag") as f:  # Use ES 2.0 version
        distortion_frag = f.read()
    with open("GUI/Distortions/barrel.frag") as f:  # Use ES 2.0 version
        barrel_frag = f.read()

    # Create shader programs for each pass
    prog_lighting = ctx.program(vertex_shader=vertex_shader, fragment_shader=lighting_frag)
    prog_distortion = ctx.program(vertex_shader=vertex_shader, fragment_shader=distortion_frag)
    prog_barrel = ctx.program(vertex_shader=vertex_shader, fragment_shader=barrel_frag)
    
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

    # Create vertex arrays with proper attribute names
    vao_lighting = ctx.vertex_array(prog_lighting, [(vbo, '2f 2f', 'in_vert', 'in_uv')])
    vao_distortion = ctx.vertex_array(prog_distortion, [(vbo, '2f 2f', 'in_vert', 'in_uv')])
    vao_barrel = ctx.vertex_array(prog_barrel, [(vbo, '2f 2f', 'in_vert', 'in_uv')])

    # Texture for GUI input - use RGBA format for better compatibility
    texture_gui = ctx.texture(screen_size, 4)  # RGBA
    texture_gui.repeat_x = False
    texture_gui.repeat_y = False

    # Composite pass (combining 3d framebuffer with pygame screen in gpu)
    with open("GUI/ThreeDee/shaders/composite.vert") as f:
        composite_vert = f.read()
    with open("GUI/ThreeDee/shaders/composite.frag") as f:  # Use ES 2.0 version
        composite_frag = f.read()
    prog_composite = ctx.program(vertex_shader=composite_vert, fragment_shader=composite_frag)
    vao_composite = ctx.vertex_array(prog_composite, [(vbo, '2f 2f', 'in_vert', 'in_uv')])

    # Create intermediate framebuffers for passes - use RGBA format
    tex_pass1 = ctx.texture(screen_size, 4)  # RGBA
    tex_pass2 = ctx.texture(screen_size, 4)  # RGBA
    tex_pass3 = ctx.texture(screen_size, 4)  # RGBA
    fbo_pass1 = ctx.framebuffer(color_attachments=[tex_pass1])
    fbo_pass2 = ctx.framebuffer(color_attachments=[tex_pass2])
    fbo_pass3 = ctx.framebuffer(color_attachments=[tex_pass3])

    # Setup notification system
    notification = Notification(font_size=24, display_time=2.5)

    # Create menu manager
    manager = MenuManager(gui_surface, query, notification, ctx, fbo_3d, tex_3d)

    # Instantiate all menus
    loading_menu = MockLoadingMenu(gui_surface, manager)
    
    # Register all menus with string names
    manager.register_menu("LoadingMenu", loading_menu)
    
    # Start with main menu
    manager.switch_to("LoadingMenu")
    
    # Main game loop
    running = True
    last_time = pygame.time.get_ticks() / 1000.0
    
    while running:
        current_time = pygame.time.get_ticks() / 1000.0
        delta_time = current_time - last_time
        last_time = current_time
        
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

        # If menu has update() perform it
        if hasattr(manager.current_menu, "update"):
            manager.current_menu.update(delta_time)

        # === Draw GUI to offscreen surface ===
        gui_surface.fill(StyleManager.DARK.bg_color)
        if manager.current_menu:
            manager.current_menu.render2d(gui_surface)
        notification.render(gui_surface)

        # === Convert surface to texture ===
        # Create an RGBA surface and blit the original onto it
        gui_rgba = pygame.Surface(screen_size, pygame.SRCALPHA)
        gui_rgba.blit(gui_surface, (0, 0))

        # Convert to bytes in RGBA format
        texture_data = pygame.image.tostring(gui_rgba, 'RGBA', False)
        texture_gui.write(texture_data)

        # === Render 3D into fbo_3d ===
        if manager.current_menu:
            manager.current_menu.render3d()

        # === Composite GUI and 3D into first post-process texture ===
        fbo_pass1.use()
        ctx.viewport = (0, 0, screen_size[0], screen_size[1])
        ctx.clear(0.0, 0.0, 0.0, 1.0)
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
        ctx.clear(0.0, 0.0, 0.0, 1.0)
        tex_pass1.use(0)
        prog_distortion['time'].value = current_time
        vao_distortion.render(moderngl.TRIANGLE_STRIP)

        # === Pass 2: Lighting (now after distortion) ===
        fbo_pass3.use()
        ctx.clear(0.0, 0.0, 0.0, 1.0)
        tex_pass2.use(0)
        prog_lighting['time'].value = current_time

        if manager.focus_manager and manager.focus_manager.current_focus:                
            fx, fy = manager.focus_manager.current_focus.x, manager.focus_manager.current_focus.y
            # if its scrolling table, needs to translate y to viewport pos
            if isinstance(manager.focus_manager.current_focus.parent_panel, ScrollingTableVertical):
                fy = fy - manager.focus_manager.current_focus.parent_panel.scroll_offset
            fw, fh = manager.focus_manager.current_focus.width, manager.focus_manager.current_focus.height
            prog_lighting['focus_pos'].value = (fx / screen_size[0], fy / screen_size[1])
            prog_lighting['focus_size'].value = (fw / screen_size[0], fh / screen_size[1])

            # Parent panel bounds
            if hasattr(manager.focus_manager.current_focus, 'parent_panel'):
                px = manager.focus_manager.current_focus.parent_panel.x
                py = manager.focus_manager.current_focus.parent_panel.y
                pw = manager.focus_manager.current_focus.parent_panel.width
                ph = manager.focus_manager.current_focus.parent_panel.height
                prog_lighting['clip_pos'].value = (px / screen_size[0], py / screen_size[1])
                prog_lighting['clip_size'].value = (pw / screen_size[0], ph / screen_size[1])
            else:
                prog_lighting['clip_size'].value = (0.0, 0.0)
        else:
            prog_lighting['focus_size'].value = (0.0, 0.0)
            prog_lighting['clip_size'].value = (0.0, 0.0)

        vao_lighting.render(moderngl.TRIANGLE_STRIP)

        # === Pass 3: CRT barrel distortion ===
        ctx.screen.use()
        ctx.clear(0.0, 0.0, 0.0, 1.0)
        tex_pass3.use(0)
        vao_barrel.render(moderngl.TRIANGLE_STRIP)

        # === Swap buffers ===
        pygame.display.flip()
        clock.tick(12)

    pygame.quit()

if __name__ == "__main__":
    main()
