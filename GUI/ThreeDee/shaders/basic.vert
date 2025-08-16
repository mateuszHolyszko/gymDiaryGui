#version 330
in vec3 in_vert;
in vec3 in_norm;

uniform mat4 mvp;
uniform mat4 model;

out vec3 v_normal;

void main() {
    gl_Position = mvp * vec4(in_vert, 1.0);
    v_normal = mat3(transpose(inverse(model))) * in_norm;
}
