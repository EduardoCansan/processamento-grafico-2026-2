// Câmera

// Neste exemplo, especificamos uma câmera virtual através da aplicação de transformações de projeção e lookAt
#include <iostream>
#include <glad/glad.h>
#include <GLFW/glfw3.h>
#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>
#include <glm/gtc/type_ptr.hpp>
#define STB_IMAGE_IMPLEMENTATION
#include "stb_image.h"
#include <fstream>
#include <sstream>

GLFWwindow* Window = nullptr;
GLuint Shader_programm = 0;
GLuint Vao = 0;
unsigned int texture1;
int WIDTH = 800;
int HEIGHT = 600;

float Tempo_entre_frames = 0.0f; // variavel utilizada para movimentar a camera

// Variáveis referentes a câmera virtual e sua projeção
float Cam_speed = 5.0f; // velocidade da camera aumentada um pouco para navegação livre
glm::vec3 Cam_pos = glm::vec3(0.0f, 0.0f, 2.0f); // posicao inicial da câmera
glm::vec3 Cam_front = glm::vec3(0.0f, 0.0f, -1.0f); // vetor para onde a câmera está olhando
glm::vec3 Cam_up = glm::vec3(0.0f, 1.0f, 0.0f); // vetor "para cima" global

float Cam_yaw = 0.0f; // ângulo de rotação da câmera (esquerda/direita)
float Cam_pitch = 0.0f; // ângulo de inclinação da câmera (cima/baixo)

// Variáveis de controle do mouse
double lastX = WIDTH / 2.0;
double lastY = HEIGHT / 2.0;
bool primeiro_mouse = true;

std::string leShaderDoArquivo(const char* caminhoArquivo) {
    std::ifstream arquivoShader(caminhoArquivo);
    
    // Verifica se conseguiu abrir o arquivo
    if (!arquivoShader.is_open()) {
        std::cerr << "ERRO: Nao foi possivel abrir o arquivo do shader: " << caminhoArquivo << std::endl;
        return "";
    }
    
    std::stringstream shaderStream;
    // Lê o buffer do arquivo e joga no stream
    shaderStream << arquivoShader.rdbuf();
    arquivoShader.close();
    
    // Retorna o stream convertido para string
    return shaderStream.str();
}

void carregaTextura(){
    // AVISO: Imagens são lidas de Cima para Baixo pelo STB.
    // O OpenGL espera o Y(0) embaixo. É VITAL mandar o STB inverter o eixo Y!
    stbi_set_flip_vertically_on_load(true);

    int width, height, nrChannels;
    unsigned char *data = stbi_load("../assets/tex/dirt.jpg", &width, &height, &nrChannels, 0);

    if (data) {
        // O ponteiro "data" agora contém os pixels sequenciais (ex: RGB RGB...)
        // 1. Gera e faz o bind do ID da textura
        glGenTextures(1, &texture1);
        glBindTexture(GL_TEXTURE_2D, texture1);

        // 2. Configura os parâmetros (Wrapping / Filtering) no objeto ativo
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR);

        // 3. Envia os bytes da RAM para a VRAM e gera os mipmaps
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, data);
        glGenerateMipmap(GL_TEXTURE_2D);
    } else {
        std::cout << "Falha ao ler textura" << std::endl;
    }
    // 4. Libera a RAM, a GPU já assumiu a carga
    stbi_image_free(data);
}

void redimensionaCallback(GLFWwindow* window, int w, int h) {
    WIDTH = w;
    HEIGHT = h;
    glViewport(0, 0, WIDTH, HEIGHT);
}

// Callback responsável por ler a posição do mouse e girar a câmera
void mouse_callback(GLFWwindow* window, double xpos, double ypos) {
    if (primeiro_mouse) {
        lastX = xpos;
        lastY = ypos;
        primeiro_mouse = false;
    }

    float xoffset = xpos - lastX;
    float yoffset = lastY - ypos; // Invertido, pois as coordenadas Y vão de cima para baixo
    
    lastX = xpos;
    lastY = ypos;

    float sensibilidade = 0.1f;
    xoffset *= sensibilidade;
    yoffset *= sensibilidade;

    Cam_yaw -= xoffset;
    Cam_pitch += yoffset;

    // Trava do pitch para evitar que a câmera dê uma cambalhota
    if (Cam_pitch > 89.0f) Cam_pitch = 89.0f;
    if (Cam_pitch < -89.0f) Cam_pitch = -89.0f;
}

