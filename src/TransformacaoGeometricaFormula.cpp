// Este exemplo apresenta uma aplicação completa de OpenGL, que renderiza um triângulo e um quadrado na tela.
#include <iostream>
#include <string>
#include <fstream>
#include <sstream>
#include <math.h>
#include <glad/glad.h>
#include <GLFW/glfw3.h>
#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>
#include <glm/gtc/type_ptr.hpp>

GLFWwindow* Window = nullptr;
GLuint Shader_programm;
GLuint Vao_quadrado;
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
    glGenVertexArrays(1, &Vao_quadrado);
    glBindVertexArray(Vao_quadrado);

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
}

void inicializaShader1() {
    // 1. Lê o código dos arquivos externos (eles precisam estar na pasta assets/shaders do projeto)
    std::string vertexCode = leShaderDoArquivo("../assets/shaders/vertex_shader.glsl");
    std::string fragmentCode = leShaderDoArquivo("../assets/shaders/fragment_shader.glsl");

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
    float R = 0.0, G = 0.0, B = 0.0;
    float Tx = 0.0, Ty = 0.0;
    float Sx = 1.0, Sy = 1.0;
    float angulo = 80.0;

    while (!glfwWindowShouldClose(Window)) {
        //Limpa a tela
        glClear(GL_COLOR_BUFFER_BIT);
        glClearColor(0.2f, 0.3f, 0.3f, 1.0f);
        glViewport(0, 0, WIDTH, HEIGHT);

        
        glUseProgram(Shader_programm);

        //buscamos a localização da variável "cor" no shader
        int corLocalizacao = glGetUniformLocation(Shader_programm, "cor");
        //enviamos para o shader um valor para a cor
        glUniform4f(corLocalizacao, R, G, B, 1.0);

        //TRANSLAÇÃO
        //buscamos a localização das variáveis Tx e Ty no shader
        int TxLocalizacao = glGetUniformLocation(Shader_programm, "Tx");
        int TyLocalizacao = glGetUniformLocation(Shader_programm, "Ty");
        //enviamos um valor para Tx e Ty
        glUniform1f(TxLocalizacao, Tx);
        glUniform1f(TyLocalizacao, Ty);

        //ESCALA
        //buscamos a localização das variáveis Sx e Sy no shader
        int SxLocalizacao = glGetUniformLocation(Shader_programm, "Sx");
        int SyLocalizacao = glGetUniformLocation(Shader_programm, "Sy");
        //enviamos um valor para Sx e Sy
        glUniform1f(SxLocalizacao, Sx);
        glUniform1f(SyLocalizacao, Sy);

        //ROTAÇÃO
        //buscamos a localização da variável "angulo" no shader
        int anguloLocalizacao = glGetUniformLocation(Shader_programm, "angulo");
        //enviamos o valor para 'angulo', convertido para radianos
        angulo = 30*glfwGetTime(); //usamos o TEMPO como angulo
        std::cout << angulo << std::endl;
        float radianos = angulo * (M_PI / 180.0);
        glUniform1f(anguloLocalizacao, radianos);

        glBindVertexArray(Vao_quadrado);
        glDrawArrays(GL_TRIANGLES, 0, 6);


        glfwPollEvents();

        glfwSwapBuffers(Window);

        if (glfwGetKey(Window, GLFW_KEY_ESCAPE) == GLFW_PRESS) {
            glfwSetWindowShouldClose(Window, true);
        }

        //Testamos se o usuário pressionou R, G ou B para aumentar o valor do RGB e resetar quando chega em 1
        if (glfwGetKey(Window, GLFW_KEY_R) == GLFW_PRESS) {
            R+=0.01;
            if(R > 1.0) R = 0.0;
        }
        if (glfwGetKey(Window, GLFW_KEY_G) == GLFW_PRESS) {
            G+=0.01;
            if(G > 1.0) G = 0.0;
        }
        if (glfwGetKey(Window, GLFW_KEY_B) == GLFW_PRESS) {
            B+=0.01;
            if(B > 1.0) B = 0.0;
        }

        //testamos se o usuário apertou para A ou D (mexe no Tx)
        if (glfwGetKey(Window, GLFW_KEY_A) == GLFW_PRESS) {
            Tx-=0.02;
        }
        if (glfwGetKey(Window, GLFW_KEY_D) == GLFW_PRESS) {
            Tx+=0.02;
        }
        //testamos se o usuário apertou para W ou S (mexe no Ty)
        if (glfwGetKey(Window, GLFW_KEY_S) == GLFW_PRESS) {
            Ty-=0.02;
        }
        if (glfwGetKey(Window, GLFW_KEY_W) == GLFW_PRESS) {
            Ty+=0.02;
        }

        //testamos se o usuário apertou para para direita ou esquerda (mexe no Sx)
        if (glfwGetKey(Window, GLFW_KEY_LEFT) == GLFW_PRESS) {
            Sx-=0.02;
        }
        if (glfwGetKey(Window, GLFW_KEY_RIGHT) == GLFW_PRESS) {
            Sx+=0.02;
        }
        //testamos se o usuário apertou para para cima ou baixo (mexe no Sy)
        if (glfwGetKey(Window, GLFW_KEY_DOWN) == GLFW_PRESS) {
            Sy-=0.02;
        }
        if (glfwGetKey(Window, GLFW_KEY_UP) == GLFW_PRESS) {
            Sy+=0.02;
        }

        //testamos se o usuário apertou P (mexe no angulo)
        /*if (glfwGetKey(Window, GLFW_KEY_P) == GLFW_PRESS) {
            angulo+=1.0;
            if(angulo >=360) angulo = 360-angulo;
            std::cout << angulo << std::endl;
        }*/
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