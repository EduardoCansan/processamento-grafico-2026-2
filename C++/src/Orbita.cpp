// Exercicio: Sistema Planetario com hierarquia de transformacoes.
#include <cmath>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

#include <glad/glad.h>
#include <GLFW/glfw3.h>
#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>
#include <glm/gtc/type_ptr.hpp>

GLFWwindow* Window = nullptr;
GLuint Shader_programm = 0;
GLuint Vao_circulo = 0;
GLuint Vbo_circulo = 0;

int WIDTH = 800;
int HEIGHT = 800;

const int LADOS_CIRCULO = 40;
// Um vertice central, 40 vertices da borda e a repeticao do primeiro
// vertice da borda para fechar o leque de triangulos.
const int TOTAL_VERTICES = LADOS_CIRCULO + 2;

std::string leShaderDoArquivo(const char* caminhoArquivo) {
    std::ifstream arquivoShader(caminhoArquivo);

    if (!arquivoShader.is_open()) {
        std::cerr << "ERRO: Nao foi possivel abrir o arquivo do shader: "
                  << caminhoArquivo << std::endl;
        return "";
    }

    std::stringstream shaderStream;
    shaderStream << arquivoShader.rdbuf();
    return shaderStream.str();
}

void redimensionaCallback(GLFWwindow*, int largura, int altura) {
    WIDTH = largura;
    HEIGHT = altura;
}

void inicializaOpenGL() {
    if (!glfwInit()) {
        std::cerr << "Falha ao inicializar o GLFW" << std::endl;
        std::exit(EXIT_FAILURE);
    }

    Window = glfwCreateWindow(WIDTH, HEIGHT, "Sistema Planetario", nullptr, nullptr);
    if (!Window) {
        glfwTerminate();
        std::exit(EXIT_FAILURE);
    }

    glfwSetWindowSizeCallback(Window, redimensionaCallback);
    glfwMakeContextCurrent(Window);

    if (!gladLoadGLLoader((GLADloadproc)glfwGetProcAddress)) {
        std::cerr << "Falha ao inicializar o GLAD" << std::endl;
        glfwDestroyWindow(Window);
        glfwTerminate();
        std::exit(EXIT_FAILURE);
    }

    std::cout << "Placa de video: " << glGetString(GL_RENDERER) << std::endl;
    std::cout << "Versao do OpenGL: " << glGetString(GL_VERSION) << std::endl;
}

void inicializaCirculo() {
    std::vector<float> vertices;
    vertices.reserve(TOTAL_VERTICES * 3);

    const float raio = 0.25f;
    const float PI = 3.14159265359f;

    // Primeiro vertice: centro do circulo.
    vertices.push_back(0.0f);
    vertices.push_back(0.0f);
    vertices.push_back(0.0f);

    // Os vertices da borda percorrem de 0 a 2*PI. O ultimo repete o
    // primeiro ponto da borda e fecha o GL_TRIANGLE_FAN.
    for (int i = 0; i <= LADOS_CIRCULO; ++i) {
        const float theta = (2.0f * PI * i) / LADOS_CIRCULO;
        const float x = raio * std::cos(theta);
        const float y = raio * std::sin(theta);

        vertices.push_back(x);
        vertices.push_back(y);
        vertices.push_back(0.0f);
    }

    glGenVertexArrays(1, &Vao_circulo);
    glBindVertexArray(Vao_circulo);

    glGenBuffers(1, &Vbo_circulo);
    glBindBuffer(GL_ARRAY_BUFFER, Vbo_circulo);
    glBufferData(
        GL_ARRAY_BUFFER,
        static_cast<GLsizeiptr>(vertices.size() * sizeof(float)),
        vertices.data(),
        GL_STATIC_DRAW
    );

    glEnableVertexAttribArray(0);
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * sizeof(float), nullptr);

    glBindBuffer(GL_ARRAY_BUFFER, 0);
    glBindVertexArray(0);
}

GLuint compilaShader(GLenum tipo, const std::string& codigo, const char* nome) {
    const char* fonte = codigo.c_str();
    GLuint shader = glCreateShader(tipo);
    glShaderSource(shader, 1, &fonte, nullptr);
    glCompileShader(shader);

    GLint compilou = GL_FALSE;
    glGetShaderiv(shader, GL_COMPILE_STATUS, &compilou);
    if (!compilou) {
        char infoLog[512];
        glGetShaderInfoLog(shader, sizeof(infoLog), nullptr, infoLog);
        std::cerr << "Erro no " << nome << ":\n" << infoLog << std::endl;
    }

    return shader;
}