void inicializaOpenGL() {
    if (!glfwInit()) {
        std::cerr << "Falha ao inicializar o GLFW" << std::endl;
        exit(EXIT_FAILURE);
    }

    Window = glfwCreateWindow(WIDTH, HEIGHT, "Exemplo - Camera Livre com Mouse", NULL, NULL);
    if (!Window) {
        glfwTerminate();
        exit(EXIT_FAILURE);
    }

    glfwSetWindowSizeCallback(Window, redimensionaCallback);
    
    // Registra a função do mouse e oculta o cursor na tela
    glfwSetCursorPosCallback(Window, mouse_callback);
    glfwSetInputMode(Window, GLFW_CURSOR, GLFW_CURSOR_DISABLED);
    
    glfwMakeContextCurrent(Window);

    if (!gladLoadGLLoader((GLADloadproc)glfwGetProcAddress)) {
        std::cerr << "Falha ao inicializar o GLAD" << std::endl;
        exit(EXIT_FAILURE);
    }
}

void inicializaObjetos() {
    glGenVertexArrays(1, &Vao);
    glBindVertexArray(Vao);

    // VBO único intercalando Posições (X,Y,Z) e Texturas (U,V)
    float vertices[] = {
        // POSIÇÕES             // TEXTURAS (U, V)
        // face frontal
         0.5f,  0.5f,  0.5f,    1.0f, 1.0f,
         0.5f, -0.5f,  0.5f,    1.0f, 0.0f,
        -0.5f, -0.5f,  0.5f,    0.0f, 0.0f,
        -0.5f,  0.5f,  0.5f,    0.0f, 1.0f,
         0.5f,  0.5f,  0.5f,    1.0f, 1.0f,
        -0.5f, -0.5f,  0.5f,    0.0f, 0.0f,

        // face traseira
         0.5f,  0.5f, -0.5f,    1.0f, 1.0f,
         0.5f, -0.5f, -0.5f,    1.0f, 0.0f,
        -0.5f, -0.5f, -0.5f,    0.0f, 0.0f,
        -0.5f,  0.5f, -0.5f,    0.0f, 1.0f,
         0.5f,  0.5f, -0.5f,    1.0f, 1.0f,
        -0.5f, -0.5f, -0.5f,    0.0f, 0.0f,

        // face esquerda
        -0.5f, -0.5f,  0.5f,    1.0f, 0.0f,
        -0.5f,  0.5f,  0.5f,    1.0f, 1.0f,
        -0.5f, -0.5f, -0.5f,    0.0f, 0.0f,
        -0.5f, -0.5f, -0.5f,    0.0f, 0.0f,
        -0.5f,  0.5f, -0.5f,    0.0f, 1.0f,
        -0.5f,  0.5f,  0.5f,    1.0f, 1.0f,

        // face direita
         0.5f, -0.5f,  0.5f,    0.0f, 0.0f,
         0.5f,  0.5f,  0.5f,    0.0f, 1.0f,
         0.5f, -0.5f, -0.5f,    1.0f, 0.0f,
         0.5f, -0.5f, -0.5f,    1.0f, 0.0f,
         0.5f,  0.5f, -0.5f,    1.0f, 1.0f,
         0.5f,  0.5f,  0.5f,    0.0f, 1.0f,

        // face baixo
        -0.5f, -0.5f,  0.5f,    0.0f, 1.0f,
         0.5f, -0.5f,  0.5f,    1.0f, 1.0f,
         0.5f, -0.5f, -0.5f,    1.0f, 0.0f,
         0.5f, -0.5f, -0.5f,    1.0f, 0.0f,
        -0.5f, -0.5f, -0.5f,    0.0f, 0.0f,
        -0.5f, -0.5f,  0.5f,    0.0f, 1.0f,

        // face cima
        -0.5f,  0.5f,  0.5f,    0.0f, 0.0f,
         0.5f,  0.5f,  0.5f,    1.0f, 0.0f,
         0.5f,  0.5f, -0.5f,    1.0f, 1.0f,
         0.5f,  0.5f, -0.5f,    1.0f, 1.0f,
        -0.5f,  0.5f, -0.5f,    0.0f, 1.0f,
        -0.5f,  0.5f,  0.5f,    0.0f, 0.0f
    };
    
    GLuint vbo;
    glGenBuffers(1, &vbo);
    glBindBuffer(GL_ARRAY_BUFFER, vbo);
    glBufferData(GL_ARRAY_BUFFER, sizeof(vertices), vertices, GL_STATIC_DRAW);

    // Atributo 0: Posições (X, Y, Z)
    // O stride agora é 5 floats. Offset é 0.
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 5 * sizeof(float), (void*)0);
    glEnableVertexAttribArray(0);

    // Atributo 1: Coordenadas de Textura (U, V)
    // O stride é 5 floats. Offset pula 3 floats para chegar no U.
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 5 * sizeof(float), (void*)(3 * sizeof(float)));
    glEnableVertexAttribArray(1);
}

