#version 330

in vec2 in_vert;
in vec2 in_uv;
out vec2 uv;

void main() {
    uv = vec2(in_uv.x,in_uv.y); // if number of passes is uneaven put uv = vec2(in_uv.x, 1.0 - in_uv.y);
    gl_Position = vec4(in_vert, 0.0, 1.0);
}
