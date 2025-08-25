# gl_helpers.py  (GLES2)
import numpy as np
import ctypes
import os
import sys
# Try to use GLES2 first, fall back to desktop OpenGL if not available
try:
    # Try to set up Angle for Windows GLES support
    os.environ['PYOPENGL_PLATFORM'] = 'angle'
    from OpenGL import GLES2 as gl
    USING_GLES = True
    print("Using OpenGL ES 2.0 with Angle")
except (ImportError, AttributeError, AssertionError) as e:
    try:
        # Fall back to desktop OpenGL
        del os.environ['PYOPENGL_PLATFORM']  # Remove Angle setting
        from OpenGL.GL import *
        import OpenGL.GL as gl
        USING_GLES = False
        print("Using desktop OpenGL (fallback)")
    except ImportError:
        print("No OpenGL implementation available")
        sys.exit(1)

def compile_shader(src: str, shader_type) -> int:
    sid = gl.glCreateShader(shader_type)
    gl.glShaderSource(sid, src)
    gl.glCompileShader(sid)
    status = gl.glGetShaderiv(sid, gl.GL_COMPILE_STATUS)
    if status != gl.GL_TRUE:
        log = gl.glGetShaderInfoLog(sid).decode()
        raise RuntimeError(f"Shader compile error ({shader_type}):\n{log}")
    return sid

def link_program(vs_src: str, fs_src: str) -> int:
    vs = compile_shader(vs_src, gl.GL_VERTEX_SHADER)
    fs = compile_shader(fs_src, gl.GL_FRAGMENT_SHADER)
    pid = gl.glCreateProgram()
    gl.glAttachShader(pid, vs)
    gl.glAttachShader(pid, fs)
    gl.glLinkProgram(pid)
    status = gl.glGetProgramiv(pid, gl.GL_LINK_STATUS)
    if status != gl.GL_TRUE:
        log = gl.glGetProgramInfoLog(pid).decode()
        raise RuntimeError(f"Program link error:\n{log}")
    gl.glDeleteShader(vs)
    gl.glDeleteShader(fs)
    return pid

def create_rgba_texture(w: int, h: int, *, filter_linear=False, data=None) -> int:
    tex = gl.glGenTextures(1)
    gl.glBindTexture(gl.GL_TEXTURE_2D, tex)
    filt = gl.GL_LINEAR if filter_linear else gl.GL_NEAREST
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, filt)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, filt)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_CLAMP_TO_EDGE)
    gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_CLAMP_TO_EDGE)
    gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, w, h, 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE,
                    data if data is not None else None)
    gl.glBindTexture(gl.GL_TEXTURE_2D, 0)
    return tex

def create_fbo_with_color(w: int, h: int) -> tuple[int, int]:
    color_tex = create_rgba_texture(w, h)
    fbo = gl.glGenFramebuffers(1)
    gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, fbo)
    gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER, gl.GL_COLOR_ATTACHMENT0, gl.GL_TEXTURE_2D, color_tex, 0)
    status = gl.glCheckFramebufferStatus(gl.GL_FRAMEBUFFER)
    if status != gl.GL_FRAMEBUFFER_COMPLETE:
        raise RuntimeError(f"FBO incomplete (color only): {hex(status)}")
    gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)
    return fbo, color_tex

def create_fbo_with_color_depth(w: int, h: int) -> tuple[int, int, int]:
    color_tex = create_rgba_texture(w, h)
    depth_rb = gl.glGenRenderbuffers(1)
    gl.glBindRenderbuffer(gl.GL_RENDERBUFFER, depth_rb)
    # GLES2-guaranteed depth format:
    gl.glRenderbufferStorage(gl.GL_RENDERBUFFER, gl.GL_DEPTH_COMPONENT16, w, h)

    fbo = gl.glGenFramebuffers(1)
    gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, fbo)
    gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER, gl.GL_COLOR_ATTACHMENT0, gl.GL_TEXTURE_2D, color_tex, 0)
    gl.glFramebufferRenderbuffer(gl.GL_FRAMEBUFFER, gl.GL_DEPTH_ATTACHMENT, gl.GL_RENDERBUFFER, depth_rb)

    status = gl.glCheckFramebufferStatus(gl.GL_FRAMEBUFFER)
    if status != gl.GL_FRAMEBUFFER_COMPLETE:
        raise RuntimeError(f"FBO incomplete (color+depth): {hex(status)}")

    gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)
    gl.glBindRenderbuffer(gl.GL_RENDERBUFFER, 0)
    return fbo, color_tex, depth_rb

class FullscreenQuad:
    def __init__(self):
        verts = np.array([
            # x,   y,   u,  v
            -1.0,  1.0, 0.0, 1.0,
            -1.0, -1.0, 0.0, 0.0,
             1.0,  1.0, 1.0, 1.0,
             1.0, -1.0, 1.0, 0.0,
        ], dtype=np.float32)

        self.vbo = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, verts.nbytes, verts, gl.GL_STATIC_DRAW)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
        self.stride = 4 * 4  # bytes

    def draw(self, program, a_pos, a_uv):
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)

        gl.glEnableVertexAttribArray(a_pos)
        gl.glVertexAttribPointer(a_pos, 2, gl.GL_FLOAT, gl.GL_FALSE, self.stride, ctypes.c_void_p(0))

        gl.glEnableVertexAttribArray(a_uv)
        gl.glVertexAttribPointer(a_uv, 2, gl.GL_FLOAT, gl.GL_FALSE, self.stride, ctypes.c_void_p(8))

        gl.glDrawArrays(gl.GL_TRIANGLE_STRIP, 0, 4)

        gl.glDisableVertexAttribArray(a_pos)
        gl.glDisableVertexAttribArray(a_uv)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
