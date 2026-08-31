// Este exemplo apresenta uma aplicação completa de OpenGL, que renderiza um triângulo e um quadrado na tela.
#include <iostream>
#include <glad/glad.h>
#include <GLFW/glfw3.h>
#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>
#include <glm/gtc/type_ptr.hpp>

GLFWwindow* Window = nullptr;
GLuint Shader_programm1 = 0, Shader_programm2 = 0;
GLuint Vao_triangulo1 = 0, Vao_triangulo2 = 0;
int WIDTH = 800;
int HEIGHT = 600;

void redimensionaCallback(GLFWwindow* window, int w, int h) {
    WIDTH = w;
    HEIGHT = h;
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

void inicializaTriangulo1() {
    glGenVertexArrays(1, &Vao_triangulo1);
    glBindVertexArray(Vao_triangulo1);

    // VBO dos vértices
    float points[] = {
        -0.5f,  0.25f, 0.0f, // cima
        -0.75f, -0.25f, 0.0f, // direita
        -0.25f, -0.25f, 0.0f  // esquerda
    };

    GLuint pvbo;
    glGenBuffers(1, &pvbo);
    glBindBuffer(GL_ARRAY_BUFFER, pvbo);
    glBufferData(GL_ARRAY_BUFFER, sizeof(points), points, GL_STATIC_DRAW);
    glEnableVertexAttribArray(0);
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, (void*)0);


    // VBO de cores
    float cores[] = {
        1.0f, 0.0f, 0.0f, // vermelho
        0.0f, 1.0f, 0.0f, // verde
        0.0f, 0.0f, 1.0f  // azul
    };
    
    GLuint cvbo;
    glGenBuffers(1, &cvbo);
    glBindBuffer(GL_ARRAY_BUFFER, cvbo);
    glBufferData(GL_ARRAY_BUFFER, sizeof(cores), cores, GL_STATIC_DRAW);
    glEnableVertexAttribArray(1);
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, (void*)0);
}


void inicializaTriangulo2() {
    glGenVertexArrays(1, &Vao_triangulo2);
    glBindVertexArray(Vao_triangulo2);

    // VBO dos vértices
    float points[] = {
        0.5f,  0.25f, 0.0f, // cima
        0.75f, -0.25f, 0.0f, // direita
        0.25f, -0.25f, 0.0f  // esquerda
    };

    GLuint pvbo;
    glGenBuffers(1, &pvbo);
    glBindBuffer(GL_ARRAY_BUFFER, pvbo);
    glBufferData(GL_ARRAY_BUFFER, sizeof(points), points, GL_STATIC_DRAW);
    glEnableVertexAttribArray(0);
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, (void*)0);


    // VBO de cores
    float cores[] = {
        1.0f, 0.0f, 0.0f, // vermelho
        0.0f, 1.0f, 0.0f, // verde
        0.0f, 0.0f, 1.0f  // azul
    };
    
    GLuint cvbo;
    glGenBuffers(1, &cvbo);
    glBindBuffer(GL_ARRAY_BUFFER, cvbo);
    glBufferData(GL_ARRAY_BUFFER, sizeof(cores), cores, GL_STATIC_DRAW);
    glEnableVertexAttribArray(1);
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, (void*)0);
}


void inicializaShader1() {
    // Especificação do Vertex Shader
    const char* vertex_shader = 
        "#version 400\n"
        "layout(location = 0) in vec3 vertex_posicao;\n"
        "layout(location = 1) in vec3 vertex_cores;\n"
        "out vec3 cores;\n"
        "void main () {\n"
        "    cores = vertex_cores;\n"
        "    gl_Position = vec4(vertex_posicao, 1.0);\n"
        "}\n";

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

    // Especificação do Fragment Shader
    const char* fragment_shader = 
        "#version 400\n"
        "in vec3 cores;\n"
        "out vec4 frag_colour;\n"
        "void main () {\n"
        "    vec3 corInvertida = vec3(1.0) - cores;\n"
        "    frag_colour = vec4(corInvertida, 1.0);\n"
        "}\n";

    GLuint fs = glCreateShader(GL_FRAGMENT_SHADER);
    glShaderSource(fs, 1, &fragment_shader, NULL);
    glCompileShader(fs);
    
    glGetShaderiv(fs, GL_COMPILE_STATUS, &success);
    if (!success) {
        glGetShaderInfoLog(fs, 512, NULL, infoLog);
        std::cerr << "Erro no fragment shader:\n" << infoLog << std::endl;
    }

    // Especificação do Shader Programm
    Shader_programm1 = glCreateProgram();
    glAttachShader(Shader_programm1, vs);
    glAttachShader(Shader_programm1, fs);
    glLinkProgram(Shader_programm1);

    glGetProgramiv(Shader_programm1, GL_LINK_STATUS, &success);
    if (!success) {
        glGetProgramInfoLog(Shader_programm1, 512, NULL, infoLog);
    }

    glDeleteShader(vs);
    glDeleteShader(fs);
}

void inicializaShader2() {
    // Especificação do Vertex Shader
    const char* vertex_shader = 
        "#version 400\n"
        "layout(location = 0) in vec3 vertex_posicao;\n"
        "layout(location = 1) in vec3 vertex_cores;\n"
        "out vec3 cores;\n"
        "void main () {\n"
        "    cores = vertex_cores;\n"
        "    gl_Position = vec4(vertex_posicao, 1.0);\n"
        "}\n";

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

    // Especificação do Fragment Shader
    const char* fragment_shader = 
        "#version 400\n"
        "in vec3 cores;\n"
        "out vec4 frag_colour;\n"
        "void main () {\n"
        "    float L = cores.r * 0.299 + cores.g * 0.587 + cores.b * 0.114;\n"
        "    frag_colour = vec4(L, L, L, 1.0);\n"
        "}\n";

    GLuint fs = glCreateShader(GL_FRAGMENT_SHADER);
    glShaderSource(fs, 1, &fragment_shader, NULL);
    glCompileShader(fs);
    
    glGetShaderiv(fs, GL_COMPILE_STATUS, &success);
    if (!success) {
        glGetShaderInfoLog(fs, 512, NULL, infoLog);
        std::cerr << "Erro no fragment shader:\n" << infoLog << std::endl;
    }

    // Especificação do Shader Programm
    Shader_programm2 = glCreateProgram();
    glAttachShader(Shader_programm2, vs);
    glAttachShader(Shader_programm2, fs);
    glLinkProgram(Shader_programm2);
    
    glGetProgramiv(Shader_programm2, GL_LINK_STATUS, &success);
    if (!success) {
        glGetProgramInfoLog(Shader_programm2, 512, NULL, infoLog);
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

        //desenha o triangulo 1 usando o shader program 1
        glUseProgram(Shader_programm1);
        glBindVertexArray(Vao_triangulo1);
        glDrawArrays(GL_TRIANGLES, 0, 3);

        //desenha o triangulo 2 usando o shader program 2
        glUseProgram(Shader_programm2);
        glBindVertexArray(Vao_triangulo2);
        glDrawArrays(GL_TRIANGLES, 0, 3);

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
    inicializaTriangulo1();
    inicializaTriangulo2();
    inicializaShader1();
    inicializaShader2();
    inicializaRenderizacao();
    
    return 0;
}