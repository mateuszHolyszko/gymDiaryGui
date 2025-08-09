#version 330

uniform sampler2D tex;
uniform float time;

uniform vec2 focus_pos;   // top-left of focus rect in normalized coords
uniform vec2 focus_size;  // size of focus rect in normalized coords

uniform vec2 clip_pos;   // normalized top-left of parent panel
uniform vec2 clip_size;  // normalized size of parent panel

in vec2 uv;
out vec4 fragColor;

// Simple random function based on UV and time for subtle flicker noise
float rand(vec2 co) {
    return fract(sin(dot(co.xy ,vec2(12.9898,78.233))) * 43758.5453);
}

void main() {
    // Get base color from previous pass
    vec3 color = texture(tex, uv).rgb;

    // === Glow around focus element ===
    if (focus_size.x > 0.0 && focus_size.y > 0.0) {
        vec2 elementCenter = focus_pos + focus_size * 0.5;

        // Distance from current pixel to element center in "element space"
        float distX = abs(uv.x - elementCenter.x) / (focus_size.x * 0.5);
        float distY = abs((1.0 - uv.y) - elementCenter.y) / (focus_size.y * 0.5);

        float dist = sqrt(distX * distX + distY * distY);

        // Glow falloff - very gradual for wide bleed (range increased to 5.0)
        float glow = 1.0 - smoothstep(0.0, 5.0, dist);

        // Subtle noisy flicker using rand with UV and time, amplitude about 0.05
        float flicker = 0.05 * rand(vec2(time * 10.0, uv.x * 100.0 + uv.y * 100.0));

        // Final glow intensity: low base + noisy flicker
        glow *= 0.07 + flicker;

        // Add the glow (cold bluish tint)
        color += glow * vec3(0.6, 0.8, 1.0);
    }

    fragColor = vec4(clamp(color, 0.0, 1.0), 1.0);
}
