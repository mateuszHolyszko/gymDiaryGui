import ctypes
import pygame
import numpy as np
from pygame.locals import DOUBLEBUF, OPENGL

# --- OpenGL (raw GL 2.0) ---
from OpenGL.GL import *

# --- Your imports ---
from GUI.MenuManager import MenuManager
from GUI.style import StyleManager
from GUI.menus.MockLoadingMenu import MockLoadingMenu
from GUI.Notifications import Notification
from GUI.ScrollingTableVertical import ScrollingTableVertical

from workout_db_r.Database import Database
from workout_db_r.Query import Query


# =========================
# GL helpers (GL 2.0 only)
# =========================
import gl_helpers

    

# =========================
# Main application (PyOpenGL)
# =========================

def main():
    # Init DB + query
    db = Database()
    query = Query(db)

    # Pygame + GL context
    pygame.init()
    screen_size = (800, 480)
    pygame.display.set_mode(screen_size, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Modular Activity Tracker (PyOpenGL GL2.0)")
    clock = pygame.time.Clock()

    w, h = screen_size
    glViewport(0, 0, w, h)
    glDisable(GL_DEPTH_TEST)

    # Offscreen GUI surface
    gui_surface = pygame.Surface(screen_size, pygame.SRCALPHA)

    # === Load shaders (GLSL 1.20/2.0) ===
    def read(path):
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

    vertex_shader_src = read("GUI/Distortions/distortion.vert")
    lighting_frag_src = read("GUI/Distortions/lighting.frag")
    distortion_frag_src = read("GUI/Distortions/distortion.frag")
    barrel_frag_src = read("GUI/Distortions/barrel.frag")

    composite_vert_src = read("GUI/ThreeDee/shaders/composite.vert")
    composite_frag_src = read("GUI/ThreeDee/shaders/composite.frag")

    # Programs
    prog_lighting = gl_helpers.link_program(vertex_shader_src, lighting_frag_src)
    prog_distortion = gl_helpers.link_program(vertex_shader_src, distortion_frag_src)
    prog_barrel = gl_helpers.link_program(vertex_shader_src, barrel_frag_src)
    prog_composite = gl_helpers.link_program(composite_vert_src, composite_frag_src)

    # Attribute locations (shared names across programs)
    def get_attribs(pid):
        a_pos = glGetAttribLocation(pid, b"in_vert")
        a_uv = glGetAttribLocation(pid, b"in_uv")
        return a_pos, a_uv

    attr_lighting = get_attribs(prog_lighting)
    attr_distortion = get_attribs(prog_distortion)
    attr_barrel = get_attribs(prog_barrel)
    attr_composite = get_attribs(prog_composite)

    quad = gl_helpers.FullscreenQuad()

    # === Textures/FBOs ===
    # GUI texture to be uploaded every frame
    tex_gui = gl_helpers.create_rgba_texture(w, h)

    # 3D render target (color+depth) — you can render with raw GL later if needed
    fbo_3d, tex_3d, depth_rb_3d = gl_helpers.create_fbo_with_color_depth(w, h)

    # Intermediate passes
    fbo_pass1, tex_pass1 = gl_helpers.create_fbo_with_color(w, h)
    fbo_pass2, tex_pass2 = gl_helpers.create_fbo_with_color(w, h)
    fbo_pass3, tex_pass3 = gl_helpers.create_fbo_with_color(w, h)

    # === Notification system & Menu manager ===
    notification = Notification(font_size=24, display_time=2.5)
    manager = MenuManager(gui_surface, query, notification, None, fbo_3d, tex_3d)

    loading_menu = MockLoadingMenu(gui_surface, manager)
    manager.register_menu("LoadingMenu", loading_menu)
    manager.switch_to("LoadingMenu")

    # === Uniform locations convenience ===
    def uloc(pid, name):
        loc = glGetUniformLocation(pid, name.encode('utf-8'))
        return loc

    # Distortion uniforms
    u_time_dist = uloc(prog_distortion, 'time')
    u_intensity = uloc(prog_distortion, 'intensity')
    u_tex_dist = uloc(prog_distortion, 'tex')

    # Lighting uniforms
    u_time_light = uloc(prog_lighting, 'time')
    u_tex_light = uloc(prog_lighting, 'tex')
    u_focus_pos = uloc(prog_lighting, 'focus_pos')
    u_focus_size = uloc(prog_lighting, 'focus_size')
    u_clip_pos = uloc(prog_lighting, 'clip_pos')
    u_clip_size = uloc(prog_lighting, 'clip_size')

    # Composite uniforms
    u_tex_gui = uloc(prog_composite, 'tex_gui')
    u_tex_3d = uloc(prog_composite, 'tex_3d')
    u_elem_pos = uloc(prog_composite, 'elem_pos')
    u_elem_size = uloc(prog_composite, 'elem_size')

    # Barrel uniforms
    u_tex_barrel = uloc(prog_barrel, 'tex')

    # Set some defaults
    glUseProgram(prog_distortion)
    glUniform1f(u_intensity, 0.2)
    glUseProgram(0)

    running = True
    last_time = pygame.time.get_ticks() / 1000.0

    while running:
        current_time = pygame.time.get_ticks() / 1000.0
        delta_time = current_time - last_time
        last_time = current_time

        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pass
            manager.handle_event(event)

        # Update
        if hasattr(manager.current_menu, 'update'):
            manager.current_menu.update(delta_time)

        # === Draw GUI to offscreen surface ===
        gui_surface.fill(StyleManager.DARK.bg_color)
        if manager.current_menu:
            manager.current_menu.render2d(gui_surface)
        notification.render(gui_surface)

        # === Upload GUI surface to tex_gui ===
        gui_rgba = pygame.Surface(screen_size, pygame.SRCALPHA)
        gui_rgba.blit(gui_surface, (0, 0))
        pixels = pygame.image.tostring(gui_rgba, 'RGBA', False)
        glBindTexture(GL_TEXTURE_2D, tex_gui)
        glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, w, h, GL_RGBA, GL_UNSIGNED_BYTE, pixels)
        glBindTexture(GL_TEXTURE_2D, 0)

        # === Render 3D into fbo_3d (optional) ===
        glBindFramebuffer(GL_FRAMEBUFFER, fbo_3d)
        glViewport(0, 0, w, h)
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        # TODO: Raw GL 3D drawing here (if you have any); keep GL2.0 calls only.
        glDisable(GL_DEPTH_TEST)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

        # === Pass 0: Composite GUI + 3D -> pass1 ===
        glBindFramebuffer(GL_FRAMEBUFFER, fbo_pass1)
        glViewport(0, 0, w, h)
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)

        glUseProgram(prog_composite)
        # Bind textures
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, tex_gui)
        glUniform1i(u_tex_gui, 0)

        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, tex_3d)
        glUniform1i(u_tex_3d, 1)

        # Element rect
        display3d_elem = manager.current_menu.get_display3d_element() if manager.current_menu else None
        if display3d_elem is not None:
            glUniform2f(u_elem_pos, display3d_elem.x / w, display3d_elem.y / h)
            glUniform2f(u_elem_size, display3d_elem.width / w, display3d_elem.height / h)
        else:
            glUniform2f(u_elem_pos, 0.0, 0.0)
            glUniform2f(u_elem_size, 0.0, 0.0)

        # Draw quad
        a_pos, a_uv = attr_composite
        quad.draw(prog_composite, a_pos, a_uv)

        # Unbind
        glBindTexture(GL_TEXTURE_2D, 0)
        glUseProgram(0)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

        # === Pass 1: Distortion (pass1 -> pass2) ===
        glBindFramebuffer(GL_FRAMEBUFFER, fbo_pass2)
        glViewport(0, 0, w, h)
        glClear(GL_COLOR_BUFFER_BIT)

        glUseProgram(prog_distortion)
        glUniform1f(u_time_dist, current_time)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, tex_pass1)
        glUniform1i(u_tex_dist, 0)
        a_pos, a_uv = attr_distortion
        quad.draw(prog_distortion, a_pos, a_uv)
        glBindTexture(GL_TEXTURE_2D, 0)
        glUseProgram(0)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

        # === Pass 2: Lighting (pass2 -> pass3) ===
        glBindFramebuffer(GL_FRAMEBUFFER, fbo_pass3)
        glViewport(0, 0, w, h)
        glClear(GL_COLOR_BUFFER_BIT)

        glUseProgram(prog_lighting)
        glUniform1f(u_time_light, current_time)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, tex_pass2)
        glUniform1i(u_tex_light, 0)

        # Focus / clip
        if getattr(manager, 'focus_manager', None) and manager.focus_manager.current_focus:
            f = manager.focus_manager.current_focus
            fx, fy = f.x, f.y
            if isinstance(f.parent_panel, ScrollingTableVertical):
                fy = fy - f.parent_panel.scroll_offset
            fw, fh = f.width, f.height
            glUniform2f(u_focus_pos, fx / w, fy / h)
            glUniform2f(u_focus_size, fw / w, fh / h)
            if hasattr(f, 'parent_panel'):
                px, py = f.parent_panel.x, f.parent_panel.y
                pw, ph = f.parent_panel.width, f.parent_panel.height
                glUniform2f(u_clip_pos, px / w, py / h)
                glUniform2f(u_clip_size, pw / w, ph / h)
            else:
                glUniform2f(u_clip_size, 0.0, 0.0)
        else:
            glUniform2f(u_focus_size, 0.0, 0.0)
            glUniform2f(u_clip_size, 0.0, 0.0)

        a_pos, a_uv = attr_lighting
        quad.draw(prog_lighting, a_pos, a_uv)
        glBindTexture(GL_TEXTURE_2D, 0)
        glUseProgram(0)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

        # === Pass 3: Barrel (pass3 -> default framebuffer) ===
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glViewport(0, 0, w, h)
        glClear(GL_COLOR_BUFFER_BIT)

        glUseProgram(prog_barrel)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, tex_pass3)
        glUniform1i(u_tex_barrel, 0)
        a_pos, a_uv = attr_barrel
        quad.draw(prog_barrel, a_pos, a_uv)
        glBindTexture(GL_TEXTURE_2D, 0)
        glUseProgram(0)

        # Swap
        pygame.display.flip()
        clock.tick(12)

    # Cleanup
    pygame.quit()


if __name__ == "__main__":
    main()
