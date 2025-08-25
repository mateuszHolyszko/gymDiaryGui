import pygame
import numpy as np
from pygame.locals import DOUBLEBUF, OPENGL
from OpenGL.GL import *
from OpenGL.GL.shaders import compileShader, compileProgram

import gl_helpers
from GUI.elements.Display3D import Display3D

def debug_main():
    # Init pygame + OpenGL context
    pygame.init()
    screen_size = (800, 480)
    pygame.display.set_mode(screen_size, DOUBLEBUF | OPENGL)
    print("Using OpenGL context")
    
    clock = pygame.time.Clock()
    w, h = screen_size
    glViewport(0, 0, w, h)
    
    print(f"OpenGL Version: {glGetString(GL_VERSION)}")
    print(f"OpenGL Vendor: {glGetString(GL_VENDOR)}")
    print(f"OpenGL Renderer: {glGetString(GL_RENDERER)}")

    # === Create central FBO for 3D rendering ===
    fbo_3d = glGenFramebuffers(1)
    tex_3d = glGenTextures(1)
    
    glBindFramebuffer(GL_FRAMEBUFFER, fbo_3d)
    glBindTexture(GL_TEXTURE_2D, tex_3d)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, None)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, tex_3d, 0)
    
    # Create depth buffer
    depth_rb = glGenRenderbuffers(1)
    glBindRenderbuffer(GL_RENDERBUFFER, depth_rb)
    glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT16, w, h)
    glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, depth_rb)
    
    # Check FBO status
    status = glCheckFramebufferStatus(GL_FRAMEBUFFER)
    if status != GL_FRAMEBUFFER_COMPLETE:
        print(f"3D FBO is not complete! Status: {status}")
        return
    else:
        print("3D FBO created successfully")
    
    glBindFramebuffer(GL_FRAMEBUFFER, 0)
    glBindTexture(GL_TEXTURE_2D, 0)

    # Create debug shader
    debug_vert_src = """
    attribute vec2 in_vert;
    attribute vec2 in_uv;
    varying vec2 v_uv;
    
    void main() {
        gl_Position = vec4(in_vert, 0.0, 1.0);
        v_uv = in_uv;
    }
    """
    
    debug_frag_src = """
    precision mediump float;
    varying vec2 v_uv;
    uniform sampler2D tex;
    
    void main() {
        vec4 color = texture2D(tex, v_uv);
        // Make alpha areas bright red for visibility
        if (color.a < 0.1) {
            gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0);
        } else {
            gl_FragColor = color;
        }
    }
    """
    
    # Compile debug shader
    def compile_shader_program(vertex_src, fragment_src):
        vertex_shader = compileShader(vertex_src, GL_VERTEX_SHADER)
        fragment_shader = compileShader(fragment_src, GL_FRAGMENT_SHADER)
        return compileProgram(vertex_shader, fragment_shader)
    
    prog_debug = compile_shader_program(debug_vert_src, debug_frag_src)
    u_tex_debug = glGetUniformLocation(prog_debug, "tex")
    
    def get_attribs(pid):
        a_pos = glGetAttribLocation(pid, "in_vert")
        a_uv = glGetAttribLocation(pid, "in_uv")
        return a_pos, a_uv
    
    attr_debug = get_attribs(prog_debug)
    quad = gl_helpers.FullscreenQuad()

    # Create test 3D element
    test_element = Display3D(
        x=100, y=100, width=200, height=200,
        manager=None,
        model_path="GUI\ThreeDee\models\Mat.obj",  # Replace with actual path
        vertex_shader_path="GUI\ThreeDee\shaders\\basic.vert",  # Replace
        fragment_shader_path="GUI\ThreeDee\shaders\\basic.frag",  # Replace
        target_size=1.0
    )

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        # Clear screen
        glClearColor(0.2, 0.2, 0.2, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)

        # Render 3D content to FBO
        test_element.render3d(fbo_3d, w, h)

        # Draw the 3D texture directly to screen
        glUseProgram(prog_debug)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, tex_3d)
        glUniform1i(u_tex_debug, 0)
        
        a_pos, a_uv = attr_debug
        quad.draw(prog_debug, a_pos, a_uv)
        
        glBindTexture(GL_TEXTURE_2D, 0)
        glUseProgram(0)

        # Draw debug info
        pygame.display.set_caption(f"3D Debug - Press ESC to exit - Angle: {test_element.angle:.1f}")

        # Swap buffers
        pygame.display.flip()
        clock.tick(60)

    # Cleanup
    test_element.release()
    glDeleteFramebuffers(1, [fbo_3d])
    glDeleteTextures(1, [tex_3d])
    glDeleteRenderbuffers(1, [depth_rb])
    pygame.quit()

if __name__ == "__main__":
    debug_main()