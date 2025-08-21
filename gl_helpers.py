from OpenGL.GL import *
import numpy as np

def compile_shader( src: str, shader_type) -> int:
    sid = glCreateShader(shader_type)
    glShaderSource(sid, src)
    glCompileShader(sid)
    status = glGetShaderiv(sid, GL_COMPILE_STATUS)
    if status != GL_TRUE:
        log = glGetShaderInfoLog(sid).decode()
        raise RuntimeError(f"Shader compile error ({shader_type}):\n{log}")
    return sid


def link_program( vs_src: str, fs_src: str) -> int:
    vs = compile_shader(vs_src, GL_VERTEX_SHADER)
    fs = compile_shader(fs_src, GL_FRAGMENT_SHADER)
    pid = glCreateProgram()
    glAttachShader(pid, vs)
    glAttachShader(pid, fs)
    glLinkProgram(pid)
    status = glGetProgramiv(pid, GL_LINK_STATUS)
    if status != GL_TRUE:
        log = glGetProgramInfoLog(pid).decode()
        raise RuntimeError(f"Program link error:\n{log}")
    # Shaders can be deleted after linking
    glDeleteShader(vs)
    glDeleteShader(fs)
    return pid


def create_rgba_texture(w: int, h: int, *, filter_linear=False, data=None) -> int:
    tex = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex)
    minf = GL_LINEAR if filter_linear else GL_NEAREST
    magf = GL_LINEAR if filter_linear else GL_NEAREST
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, minf)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, magf)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE,
                data if data is not None else None)
    glBindTexture(GL_TEXTURE_2D, 0)
    return tex


def create_fbo_with_color(w: int, h: int) -> tuple[int, int]:
    color_tex = create_rgba_texture(w, h)
    fbo = glGenFramebuffers(1)
    glBindFramebuffer(GL_FRAMEBUFFER, fbo)
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, color_tex, 0)
    status = glCheckFramebufferStatus(GL_FRAMEBUFFER)
    if status != GL_FRAMEBUFFER_COMPLETE:
        raise RuntimeError(f"FBO incomplete (color only): {hex(status)}")
    glBindFramebuffer(GL_FRAMEBUFFER, 0)
    return fbo, color_tex


def create_fbo_with_color_depth(w: int, h: int) -> tuple[int, int, int]:
    color_tex = create_rgba_texture(w, h)
    depth_rb = glGenRenderbuffers(1)
    glBindRenderbuffer(GL_RENDERBUFFER, depth_rb)
    glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT24, w, h)

    fbo = glGenFramebuffers(1)
    glBindFramebuffer(GL_FRAMEBUFFER, fbo)
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, color_tex, 0)
    glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, depth_rb)

    status = glCheckFramebufferStatus(GL_FRAMEBUFFER)
    if status != GL_FRAMEBUFFER_COMPLETE:
        raise RuntimeError(f"FBO incomplete (color+depth): {hex(status)}")

    glBindFramebuffer(GL_FRAMEBUFFER, 0)
    glBindRenderbuffer(GL_RENDERBUFFER, 0)
    return fbo, color_tex, depth_rb
    
from OpenGL.GL import *

class FullscreenQuad:
    def __init__(self):
        verts = np.array([
            # x,   y,   u,  v
            -1.0,  1.0, 0.0, 1.0,
            -1.0, -1.0, 0.0, 0.0,
             1.0,  1.0, 1.0, 1.0,
             1.0, -1.0, 1.0, 0.0,
        ], dtype=np.float32)

        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, verts.nbytes, verts, GL_STATIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

        self.stride = 4 * 4  # 4 floats per vertex (x,y,u,v), 4 bytes each

    def draw(self, program, a_pos, a_uv):
        """Draws fullscreen quad with given program + attribute locations."""
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)

        # Position (x, y)
        glEnableVertexAttribArray(a_pos)
        glVertexAttribPointer(
            a_pos, 2, GL_FLOAT, GL_FALSE, self.stride, ctypes.c_void_p(0)
        )

        # UV (u, v)
        glEnableVertexAttribArray(a_uv)
        glVertexAttribPointer(
            a_uv, 2, GL_FLOAT, GL_FALSE, self.stride, ctypes.c_void_p(8)
        )

        # Draw quad as triangle strip (4 verts)
        glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)

        # Cleanup
        glDisableVertexAttribArray(a_pos)
        glDisableVertexAttribArray(a_uv)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
