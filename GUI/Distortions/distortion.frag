#version 330

uniform sampler2D tex;
uniform float time;
uniform float intensity;

in vec2 uv;
out vec4 fragColor;

// Random number generator
float rand(vec2 co) {
    return fract(sin(dot(co.xy, vec2(12.9898,78.233))) * 43758.5453);
}

void main() {
    // === Simple per-row sync jitter ===
    vec2 uv0 = uv; // Keep original UVs for distortion effects
    float rowIndex = floor(uv0.y * 240.0);
    float tStep = floor(time * 10.0);
    vec2 seed = vec2(rowIndex, tStep);

    if (rand(seed) < 0.04) {
        float dir = rand(seed + 10.0) < 0.5 ? -1.0 : 1.0;
        uv0.x += dir / 320.0;
    }

    // === VHS glitch ===
    if (rand(vec2(floor(time * 12.0), 0.0)) > 0.95) {
        float glitch_y = step(0.3, fract(uv0.y * 10.0));
        float glitch_offset = (rand(vec2(time, uv0.y)) - 0.5) * 0.2 * intensity;
        uv0.x += glitch_offset * glitch_y;
    }

    // === Chromatic aberration ===
    float shift = 0.02 * intensity;
    float r = texture(tex, uv0 + vec2(shift, 0.0)).r;
    float g = texture(tex, uv0).g;
    float b = texture(tex, uv0 - vec2(shift, 0.0)).b;
    vec3 color = vec3(r, g, b);

    // === Noise ===
    float noise = (rand(uv0 * time) - 0.5) * 0.5 * intensity;
    color += noise;

    // === Pronounced scanlines ===
    float scanlineMask = mod(floor(uv0.y * 480.0), 2.0);
    float scanlineStrength = mix(0.55, 1.0, scanlineMask);
    color *= scanlineStrength;

    fragColor = vec4(clamp(color, 0.0, 1.0), 1.0);
}