void inicializaShaders() {
    const std::string vertexCode =
        leShaderDoArquivo("../assets/shaders/3/2/vertex_shader.glsl");
    const std::string fragmentCode =
        leShaderDoArquivo("../assets/shaders/3/2/fragment_shader.glsl");

    if (vertexCode.empty() || fragmentCode.empty()) {
        glfwDestroyWindow(Window);
        glfwTerminate();
        std::exit(EXIT_FAILURE);
    }

    const GLuint vertexShader =
        compilaShader(GL_VERTEX_SHADER, vertexCode, "vertex shader");
    const GLuint fragmentShader =
        compilaShader(GL_FRAGMENT_SHADER, fragmentCode, "fragment shader");

    Shader_programm = glCreateProgram();
    glAttachShader(Shader_programm, vertexShader);
    glAttachShader(Shader_programm, fragmentShader);
    glLinkProgram(Shader_programm);

    GLint linkou = GL_FALSE;
    glGetProgramiv(Shader_programm, GL_LINK_STATUS, &linkou);
    if (!linkou) {
        char infoLog[512];
        glGetProgramInfoLog(Shader_programm, sizeof(infoLog), nullptr, infoLog);
        std::cerr << "Erro na linkagem do shader:\n" << infoLog << std::endl;
    }

    glDeleteShader(vertexShader);
    glDeleteShader(fragmentShader);
}

void inicializaRenderizacao() {
    const GLint modelLoc = glGetUniformLocation(Shader_programm, "model");
    const GLint corLoc = glGetUniformLocation(Shader_programm, "cor");

    const float Tx = 0.58f;
    const float Ty = 0.0f;
    const float escalaSatelite = 0.35f;

    while (!glfwWindowShouldClose(Window)) {
        glClearColor(0.0f, 0.0f, 0.1f, 1.0f);
        glClear(GL_COLOR_BUFFER_BIT);
        glViewport(0, 0, WIDTH, HEIGHT);

        glUseProgram(Shader_programm);
        glBindVertexArray(Vao_circulo);

        // Astro central: a geometria permanece na origem com matriz identidade.
        glm::mat4 modelAstro = glm::mat4(1.0f);
        glUniformMatrix4fv(modelLoc, 1, GL_FALSE, glm::value_ptr(modelAstro));
        glUniform4f(corLoc, 1.0f, 0.0f, 0.0f, 1.0f);
        glDrawArrays(GL_TRIANGLE_FAN, 0, TOTAL_VERTICES);

        // Satelite: R * T * S. Como os vertices sao vetores-coluna, a escala
        // atua primeiro, depois a translacao define o raio e a rotacao produz
        // a orbita ao redor da origem.
        const float anguloOrbita = 35.0f * static_cast<float>(glfwGetTime());
        glm::mat4 modelSatelite = glm::mat4(1.0f);
        modelSatelite = glm::rotate(
            modelSatelite,
            glm::radians(anguloOrbita),
            glm::vec3(0.0f, 0.0f, 1.0f)
        );
        modelSatelite = glm::translate(modelSatelite, glm::vec3(Tx, Ty, 0.0f));
        modelSatelite = glm::scale(
            modelSatelite,
            glm::vec3(escalaSatelite, escalaSatelite, 1.0f)
        );

        glUniformMatrix4fv(modelLoc, 1, GL_FALSE, glm::value_ptr(modelSatelite));
        glUniform4f(corLoc, 0.15f, 0.55f, 1.0f, 1.0f);
        glDrawArrays(GL_TRIANGLE_FAN, 0, TOTAL_VERTICES);

        glfwSwapBuffers(Window);
        glfwPollEvents();

        if (glfwGetKey(Window, GLFW_KEY_ESCAPE) == GLFW_PRESS) {
            glfwSetWindowShouldClose(Window, GLFW_TRUE);
        }
    }
}

void liberaRecursos() {
    glDeleteBuffers(1, &Vbo_circulo);
    glDeleteVertexArrays(1, &Vao_circulo);
    glDeleteProgram(Shader_programm);
    glfwDestroyWindow(Window);
    glfwTerminate();
}

int main() {
    inicializaOpenGL();
    inicializaCirculo();
    inicializaShaders();
    inicializaRenderizacao();
    liberaRecursos();

    return 0;
}
