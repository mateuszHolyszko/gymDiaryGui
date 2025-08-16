#version 330
in vec2 v_uv;
out vec4 f_color;

uniform sampler2D tex_gui;
uniform sampler2D tex_3d;

// elem_pos/elem_size are in TOP-LEFT normalized coords (from Pygame)
uniform vec2 elem_pos;   // (x, y) of top-left-space bottom-left corner of the rect? No: top-left origin!
uniform vec2 elem_size;  // width, height

void main() {
    // Convert screen uv to TOP-LEFT space once
    vec2 uv_top = vec2(v_uv.x, 1.0 - v_uv.y);

    // GUI samples already in top-left space
    vec4 gui_color = texture(tex_gui, uv_top);

    // Compute element-relative uv ALSO in top-left space
    vec2 rel_uv_top = (uv_top - elem_pos) / elem_size;

    // Prepare model color
    vec4 model_color = vec4(0.0);

    // If inside the element rect...
    if (rel_uv_top.x >= 0.0 && rel_uv_top.x <= 1.0 &&
        rel_uv_top.y >= 0.0 && rel_uv_top.y <= 1.0)
    {
        // Flip Y when sampling the 3D texture (3D tex is bottom-left space)
        vec2 rel_uv_gl = vec2(rel_uv_top.x, 1.0 - rel_uv_top.y);
        model_color = texture(tex_3d, rel_uv_gl);
    }

    // 3D over GUI using model alpha
    f_color = mix(gui_color, model_color, model_color.a);
}
