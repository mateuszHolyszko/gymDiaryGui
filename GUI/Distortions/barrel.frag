#version 330

uniform sampler2D tex;
uniform float time;

in vec2 uv;
out vec4 fragColor;

void main() {
    // === CRT tube distortion ===
    vec2 center = vec2(0.5, 0.5);
    vec2 off_center = uv - center;

    // Barrel distortion: 0.3 controls curvature strength
    off_center *= 1.0 + 0.3 * pow(abs(off_center.yx), vec2(2.5));

    vec2 uv0 = center + off_center;

    // Outside screen → gray border
    if (uv0.x > 1.0 || uv0.x < 0.0 || uv0.y > 1.0 || uv0.y < 0.0) {
        fragColor = vec4(0.1, 0.1, 0.1, 1.0);
        return;
    }

    fragColor = texture(tex, uv0);
}
