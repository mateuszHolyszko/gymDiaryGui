from OpenGL.GL import *
import numpy as np
from pathlib import Path
import trimesh

from gl_helpers import link_program  

class ModelLoader:
    def __init__(self, model_path: Path, vertex_shader_path: Path, fragment_shader_path: Path, target_size: float = 1.0):
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
        """Load and normalize mesh, upload to GPU as VBO."""
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

        self.vertex_count = len(data)

        # Upload VBO
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, data.nbytes, data, GL_STATIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def _load_shaders(self):
        """Compile and link shaders."""
        vs_src = self.vertex_shader_path.read_text()
        fs_src = self.fragment_shader_path.read_text()
        self.program = link_program(vs_src, fs_src)

        # Cache attribute/uniform locations
        self.attr_vert = glGetAttribLocation(self.program, "in_vert")
        self.attr_norm = glGetAttribLocation(self.program, "in_norm")

        self.uniform_locs = {}
        # optional: cache frequently used uniforms
        for name in ["model", "view", "proj", "color", "light_dir"]:
            loc = glGetUniformLocation(self.program, name)
            if loc != -1:
                self.uniform_locs[name] = loc

    def release(self):
        """Free GPU resources."""
        if hasattr(self, 'program'):
            glDeleteProgram(self.program)
        if hasattr(self, 'vbo'):
            glDeleteBuffers(1, [self.vbo])

    def draw(self, uniforms: dict = None):
        """Draw the model with given uniforms (OpenGL 2.0 compatible)."""
        glUseProgram(self.program)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)

        stride = 6 * 4  # 6 floats per vertex (pos+norm)
        offset_pos = ctypes.c_void_p(0)
        offset_norm = ctypes.c_void_p(12)  # 3 floats * 4 bytes

        # Enable and set vertex attributes
        if self.attr_vert != -1:
            glEnableVertexAttribArray(self.attr_vert)
            glVertexAttribPointer(self.attr_vert, 3, GL_FLOAT, GL_FALSE, stride, offset_pos)
        if self.attr_norm != -1:
            glEnableVertexAttribArray(self.attr_norm)
            glVertexAttribPointer(self.attr_norm, 3, GL_FLOAT, GL_FALSE, stride, offset_norm)

        # Upload uniforms
        if uniforms:
            for name, value in uniforms.items():
                loc = self.uniform_locs.get(name)
                if loc is None:  # cache miss → query and store
                    loc = glGetUniformLocation(self.program, name)
                    self.uniform_locs[name] = loc

                if loc != -1:
                    if isinstance(value, (float, int)):
                        glUniform1f(loc, float(value))
                    else:
                        arr = np.array(value, dtype=np.float32)
                        if arr.shape == (3,):
                            glUniform3fv(loc, 1, arr)
                        elif arr.shape == (4, 4):
                            glUniformMatrix4fv(loc, 1, GL_FALSE, arr)

        # Draw the model
        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)

        # Cleanup
        if self.attr_vert != -1:
            glDisableVertexAttribArray(self.attr_vert)
        if self.attr_norm != -1:
            glDisableVertexAttribArray(self.attr_norm)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glUseProgram(0)

