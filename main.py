import pygame
import numpy as np
from pygame.locals import DOUBLEBUF, OPENGL
from OpenGL.GL import *
from OpenGL.GL.shaders import compileShader, compileProgram

import gl_helpers
from GUI.MenuManager import MenuManager
from GUI.style import StyleManager
from GUI.menus.MockLoadingMenu import MockLoadingMenu
from GUI.Notifications import Notification

from workout_db_r.Database import Database
from workout_db_r.Query import Query
from GUI.elements.Display3D import Display3D


def main():
    # Init DB
    db = Database()
    query = Query(db)

    # Init pygame + OpenGL context
    pygame.init()
    screen_size = (800, 480)
    
    # Try to create an OpenGL ES context if available
    try:
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 2)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 0)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, 
                                      pygame.GL_CONTEXT_PROFILE_ES)
        pygame.display.set_mode(screen_size, DOUBLEBUF | OPENGL)
    except:
        # Fallback to regular OpenGL
        pygame.display.set_mode(screen_size, DOUBLEBUF | OPENGL)
    
    pygame.display.set_caption("Activity Tracker (GL ES 2.0)")
    clock = pygame.time.Clock()

    w, h = screen_size
    glViewport(0, 0, w, h)
    glDisable(GL_DEPTH_TEST)

    # Offscreen GUI surface
    gui_surface = pygame.Surface(screen_size, pygame.SRCALPHA)

    # === Load shaders (GLSL ES 1.00) ===
    def read(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    # Load modified shaders for GLSL ES
    vertex_shader_src = read("GUI/Distortions/distortion.vert")  # Modified for ES
    distortion_frag_src = read("GUI/Distortions/distortion.frag")  # Modified for ES
    lighting_frag_src = read("GUI/Distortions/lighting.frag")  # Modified for ES
    barrel_frag_src = read("GUI/Distortions/barrel.frag")  # Add barrel shader

    # Simple texture copy shader for ES 2.0
    COPY_VERT = """
    attribute vec2 in_vert;
    attribute vec2 in_uv;
    varying vec2 uv;
    void main() {
        gl_Position = vec4(in_vert, 0.0, 1.0);
        uv = in_uv;
    }
    """

    COPY_FRAG = """
    precision highp float;
    varying vec2 uv;
    uniform sampler2D tex;
    void main() {
        gl_FragColor = texture2D(tex, uv);
    }
    """
    UNIVERSAL_VERT = """
    attribute vec2 in_vert;
    attribute vec2 in_uv;
    varying vec2 uv;
    void main() {
        gl_Position = vec4(in_vert, 0.0, 1.0);
        uv = in_uv;
    }
    """

    # Compile shaders with proper types
    def compile_shader_program(vertex_src, fragment_src):
        vertex_shader = compileShader(vertex_src, GL_VERTEX_SHADER)
        fragment_shader = compileShader(fragment_src, GL_FRAGMENT_SHADER)
        return compileProgram(vertex_shader, fragment_shader)

    prog_distortion = compile_shader_program(UNIVERSAL_VERT, distortion_frag_src)
    prog_lighting = compile_shader_program(UNIVERSAL_VERT, lighting_frag_src)
    prog_barrel = compile_shader_program(UNIVERSAL_VERT, barrel_frag_src)
    prog_copy = compile_shader_program(UNIVERSAL_VERT, COPY_FRAG)

    # Attribute locations
    def get_attribs(pid):
        a_pos = glGetAttribLocation(pid, "in_vert")
        a_uv = glGetAttribLocation(pid, "in_uv")
        return a_pos, a_uv

    attr_distortion = get_attribs(prog_distortion)
    attr_lighting = get_attribs(prog_lighting)
    attr_barrel = get_attribs(prog_barrel)
    attr_copy = get_attribs(prog_copy)  # Copy program attributes

    quad = gl_helpers.FullscreenQuad()

    # === Textures/FBOs ===
    tex_gui = gl_helpers.create_rgba_texture(w, h)
    tex_3d = gl_helpers.create_rgba_texture(w, h)

    # Create FBOs for the rendering pipeline
    fbo_pass1, tex_pass1 = gl_helpers.create_fbo_with_color(w, h)
    fbo_distortion, tex_distortion = gl_helpers.create_fbo_with_color(w, h)
    fbo_pass2, tex_pass2 = gl_helpers.create_fbo_with_color(w, h)

    # Uniforms
    def uloc(pid, name):
        return glGetUniformLocation(pid, name)

    u_time_dist = uloc(prog_distortion, "time")
    u_tex_dist = uloc(prog_distortion, "tex")
    u_intensity = uloc(prog_distortion, "intensity")

    u_time_light = uloc(prog_lighting, "time")
    u_tex_light = uloc(prog_lighting, "tex")
    
    u_time_barrel = uloc(prog_barrel, "time")
    u_tex_barrel = uloc(prog_barrel, "tex")

    u_tex_copy = uloc(prog_copy, "tex")  # Copy program uniform

    # Defaults
    glUseProgram(prog_distortion)
    glUniform1f(u_intensity, 0.2)
    glUseProgram(0)

    # === Notifications + Menus ===
    notification = Notification(font_size=24, display_time=2.5)
    manager = MenuManager(gui_surface, query, notification, None, None, None)

    loading_menu = MockLoadingMenu(gui_surface, manager)
    manager.register_menu("LoadingMenu", loading_menu)
    manager.switch_to("LoadingMenu")

    running = True
    last_time = pygame.time.get_ticks() / 1000.0

    # --- Main loop ---
    while running:
        current_time = pygame.time.get_ticks() / 1000.0
        delta_time = current_time - last_time
        last_time = current_time

        # --- Events ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            manager.handle_event(event)

        # --- Update GUI ---
        if hasattr(manager.current_menu, "update"):
            manager.current_menu.update(delta_time)

        gui_surface.fill(StyleManager.DARK.bg_color)

        # Render GUI elements to pygame surface
        if manager.current_menu:
            manager.current_menu.render2d(gui_surface)
        notification.render(gui_surface)

        # --- Upload GUI surface to GPU ---
        gui_data = pygame.image.tostring(gui_surface, "RGBA", True)
        glBindTexture(GL_TEXTURE_2D, tex_gui)
        glTexSubImage2D(GL_TEXTURE_2D, 0, 0, 0, w, h, GL_RGBA, GL_UNSIGNED_BYTE, gui_data)
        glBindTexture(GL_TEXTURE_2D, 0)

        # --- Render all Display3D elements into tex_3d ---
        glDisable(GL_DEPTH_TEST)
        if manager.current_menu.has_3d() == False:
            # Clear the 3D texture to transparent using a TEMPORARY FBO
            temp_fbo = glGenFramebuffers(1)
            glBindFramebuffer(GL_FRAMEBUFFER, temp_fbo)
            glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, tex_3d, 0)
            glClearColor(0.0, 0.0, 0.0, 0.0)  # Transparent
            glClear(GL_COLOR_BUFFER_BIT)
            glBindFramebuffer(GL_FRAMEBUFFER, 0)
            glDeleteFramebuffers(1, [temp_fbo])
        
        for panels in manager.current_menu.panels:
            for element in panels.elements:
                if isinstance(element, Display3D):
                    viewport = (0, 0, element.width, element.height)
                    element.render_3d(target_tex=tex_3d, viewport=viewport)
                    flag_3d_used = True

        # --- Pass 1: Composite GUI + 3D into tex_pass1 ---
        glDisable(GL_DEPTH_TEST)
        glBindFramebuffer(GL_FRAMEBUFFER, fbo_pass1)
        glViewport(0, 0, w, h)
        #glClear(GL_COLOR_BUFFER_BIT)
        
        # Enable blending for alpha compositing
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # First draw the GUI (full screen)
        glUseProgram(prog_copy)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, tex_gui)
        glUniform1i(u_tex_copy, 0)
        quad.draw(prog_copy, *attr_copy)
        
        # Then overlay the 3D content (with alpha blending)
        glBindTexture(GL_TEXTURE_2D, tex_3d)
        glUniform1i(u_tex_copy, 0)
        quad.draw(prog_copy, *attr_copy)
        
        glDisable(GL_BLEND)
        glBindTexture(GL_TEXTURE_2D, 0)
        glUseProgram(0)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

        # --- Pass 2: Distortion (tex_pass1 → tex_distortion) ---
        glBindFramebuffer(GL_FRAMEBUFFER, fbo_distortion)
        glViewport(0, 0, w, h)
        glClear(GL_COLOR_BUFFER_BIT)

        glUseProgram(prog_distortion)
        glUniform1f(u_time_dist, current_time)
        glUniform1f(u_intensity, 0.2)  # Set distortion intensity
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, tex_pass1)
        glUniform1i(u_tex_dist, 0)
        quad.draw(prog_distortion, *attr_distortion)

        glBindTexture(GL_TEXTURE_2D, 0)
        glUseProgram(0)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

        # --- Pass 3: Lighting (tex_distortion → tex_pass2) ---
        glBindFramebuffer(GL_FRAMEBUFFER, fbo_pass2)
        glViewport(0, 0, w, h)
        glClear(GL_COLOR_BUFFER_BIT)

        glUseProgram(prog_lighting)
        glUniform1f(u_time_light, current_time)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, tex_distortion)  # Use distorted texture as input
        glUniform1i(u_tex_light, 0)
        quad.draw(prog_lighting, *attr_lighting)

        glBindTexture(GL_TEXTURE_2D, 0)
        glUseProgram(0)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

        # --- Pass 4: Barrel Distortion (tex_pass2 → screen) ---
        glViewport(0, 0, w, h)

        glUseProgram(prog_barrel)
        glUniform1f(u_time_barrel, current_time)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, tex_pass2)
        glUniform1i(u_tex_barrel, 0)
        quad.draw(prog_barrel, *attr_barrel)

        glBindTexture(GL_TEXTURE_2D, 0)
        glUseProgram(0)

        # # --- Debug Overlay: 3D texture in bottom-left ---
        # draw_debug_tex(tex_pass2, quad, prog_barrel, attr_barrel, w, h)

        # Swap buffers
        pygame.display.flip()
        clock.tick(12)


# --- Debug Overlay: draw tex_3d in bottom-left corner ---
def draw_debug_tex(tex, quad, shader, attr, screen_w, screen_h, dbg_w=200, dbg_h=150):
    # Save previous viewport
    prev_viewport = glGetIntegerv(GL_VIEWPORT)

    # Set viewport to a small corner
    glViewport(0, 0, dbg_w, dbg_h)
    glDisable(GL_DEPTH_TEST)
    glUseProgram(shader)
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, tex)
    glUniform1i(glGetUniformLocation(shader, "tex"), 0)
    quad.draw(shader, *attr)
    glBindTexture(GL_TEXTURE_2D, 0)
    glUseProgram(0)

    # Restore previous viewport
    glViewport(*prev_viewport)


if __name__ == "__main__":
    main()