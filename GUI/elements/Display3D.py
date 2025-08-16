import numpy as np
from GUI.elements.Element import Element
from pathlib import Path
from pyrr import Matrix44
from GUI.ThreeDee.loader import ModelLoader  


class Display3D(Element):
    def __init__(self, x, y, width, height, manager,
                 ctx, fbo_3d, tex_3d,
                 model_path, vertex_shader_path, fragment_shader_path,
                 parent_panel=None, selectable=True, neighbors=None, layer=0,
                 target_size=1.0):
        """
        3D display element that renders into its own framebuffer for GPU compositing.

        :param ctx: ModernGL context
        :param fbo_3d: ModernGL framebuffer for offscreen 3D rendering
        :param tex_3d: ModernGL texture linked to fbo_3d
        """
        super().__init__(x, y, width, height, manager, parent_panel, selectable, neighbors, layer)

        self.ctx = ctx
        self.fbo_3d = fbo_3d
        self.tex_3d = tex_3d

        # Load the 3D model
        self.model = ModelLoader(
            ctx,
            model_path=Path(model_path),
            vertex_shader_path=Path(vertex_shader_path),
            fragment_shader_path=Path(fragment_shader_path),
            target_size=target_size
        )

        # Rotation angle for demo
        self.angle = 0.0

    def release(self):
        """
        Clear 3D framebuffer and release the model's GPU resources.
        Call this when removing the element or shutting down.
        """
        # Clear the framebuffer
        self.fbo_3d.use()
        self.ctx.clear(0.0, 0.0, 0.0, 0.0, 1.0)

        # Release model resources
        if hasattr(self, 'model'):
            self.model.release()

    def render3d(self):
        """
        Instead of drawing to the Pygame screen, render directly to fbo_3d.
        The compositing will be handled later in the main loop.
        """
        self.fbo_3d.use()
        self.ctx.viewport = (0, 0, self.fbo_3d.width, self.fbo_3d.height)
        # moderngl.clear: (r, g, b, a=1.0, depth=1.0)
        self.ctx.clear(0.0, 0.0, 0.0, 0.0, 1.0)

        self.ctx.enable(self.ctx.DEPTH_TEST)

        projection = Matrix44.perspective_projection(45.0, self.width / self.height, 0.1, 100.0)
        view = Matrix44.look_at(
            eye=[0, 0, 3],
            target=[0, 0, 0],
            up=[0, 1, 0]
        )
        model_matrix = Matrix44.from_y_rotation(np.radians(self.angle))

        self.model.draw({
            "mvp": (projection * view * model_matrix),
            "model": model_matrix
        })

        self.angle = (self.angle + 3.0) % 360
        if self.angle % 360 > 90 and self.angle % 360 < 270:
            self.angle += 5

    def render(self,screen):
        pass

    def on_press(self):
        pass
