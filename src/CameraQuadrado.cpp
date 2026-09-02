// Este exemplo apresenta uma aplicação completa de OpenGL, que renderiza um triângulo e um quadrado na tela.
#include <iostream>
#include <string>
#include <fstream>
#include <sstream>
#include <glad/glad.h>
#include <GLFW/glfw3.h>
#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>
#include <glm/gtc/type_ptr.hpp>

GLFWwindow* Window = nullptr;
GLuint Shader_programm;
GLuint Vao;
int WIDTH = 800;
int HEIGHT = 800;

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

void inicializaQuadrado() {
    // Vao do quadrado
    glGenVertexArrays(1, &Vao);
    // Damos um bind no VAO, setando ele como VAO atual e colocando o mesmo no topo da máquina de estados do OpenGL
    glBindVertexArray(Vao);

    // VBO dos vértices
    float points[] = {
        // triângulo 1
		0.5f, 0.5f, 0.0f,      //vertice superior direito
		0.5f, -0.5f, 0.0f,     //vertice inferior direito
		-0.5f, -0.5f, 0.0f,    //vertice inferior esquerdo
		//triângulo 2
		-0.5f, 0.5f, 0.0f,     //vertice superior esquerdo
		0.5f, 0.5f, 0.0f,      //vertice superior direito
		-0.5f, -0.5f, 0.0f     //vertice inferior esquerdo
    };

    GLuint pvbo;
    glGenBuffers(1, &pvbo);
    glBindBuffer(GL_ARRAY_BUFFER, pvbo);
    glBufferData(GL_ARRAY_BUFFER, sizeof(points), points, GL_STATIC_DRAW);
    glEnableVertexAttribArray(0);
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, (void*)0);


    // VBO das cores
    float cores[] = {
        1.0f, 1.0f, 0.0f, // amarelo
        0.0f, 1.0f, 1.0f, // ciano
        1.0f, 0.0f, 1.0f,  // magenta
        0.0f, 1.0f, 1.0f, // ciano
        1.0f, 1.0f, 0.0f, // amarelo
        1.0f, 0.0f, 1.0f  // magenta
    };
    
    GLuint cvbo;
    glGenBuffers(1, &cvbo);
    glBindBuffer(GL_ARRAY_BUFFER, cvbo);
    glBufferData(GL_ARRAY_BUFFER, sizeof(cores), cores, GL_STATIC_DRAW);
    glEnableVertexAttribArray(1);
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, (void*)0);    
}


void inicializaShader1() {
    // 1. Lê o código dos arquivos externos
    std::string vertexCode = leShaderDoArquivo("../assets/shaders/4/vertex_shader.glsl");
    std::string fragmentCode = leShaderDoArquivo("../assets/shaders/4/fragment_shader.glsl");

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

    glEnable(GL_DEPTH_TEST);

    float xCamera = 0.0f, yCamera = 0.0f, zCamera = 3.0f;

    while (!glfwWindowShouldClose(Window)) {
        //Limpa a tela
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
        glClearColor(0.2f, 0.3f, 0.3f, 1.0f);
        glViewport(0, 0, WIDTH, HEIGHT);

        
        glUseProgram(Shader_programm);

        // 1. Construção da Matriz de transformação do modelo (Model)
        glm::mat4 model = glm::mat4(1.0);

        // 2. Construção da Matriz de View (LookAt)
        glm::vec3 cameraPos = glm::vec3(xCamera, yCamera, zCamera);
        glm::vec3 cameraTarget = glm::vec3(0.0f, 0.0f, -2.0f);
        glm::vec3 cameraUp = glm::vec3(0.0f, 1.0f, 0.0f);
        glm::mat4 view = glm::lookAt(cameraPos, cameraTarget, cameraUp);

        // 3. Construção da Matriz de Projeção (Perspectiva)
        // FoV de 70 graus, Tela 800x800, Near 0.1, Far 100.0
        glm::mat4 proj = glm::perspective(glm::radians(70.0f), (float)WIDTH/HEIGHT, 0.1f, 100.0f);

        //busca as matrizes no shader
        int modelLoc = glGetUniformLocation(Shader_programm, "model");
        int viewLoc = glGetUniformLocation(Shader_programm, "view");
        int projLoc = glGetUniformLocation(Shader_programm, "proj");

        //enviamos os valores do C++ para o shader
        glUniformMatrix4fv(modelLoc, 1, GL_FALSE, glm::value_ptr(model));
        glUniformMatrix4fv(viewLoc, 1, GL_FALSE, glm::value_ptr(view));
        glUniformMatrix4fv(projLoc, 1, GL_FALSE, glm::value_ptr(proj));

        glBindVertexArray(Vao);
        glDrawArrays(GL_TRIANGLES, 0, 6);

        glfwPollEvents();

        glfwSwapBuffers(Window);

        if (glfwGetKey(Window, GLFW_KEY_ESCAPE) == GLFW_PRESS) {
            glfwSetWindowShouldClose(Window, true);
        }

        if (glfwGetKey(Window, GLFW_KEY_W) == GLFW_PRESS){
            zCamera-=0.1;
        }
        if (glfwGetKey(Window, GLFW_KEY_S) == GLFW_PRESS){
            zCamera+=0.1;
        }
        if (glfwGetKey(Window, GLFW_KEY_A) == GLFW_PRESS){
            xCamera-=0.1;
        }
        if (glfwGetKey(Window, GLFW_KEY_D) == GLFW_PRESS){
            xCamera+=0.1;
        }
        if (glfwGetKey(Window, GLFW_KEY_E) == GLFW_PRESS){
            yCamera-=0.1;
        }
        if (glfwGetKey(Window, GLFW_KEY_Q) == GLFW_PRESS){
            yCamera+=0.1;
        }
    }
    
    glfwTerminate();
}

// Função principal
int main() {
    inicializaOpenGL();
    inicializaQuadrado();
    inicializaShader1();
    inicializaRenderizacao();
    
    return 0;
}