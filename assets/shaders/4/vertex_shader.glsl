#version 400
layout(location = 0) in vec3 vertex_posicao;
layout(location = 1) in vec3 vertex_cores;

out vec3 cores;

uniform mat4 model, view, proj;

void main () {
    cores = vertex_cores;
    gl_Position = proj * view * model * vec4(vertex_posicao, 1.0);
}