#version 120

varying vec3 v_normal;

void main() {
    float light = dot(normalize(v_normal), normalize(vec3(0, 1, 1)));
    light = clamp(light, 0.1, 1.0);
    gl_FragColor = vec4(vec3(light), 1.0);
}