void inicializaShaders() {
    // 1. Lê o código dos arquivos externos
    std::string vertexCode = leShaderDoArquivo("../assets/shaders/5/2/vertex_shader.glsl");
    std::string fragmentCode = leShaderDoArquivo("../assets/shaders/5/2/fragment_shader.glsl");

    // 2. Converte de std::string para const char* para o OpenGL ler
    const char* vertex_shader = vertexCode.c_str();
    const char* fragment_shader = fragmentCode.c_str();

    //3. Compila o vertex shader
    GLuint vs = glCreateShader(GL_VERTEX_SHADER);
    glShaderSource(vs, 1, &vertex_shader, NULL);
    glCompileShader(vs);
    
    GLint success;
    char infoLog[512];
    glGetShaderiv(vs, GL_COMPILE_STATUS, &success);
    if (!success) {
        glGetShaderInfoLog(vs, 512, NULL, infoLog);
        std::cerr << "Erro no vertex shader:\n" << infoLog << std::endl;
    }

    //3. Compila o fragment shader shader
    GLuint fs = glCreateShader(GL_FRAGMENT_SHADER);
    glShaderSource(fs, 1, &fragment_shader, NULL);
    glCompileShader(fs);
    
    glGetShaderiv(fs, GL_COMPILE_STATUS, &success);
    if (!success) {
        glGetShaderInfoLog(fs, 512, NULL, infoLog);
        std::cerr << "Erro no fragment shader:\n" << infoLog << std::endl;
    }

    //5. Especificação do Shader Programm
    Shader_programm = glCreateProgram();
    glAttachShader(Shader_programm, vs);
    glAttachShader(Shader_programm, fs);
    glLinkProgram(Shader_programm);
    
    glGetProgramiv(Shader_programm, GL_LINK_STATUS, &success);
    if (!success) {
        glGetProgramInfoLog(Shader_programm, 512, NULL, infoLog);
        std::cerr << "Erro na linkagem do shader:\n" << infoLog << std::endl;
    }

    glDeleteShader(vs);
    glDeleteShader(fs);
}

void atualizaDirecaoCamera() {
    // Recalcula o vetor de direção considerando tanto o Yaw quanto o Pitch
    glm::vec3 front;
    front.x = sin(glm::radians(-Cam_yaw)) * cos(glm::radians(Cam_pitch));
    front.y = sin(glm::radians(Cam_pitch)); 
    front.z = -cos(glm::radians(-Cam_yaw)) * cos(glm::radians(Cam_pitch));
    Cam_front = glm::normalize(front);
}

void especificaMatrizVisualizacao() {
    glm::mat4 visualizacao = glm::lookAt(Cam_pos, Cam_pos + Cam_front, Cam_up);

    GLint transformLoc = glGetUniformLocation(Shader_programm, "view");
    glUniformMatrix4fv(transformLoc, 1, GL_FALSE, glm::value_ptr(visualizacao));
}

