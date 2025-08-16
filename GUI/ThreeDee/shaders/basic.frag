#version 330
in vec3 v_normal;
out vec4 f_color;

void main() {
    float light = dot(normalize(v_normal), normalize(vec3(0, 1, 1)));
    light = clamp(light, 0.1, 1.0);
    f_color = vec4(vec3(light), 1.0);
}
