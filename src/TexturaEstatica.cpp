// Este exemplo apresenta uma aplicação completa de OpenGL, que renderiza um quadrado na tela.
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
int HEIGHT = 800;

void redimensionaCallback(GLFWwindow* window, int w, int h) {
    WIDTH = w;
    HEIGHT = h;
}

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
void inicializaOpenGL() {
    // Inicializa GLFW
    if (!glfwInit()) {
        std::cerr << "Falha ao inicializar o GLFW" << std::endl;
        exit(EXIT_FAILURE);
    }

    // Criação de uma janela
    Window = glfwCreateWindow(WIDTH, HEIGHT, "Exemplo - renderizacao de um triangulo", NULL, NULL);
    
    // Caso não seja possível criar a janela, a GLFW e a aplicação são terminadas
    if (!Window) {
        glfwTerminate();
        exit(EXIT_FAILURE);
    }

    glfwSetWindowSizeCallback(Window, redimensionaCallback);
    glfwMakeContextCurrent(Window);

    // inicializar o GLAD
    if (!gladLoadGLLoader((GLADloadproc)glfwGetProcAddress)) {
        std::cerr << "Falha ao inicializar o GLAD" << std::endl;
        exit(EXIT_FAILURE);
    }

    std::cout << "Placa de video: " << glGetString(GL_RENDERER) << std::endl;
    std::cout << "Versao do OpenGL: " << glGetString(GL_VERSION) << std::endl;
}

void inicializaObjetos() {
    glGenVertexArrays(1, &Vao);
    glBindVertexArray(Vao);

    // VBO dos vértices e texturas
    float points[] = {
        // POSIÇÕES (X, Y, Z)   // COORDENADAS TEXTURA (U, V)
        //triaângulo 1
		0.5f, 0.5f, 0.0f,       1.0f, 1.0f, // Topo Direito
		0.5f, -0.5f, 0.0f,      1.0f, 0.0f, // Base Direita
		-0.5f, -0.5f, 0.0f,     0.0f, 0.0f, // Base Esquerda
		//triângulo 2
		-0.5f, 0.5f, 0.0f,      0.0f, 1.0f,  // Topo Esquerdo
		0.5f, 0.5f, 0.0f,       1.0f, 1.0f, // Topo Direito
		-0.5f, -0.5f, 0.0f,     0.0f, 0.0f, // Base Esquerda
    };

    GLuint vbo;
    glGenBuffers(1, &vbo);
    glBindBuffer(GL_ARRAY_BUFFER, vbo);
    glBufferData(GL_ARRAY_BUFFER, sizeof(points), points, GL_STATIC_DRAW);

    // Atributo 0: Posições (X, Y, Z)
    // O stride é de 5 floats (3 de posição + 2 de textura).
    // O offset é 0, pois os dados de posição começam no início do array.
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 5 * sizeof(float), (void*)0);
    glEnableVertexAttribArray(0);

    // Atributo 1: Coordenadas de Textura (U, V)
    // O stride continua sendo 5 floats.
    // O offset é o tamanho de 3 floats, pois precisamos pular X, Y e Z para chegar no U.
    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 5 * sizeof(float), (void*)(3 * sizeof(float)));
    glEnableVertexAttribArray(1);
}

void inicializaShaders() {
    // 1. Lê o código dos arquivos externos
    std::string vertexCode = leShaderDoArquivo("../assets/shaders/5/vertex_shader.glsl");
    std::string fragmentCode = leShaderDoArquivo("../assets/shaders/5/fragment_shader.glsl");

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

void inicializaRenderizacao() {
    while (!glfwWindowShouldClose(Window)) {
        glClear(GL_COLOR_BUFFER_BIT);
        glClearColor(0.2f, 0.3f, 0.3f, 1.0f);
        glViewport(0, 0, WIDTH, HEIGHT);

        glUseProgram(Shader_programm);

        glActiveTexture(GL_TEXTURE0); // Ativa Gaveta 0
        glBindTexture(GL_TEXTURE_2D, texture1); // Pluga a Textura 1 nela    
        glBindVertexArray(Vao);
        glDrawArrays(GL_TRIANGLES, 0, 6);

        glfwPollEvents();

        glfwSwapBuffers(Window);

        if (glfwGetKey(Window, GLFW_KEY_ESCAPE) == GLFW_PRESS) {
            glfwSetWindowShouldClose(Window, true);
        }
    }
    
    glfwTerminate();
}

// Função principal
int main() {
    inicializaOpenGL();
    carregaTextura();
    inicializaObjetos();
    inicializaShaders();
    inicializaRenderizacao();
    
    return 0;
}