void especificaMatrizProjecao() {
    float znear = 0.1f;
    float zfar = 100.0f;
    float fov = glm::radians(67.0f);
    float aspecto = (float)WIDTH / (float)HEIGHT;

    glm::mat4 projecao = glm::perspective(fov, aspecto, znear, zfar);

    GLint transformLoc = glGetUniformLocation(Shader_programm, "proj");
    glUniformMatrix4fv(transformLoc, 1, GL_FALSE, glm::value_ptr(projecao));
}

void inicializaCamera() {
    atualizaDirecaoCamera();
    especificaMatrizVisualizacao();
    especificaMatrizProjecao();
}

void trataTeclado() {
    if (glfwGetKey(Window, GLFW_KEY_ESCAPE) == GLFW_PRESS) {
        glfwSetWindowShouldClose(Window, true);
    }

    // Calcula o vetor "Direita" da câmera usando o Cross product
    glm::vec3 Cam_right = glm::normalize(glm::cross(Cam_front, Cam_up));

    // A/D - Movimento lateral (Strafe)
    if (glfwGetKey(Window, GLFW_KEY_A) == GLFW_PRESS) {
        Cam_pos -= Cam_right * Cam_speed * Tempo_entre_frames;
    }
    if (glfwGetKey(Window, GLFW_KEY_D) == GLFW_PRESS) {
        Cam_pos += Cam_right * Cam_speed * Tempo_entre_frames;
    }

    // W/S - Movimento para frente e para trás
    if (glfwGetKey(Window, GLFW_KEY_W) == GLFW_PRESS) {
        Cam_pos += Cam_front * Cam_speed * Tempo_entre_frames;
    }
    if (glfwGetKey(Window, GLFW_KEY_S) == GLFW_PRESS) {
        Cam_pos -= Cam_front * Cam_speed * Tempo_entre_frames;
    }

    // Subir / Descer estritamente no eixo Y global (Q e E agora fazem isso, já que o mouse cuida da rotação)
    if (glfwGetKey(Window, GLFW_KEY_E) == GLFW_PRESS) {
        Cam_pos.y += Cam_speed * Tempo_entre_frames;
    }
    if (glfwGetKey(Window, GLFW_KEY_Q) == GLFW_PRESS) {
        Cam_pos.y -= Cam_speed * Tempo_entre_frames;
    }
}

void inicializaRenderizacao() {
    double tempo_anterior = glfwGetTime();

    glEnable(GL_DEPTH_TEST);
    
    while (!glfwWindowShouldClose(Window)) {
        double tempo_frame_atual = glfwGetTime();
        Tempo_entre_frames = (float)(tempo_frame_atual - tempo_anterior);
        tempo_anterior = tempo_frame_atual;

        glClearColor(0.2f, 0.3f, 0.3f, 1.0f);
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
        
        glUseProgram(Shader_programm);
        
        trataTeclado();
        inicializaCamera();

        glActiveTexture(GL_TEXTURE0); // Ativa Gaveta 0
        glBindTexture(GL_TEXTURE_2D, texture1); // Pluga a Textura 1 nela  
        glBindVertexArray(Vao);

        glm::mat4 transformacao = glm::mat4(1.0f);
        transformacao = glm::rotate(transformacao, (float)glfwGetTime() * 0.5f, glm::vec3(0.5f, 1.0f, 0.0f));
        
        GLint transformLoc = glGetUniformLocation(Shader_programm, "matriz");
        glUniformMatrix4fv(transformLoc, 1, GL_FALSE, glm::value_ptr(transformacao));

        glDrawArrays(GL_TRIANGLES, 0, 36);

        glfwPollEvents();
        glfwSwapBuffers(Window);
    }
    
    glfwTerminate();
}

int main() {
    inicializaOpenGL();
    carregaTextura();
    inicializaObjetos();
    inicializaShaders();
    inicializaRenderizacao();

    return 0;
}