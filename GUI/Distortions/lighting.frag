#version 330

uniform sampler2D tex;
uniform float time;

uniform vec2 focus_pos;   // top-left of focus rect in normalized coords
uniform vec2 focus_size;  // size of focus rect in normalized coords

uniform vec2 clip_pos;    // normalized top-left of parent panel
uniform vec2 clip_size;   // normalized size of parent panel

in vec2 uv;
out vec4 fragColor;

// Random noise for flicker effects
float rand(vec2 co) {
    return fract(sin(dot(co.xy , vec2(12.9898, 78.233))) * 43758.5453);
}

void main() {
    vec3 baseColor = texture(tex, uv).rgb;
    vec3 color = baseColor;

    float brightness = dot(baseColor, vec3(0.299, 0.587, 0.114));

    // --- Clip only focus glow ---
    if (clip_size.x > 0.0 && clip_size.y > 0.0) {
        bool inside =
            uv.x >= clip_pos.x &&
            uv.x <= (clip_pos.x + clip_size.x) &&
            uv.y >= (1.0 - clip_pos.y - clip_size.y) &&
            uv.y <= (1.0 - clip_pos.y);

        if (inside) {
            // === Glow around focus element ===
            if (focus_size.x > 0.0 && focus_size.y > 0.0) {
                vec2 elementCenter = focus_pos + focus_size * 0.5;

                float distX = abs(uv.x - elementCenter.x) / (focus_size.x * 0.5);
                float distY = abs((1.0 - uv.y) - elementCenter.y) / (focus_size.y * 0.5);
                float dist = sqrt(distX * distX + distY * distY);

                float glow = 1.0 - smoothstep(0.0, 3.0, dist);
                glow *= mix(1.0, 2.0, clamp((brightness - 0.5) * 2.0, 0.0, 1.0));

                float flicker = 0.1 * rand(vec2(time * 10.0, uv.x * 200.0 + uv.y * 200.0));
                glow *= (0.18 + flicker);

                color += glow * vec3(0.65, 0.85, 1.0);
            }
        }
    }

    // === Global central oval lighting (not clipped, smaller radius & stronger edges) ===
    {
        vec2 center = vec2(0.5, 0.5);
        vec2 distVec = (uv - center) / vec2(0.75, 0.4); // smaller oval
        float dist = length(distVec);

        // Stronger edge darkening: center=1.0, edges ~0.6
        float lightFalloff = mix(0.6, 1.0, smoothstep(0.8, 0.2, dist));

        // Optional CRT breathing
        lightFalloff *= (0.98 + 0.02 * sin(time * 2.0));

        color *= lightFalloff;
    }

    fragColor = vec4(clamp(color, 0.0, 1.0), 1.0);
}
