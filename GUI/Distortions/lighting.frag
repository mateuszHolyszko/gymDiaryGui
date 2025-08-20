#version 120

uniform sampler2D tex;
uniform float time;

uniform vec2 focus_pos;
uniform vec2 focus_size;
uniform vec2 clip_pos;
uniform vec2 clip_size;

varying vec2 uv;

// Random noise for flicker effects
float rand(vec2 co) {
    return fract(sin(dot(co.xy, vec2(12.9898, 78.233))) * 43758.5453);
}

void main() {
    vec3 baseColor = texture2D(tex, uv).rgb;
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

    // === Global central oval lighting ===
    {
        vec2 center = vec2(0.5, 0.5);
        vec2 distVec = (uv - center) / vec2(0.75, 0.4);
        float dist = length(distVec);

        float lightFalloff = mix(0.6, 1.0, smoothstep(0.8, 0.2, dist));
        lightFalloff *= (0.98 + 0.02 * sin(time * 2.0));

        color *= lightFalloff;
    }

    gl_FragColor = vec4(clamp(color, 0.0, 1.0), 1.0);
}