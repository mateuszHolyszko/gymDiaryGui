import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from GUI.elements.Element import Element
from pathlib import Path
from pyrr import Matrix44
from GUI.ThreeDee.loader import ModelLoader


class Display3D(Element):
    def __init__(self, x, y, width, height, manager,
                 model_path, vertex_shader_path, fragment_shader_path,
                 parent_panel=None, selectable=True, neighbors=None, layer=0,
                 target_size=1.0):
        """
        3D display element with its own framebuffer (FBO).
        Uses raw OpenGL 2.0 (PyOpenGL).
        """
        super().__init__(x, y, width, height, manager, parent_panel, selectable, neighbors, layer)

        # --- Create FBO + Texture ---
        self.fbo = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, self.fbo)

        # Create texture for color attachment
        self.tex = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.tex)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0,
                     GL_RGBA, GL_UNSIGNED_BYTE, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0,
                               GL_TEXTURE_2D, self.tex, 0)

        # Create depth buffer
        self.depth_rb = glGenRenderbuffers(1)
        glBindRenderbuffer(GL_RENDERBUFFER, self.depth_rb)
        glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT, int(width), int(height))
        glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT,
                                  GL_RENDERBUFFER, self.depth_rb)

        # Check FBO
        if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
            raise RuntimeError("Framebuffer is not complete!")

        glBindFramebuffer(GL_FRAMEBUFFER, 0)

        # Load model
        self.model = ModelLoader(
            model_path=Path(model_path),
            vertex_shader_path=Path(vertex_shader_path),
            fragment_shader_path=Path(fragment_shader_path),
            target_size=target_size
        )

        # Rotation angle
        self.angle = 0.0

    def release(self):
        """Release GPU resources"""
        if hasattr(self, "model"):
            self.model.release()
        if hasattr(self, "tex"):
            glDeleteTextures([self.tex])
        if hasattr(self, "depth_rb"):
            glDeleteRenderbuffers(1, [self.depth_rb])
        if hasattr(self, "fbo"):
            glDeleteFramebuffers(1, [self.fbo])

    def render3d(self):
        """Render into the offscreen framebuffer (FBO)."""
        glBindFramebuffer(GL_FRAMEBUFFER, self.fbo)
        glViewport(0, 0, self.width, self.height)

        glEnable(GL_DEPTH_TEST)
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Projection + View + Model
        projection = Matrix44.perspective_projection(45.0, self.width / self.height, 0.1, 100.0)
        view = Matrix44.look_at(
            eye=[0, 0, 3],
            target=[0, 0, 0],
            up=[0, 1, 0]
        )
        model_matrix = Matrix44.from_y_rotation(np.radians(self.angle))

        self.model.draw({
            "mvp": (projection * view * model_matrix).astype(np.float32),
            "model": model_matrix.astype(np.float32)
        })

        glBindFramebuffer(GL_FRAMEBUFFER, 0)

        # Animate
        self.angle = (self.angle + 3.0) % 360
        if 90 < self.angle % 360 < 270:
            self.angle += 5

    def render(self, screen):
        #2d portion
        pass

    def on_press(self):
        pass
