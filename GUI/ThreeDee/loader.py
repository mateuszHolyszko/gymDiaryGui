import moderngl
import numpy as np
from pathlib import Path
import trimesh  # pip install trimesh


class ModelLoader:
    def __init__(self, ctx: moderngl.Context, model_path: Path, vertex_shader_path: Path, fragment_shader_path: Path, target_size: float = 1.0):
        """
        Loads a model and compiles shaders from files.
        Stores VAO, VBO, and shader program for later use.

        :param ctx: ModernGL context
        :param model_path: Path to the model file
        :param vertex_shader_path: Path to vertex shader file
        :param fragment_shader_path: Path to fragment shader file
        :param target_size: Desired normalized size
        """
        self.ctx = ctx
        self.model_path = Path(model_path)
        self.vertex_shader_path = Path(vertex_shader_path)
        self.fragment_shader_path = Path(fragment_shader_path)

        if not self.model_path.exists():
            raise FileNotFoundError(f"Model file not found: {self.model_path}")
        if not self.vertex_shader_path.exists():
            raise FileNotFoundError(f"Vertex shader not found: {self.vertex_shader_path}")
        if not self.fragment_shader_path.exists():
            raise FileNotFoundError(f"Fragment shader not found: {self.fragment_shader_path}")

        self._load_mesh(target_size)
        self._load_shaders()

    def _load_mesh(self, target_size: float):
        """Load and normalize mesh, upload to GPU."""
        mesh = trimesh.load_mesh(self.model_path, force='mesh')

        # Center and scale
        mesh.apply_translation(-mesh.centroid)
        scale_factor = target_size / np.linalg.norm(mesh.bounding_box.extents)
        mesh.apply_scale(scale_factor)

        # Prepare vertex data (pos + normal)
        vertices = np.array(mesh.vertices, dtype='f4')
        normals = np.array(mesh.vertex_normals, dtype='f4')
        faces = np.array(mesh.faces, dtype='i4')

        data = np.hstack([
            vertices[faces].reshape(-1, 3),
            normals[faces].reshape(-1, 3)
        ]).astype('f4')

        self.vbo = self.ctx.buffer(data.tobytes())
        self.vertex_count = len(data)

    def _load_shaders(self):
        """Load shaders from files."""
        vertex_code = self.vertex_shader_path.read_text()
        fragment_code = self.fragment_shader_path.read_text()
        self.program = self.ctx.program(
            vertex_shader=vertex_code,
            fragment_shader=fragment_code
        )
        self.vao = self.ctx.simple_vertex_array(self.program, self.vbo, 'in_vert', 'in_norm')

    def release(self):
        """Free GPU resources."""
        if hasattr(self, 'vao'):
            self.vao.release()
        if hasattr(self, 'vbo'):
            self.vbo.release()
        if hasattr(self, 'program'):
            self.program.release()

    def draw(self, uniforms: dict = None):
        """
        Draws the model using current shader program.
        This is called by the *element* that owns the scene.

        :param uniforms: Dict of uniform_name -> numpy array / value
        """
        if uniforms:
            for name, value in uniforms.items():
                if name in self.program:
                    if hasattr(value, "astype"):
                        self.program[name].write(value.astype('f4').tobytes())
                    else:
                        self.program[name].value = value

        self.vao.render()
