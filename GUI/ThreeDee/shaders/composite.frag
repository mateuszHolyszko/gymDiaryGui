#version 120

varying vec2 v_uv;

uniform sampler2D tex_gui;
uniform sampler2D tex_3d;

uniform vec2 elem_pos;
uniform vec2 elem_size;

void main() {
    // Convert screen uv to TOP-LEFT space
    vec2 uv_top = vec2(v_uv.x, 1.0 - v_uv.y);

    // GUI samples
    vec4 gui_color = texture2D(tex_gui, uv_top);

    // Compute element-relative uv
    vec2 rel_uv_top = (uv_top - elem_pos) / elem_size;
    vec4 model_color = vec4(0.0);

    // If inside the element rect...
    if (rel_uv_top.x >= 0.0 && rel_uv_top.x <= 1.0 &&
        rel_uv_top.y >= 0.0 && rel_uv_top.y <= 1.0)
    {
        // Flip Y for 3D texture
        vec2 rel_uv_gl = vec2(rel_uv_top.x, 1.0 - rel_uv_top.y);
        model_color = texture2D(tex_3d, rel_uv_gl);
    }

    // 3D over GUI using model alpha
    gl_FragColor = mix(gui_color, model_color, model_color.a);
}