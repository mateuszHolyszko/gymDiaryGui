import ctypes
import numpy as np
import pyrr
import trimesh
from gl_helpers import gl, link_program, FullscreenQuad, create_rgba_texture, create_fbo_with_color_depth
from GUI.elements.Element import Element

# --- Shaders ---
VERT_SHADER = """
attribute vec3 in_pos;
attribute vec3 in_normal;
uniform mat4 u_mvp;
varying vec3 v_normal;
void main() {
    gl_Position = u_mvp * vec4(in_pos, 1.0);
    v_normal = in_normal;
}
"""

FRAG_SHADER = """
precision mediump float;
varying vec3 v_normal;
void main() {
    vec3 light_dir = normalize(vec3(0.5, 1.0, 0.8));
    float diff = max(dot(normalize(v_normal), light_dir), 0.0);
    
    // Use alpha based on the diffuse lighting
    // This makes edges more transparent for smoother blending
    float alpha = smoothstep(0.1, 0.5, diff);
    
    // Gray color instead of blue: vec3(0.5) is medium gray
    // You can adjust this to any gray value (0.0=black, 1.0=white)
    vec3 gray_color = vec3(0.7);  // Light gray
    gl_FragColor = vec4(gray_color * diff, alpha);
}
"""

def load_obj(path):
    mesh = trimesh.load(path, force='mesh')
    mesh.apply_translation(-mesh.centroid)
    scale = 1.5 / np.max(mesh.extents)
    mesh.apply_scale(scale)
    verts = np.array(mesh.vertices, dtype=np.float32)
    norms = np.array(mesh.vertex_normals, dtype=np.float32)
    faces = np.array(mesh.faces, dtype=np.uint32)
    verts = verts[faces].reshape(-1, 3)
    norms = norms[faces].reshape(-1, 3)
    return verts, norms


class Display3D(Element):
    """A 3D element that can render into a given texture."""

    def __init__(self, x, y, width, height, model_path, manager, parent_panel=None, selectable=True, neighbors=None, layer=0):
        super().__init__(x, y, width, height, manager, parent_panel, selectable, neighbors, layer)
        self.width = int(width)
        self.height = int(height)
        self.x = int(x)
        self.y = int(y)
        
        # Store resource IDs for cleanup
        self.vbo = None
        self.prog3d = None
        self.verts = None
        self.norms = None

        # Load mesh
        self.verts, self.norms = load_obj(model_path)
        interleaved = np.hstack([self.verts, self.norms]).astype(np.float32)

        self.vbo = gl.glGenBuffers(1)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, interleaved.nbytes, interleaved, gl.GL_STATIC_DRAW)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)

        # Programs
        self.prog3d = link_program(VERT_SHADER, FRAG_SHADER)

        # Locations
        self.pos_loc = gl.glGetAttribLocation(self.prog3d, "in_pos")
        self.norm_loc = gl.glGetAttribLocation(self.prog3d, "in_normal")
        self.u_mvp_loc = gl.glGetUniformLocation(self.prog3d, "u_mvp")

        self.angle = 0.0

    def render_3d(self, target_tex: int, viewport):
        """
        Renders the 3D model into the provided texture.
        target_tex: GLuint of the texture to render into.
        viewport: tuple(x, y, width, height)
        """
        x, y, w, h = viewport

        # --- Create a temporary FBO ---
        tmp_fbo = gl.glGenFramebuffers(1)
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, tmp_fbo)
        gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER, gl.GL_COLOR_ATTACHMENT0, gl.GL_TEXTURE_2D, target_tex, 0)

        # --- Check FBO ---
        if gl.glCheckFramebufferStatus(gl.GL_FRAMEBUFFER) != gl.GL_FRAMEBUFFER_COMPLETE:
            print("Display3D FBO incomplete!")
            gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)
            gl.glDeleteFramebuffers(1, [tmp_fbo])
            return

        # --- Set viewport & clear ---
        gl.glViewport(0,50, w, h)
        
        # Disable depth test since we don't need it
        gl.glDisable(gl.GL_DEPTH_TEST)
        
        # Clear with transparent background
        gl.glClearColor(0.0, 0.0, 0.0, 0.0)  # Transparent black (alpha = 0.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        # --- Enable blending for the model ---
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

        # --- Render 3D model ---
        gl.glUseProgram(self.prog3d)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, self.vbo)
        gl.glEnableVertexAttribArray(self.pos_loc)
        gl.glVertexAttribPointer(self.pos_loc, 3, gl.GL_FLOAT, False, 24, ctypes.c_void_p(0))
        gl.glEnableVertexAttribArray(self.norm_loc)
        gl.glVertexAttribPointer(self.norm_loc, 3, gl.GL_FLOAT, False, 24, ctypes.c_void_p(12))

        # Compute MVP
        proj = pyrr.matrix44.create_perspective_projection(45, w/h, 0.1, 100.0)
        view = pyrr.matrix44.create_look_at([0,0,3], [0,0,0], [0,1,0])
        model = pyrr.matrix44.create_from_y_rotation(self.angle)
        mvp = model @ view @ proj
        gl.glUniformMatrix4fv(self.u_mvp_loc, 1, False, mvp.astype(np.float32))

        gl.glDrawArrays(gl.GL_TRIANGLES, 0, len(self.verts))

        # --- Cleanup ---
        gl.glDisableVertexAttribArray(self.pos_loc)
        gl.glDisableVertexAttribArray(self.norm_loc)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, 0)
        gl.glUseProgram(0)
        
        gl.glDisable(gl.GL_BLEND)  # Disable blending
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)

        gl.glDeleteFramebuffers(1, [tmp_fbo])

        # Calculate rotation speed based on angle
        base_speed = 0.06
        angle_mod = self.angle % (2 * np.pi)  # Normalize angle to 0-2π

        # Check if we're in the backside range (90° to 270° in radians: 1.57 to 4.71)
        if (angle_mod > 1.57 and angle_mod < 4.71):
            # Backside is facing viewer - rotate faster (3x speed)
            rotation_speed = base_speed * 3
        else:
            # Frontside is facing viewer - normal speed
            rotation_speed = base_speed

        # Update angle with appropriate speed
        self.angle += rotation_speed

    def on_release(self):
        """Release all OpenGL resources and clean up"""
        if self.vbo is not None:
            gl.glDeleteBuffers(1, [self.vbo])
            self.vbo = None
            
        if self.prog3d is not None:
            gl.glDeleteProgram(self.prog3d)
            self.prog3d = None
            
        # Release Python resources
        self.verts = None
        self.norms = None
        
        print("Display3D resources released")

    def render(self, screen):
        pass

    def on_press(self):
        pass