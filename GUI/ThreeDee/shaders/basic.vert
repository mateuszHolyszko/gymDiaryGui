#version 120

attribute vec3 in_vert;
attribute vec3 in_norm;

uniform mat4 mvp;
uniform mat4 model;

varying vec3 v_normal;

void main() {
    gl_Position = mvp * vec4(in_vert, 1.0);
    
    // Simplified normal transformation (no inverse/transpose)
    v_normal = in_norm;
}