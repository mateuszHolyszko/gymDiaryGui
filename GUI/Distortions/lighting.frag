#version 330

uniform sampler2D tex;
uniform float time;

uniform vec2 focus_pos;   // top-left of focus rect in normalized coords
uniform vec2 focus_size;  // size of focus rect in normalized coords

uniform vec2 clip_pos;   // normalized top-left of parent panel
uniform vec2 clip_size;  // normalized size of parent panel

in vec2 uv;
out vec4 fragColor;

float rand(vec2 co) {
    return fract(sin(dot(co.xy ,vec2(12.9898,78.233))) * 43758.5453);
}

float phosphorPersistence(float brightness, float t) {
    float persistence = brightness * exp(-0.5 * brightness);
    return persistence * (0.95 + 0.05 * sin(t * 10.0));
}

void main() {
    vec3 baseColor = texture(tex, uv).rgb;
    vec3 color = baseColor;

    // Clip lighting to parent panel
    if (clip_size.x > 0.0 && clip_size.y > 0.0) {
        bool inside =
            uv.x >= clip_pos.x &&
            uv.x <= (clip_pos.x + clip_size.x) &&
            uv.y >= (1.0 - clip_pos.y - clip_size.y) &&
            uv.y <= (1.0 - clip_pos.y);

        if (!inside) {
            fragColor = vec4(baseColor, 1.0);
            return;
        }
    }

    float brightness = dot(baseColor, vec3(0.299, 0.587, 0.114));

    // === Glow around focus element (now brightness-dependent) ===
    if (focus_size.x > 0.0 && focus_size.y > 0.0) {
        vec2 elementCenter = focus_pos + focus_size * 0.5;

        float distX = abs(uv.x - elementCenter.x) / (focus_size.x * 0.5);
        float distY = abs((1.0 - uv.y) - elementCenter.y) / (focus_size.y * 0.5);
        float dist = sqrt(distX * distX + distY * distY);

        // Steeper falloff but more intense at center
        float glow = 1.0 - smoothstep(0.0, 3.0, dist);

        // Boost glow based on brightness (white pixels glow more)
        glow *= mix(1.0, 2.0, clamp((brightness - 0.5) * 2.0, 0.0, 1.0));

        // Add noise flicker + small persistence shimmer
        float flicker = 0.05 * rand(vec2(time * 10.0, uv.x * 200.0 + uv.y * 200.0));
        glow *= (0.18 + flicker);  // increased base from 0.07 → 0.18

        // Cool bluish tint for focus glow
        color += glow * vec3(0.65, 0.85, 1.0);
    }

    // === Phosphor glow for bright pixels ===
    if (brightness > 0.8) {
        float persistence = phosphorPersistence(brightness, time);

        // P22 phosphor tint
        vec3 phosphorTint = vec3(0.7, 1.0, 0.8);

        // Gentle shimmer & halo
        float halo = 0.15 * sin(time * 60.0 + uv.x * 400.0) + 1.05;

        // Intensify for pure whites
        float whiteBoost = smoothstep(0.85, 1.0, brightness) * 1.5;

        color += persistence * phosphorTint * halo * whiteBoost;
    }

    fragColor = vec4(clamp(color, 0.0, 1.0), 1.0);
}
