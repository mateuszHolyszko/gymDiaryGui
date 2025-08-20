#version 120

attribute vec2 in_vert;
attribute vec2 in_uv;

varying vec2 uv;

void main() {
    // Flip Y-coordinate to match OpenGL's coordinate system
    uv = vec2(in_uv.x, 1.0 - in_uv.y);
    gl_Position = vec4(in_vert, 0.0, 1.0);
}