// Este exemplo apresenta uma aplicação completa de OpenGL, que renderiza um triângulo na tela.
#include <iostream>
#include <glad/glad.h>
#include <GLFW/glfw3.h>
#include <glm/glm.hpp>
#include <glm/gtc/matrix_transform.hpp>
#include <glm/gtc/type_ptr.hpp>

GLFWwindow* Window = nullptr;
GLuint Shader_programm = 0;
GLuint Vao = 0;
int WIDTH = 800;
int HEIGHT = 600;

// Função callback que é executada sempre que a janela for redimensionada
// Sempre que a tela for redimensionada, salvamos sua nova largura e altura nas variáveis globais acima
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

    // Registramos a função "redimensionaCallback" como sendo a função de redimensionamento
    // Isso significa que a função "redimensionaCallback" será chamada sempre que a janela for redimensionada,
    // seja pelo sistema ou pelo usuário
    glfwSetWindowSizeCallback(Window, redimensionaCallback);

    // Define o contexto atual do GLFW como sendo a janela criada acima. O contexto define
    // em qual janela o OpenGL irá funcionar, o que é essencial para que o programa funcione
    glfwMakeContextCurrent(Window);

    // No C++, precisamos inicializar o GLAD para carregar os ponteiros das funções do OpenGL
    if (!gladLoadGLLoader((GLADloadproc)glfwGetProcAddress)) {
        std::cerr << "Falha ao inicializar o GLAD" << std::endl;
        exit(EXIT_FAILURE);
    }

    // Buscamos informações a respeito do hardware (placa de vídeo) e a versão do OpenGL que a mesma da suporte
    std::cout << "Placa de video: " << glGetString(GL_RENDERER) << std::endl;
    std::cout << "Versao do OpenGL: " << glGetString(GL_VERSION) << std::endl;
}

void inicializaObjetos() {
    // Devido ao fato de que cada objeto que modelarmos possuir, geralmente, uma coleção
    // de buffers de informações referentes aos seus vértices (tais como coordenadas dos vértices,
    // coordenadas de texturas, normais, cores, etc), utilizamos um objeto do tipo Vertex Attribute Object (VAO)
    // que "une" e "representa" todos os buffers do objeto em um único identificador.

    // Nós devemos especificar um VAO para cada objeto que estamos modelando.
    // No caso deste exemplo, vamos renderizar somente 1 triângulo, logo, precisamos somente de
    // 1 VAO para representá-lo.

    // Geramos o VAO, definindo um identificador para ele através glGenVertexArrays
    glGenVertexArrays(1, &Vao);
    // Damos um bind no VAO, setando ele como VAO atual e colocando o mesmo no topo da máquina de estados do OpenGL
    glBindVertexArray(Vao);

    // Definição de um VBO para os vértices do triângulo
    // - Primeiramente, definimos em um vetor de float os vértices do triângulo;
    // - Em seguida, criamos uma cópia desses dados na placa gráfica através de uma unidade denominada Vertex Buffer Object (VBO).
    // Para isso, nós geramos primeiramente um buffer vazio, através da função glGenBuffers, e então setamos esse buffer como buffer 
    // atual na máquina de estados do OpenGL através de glBindBuffer, e por fim copiamos os pontos para esse buffer através do glBufferData.
    float points[] = {

        // triângulo baixo
        0.0f,  0.0f, 0.0f, // centro
        0.5f,-0.5f, 0.0f, // direita baixo
        -0.5f,-0.5f, 0.0f, // esquerda baixo

        // triângulo direita baixo
        0.0f,  0.0f, 0.0f, // centro
        0.67f, 0.57f, 0.0f, // direita cima
        0.5f,-0.5f, 0.0f, // direita baixo

        // triângulo esquerda baixo
        0.0f,  0.0f, 0.0f, // centro
        -0.5f,-0.5f, 0.0f, // esquerda baixo
        -0.67f, 0.57f, 0.0f, // esquerda cima

        // triângulo direita cima
        0.0f,  0.0f, 0.0f,   // centro
        0.0f,  1.0f, 0.0f,   // topo
        0.67f, 0.57f, 0.0f,   // direita cima

        // triângulo esquerda cima
        0.0f,  0.0f, 0.0f,   // centro
        -0.67f, 0.57f, 0.0f,   // esquerda cima
        0.0f,  1.0f, 0.0f     // topo
    };

    GLuint pvbo;
    glGenBuffers(1, &pvbo);
    glBindBuffer(GL_ARRAY_BUFFER, pvbo);
    glBufferData(GL_ARRAY_BUFFER, sizeof(points), points, GL_STATIC_DRAW);
    
    // Ativamos o primeiro atributo do VAO (índice 0), que é o atributo referente ao buffer das posições dos vértices.
    glEnableVertexAttribArray(0);
    
    // E então definimos o layout do buffer de vértices:
    // - o primeiro parâmetro (0) significa que estamos definido o layout do atributo 0 (buffer de vértices)
    // - o segundo parâmetro (3) significa que esse buffer é formado por 3 variáveis (x,y, e z),
    // - o terceiro parâmetro, indica que as variáveis são do tipo float
    // - o quarto parâmetro indica que não desejamos normalizar os valores
    // - o quinto parâmetro é o byte offset entre os atributos, caso tenha sido especificado um único VBO para mais de um tipo de informação
    // - o sexto parâmetro é o offset do primeiro elemento, que no nosso caso, é 0, pois queremos todos os elementos do array
    //   -- Em C++, passamos um ponteiro void (ex: (void*)0) para representar esse offset de memória
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, (void*)0);


    // Definição de um VBO para as cores do triângulo. Observe que passamos como parâmetro o valor 1
    // na chamada ao "glEnableVertexAttribArray", pois estamos ativando o segundo atributo deste VAO,
    // que são as cores dos vértices. Além disso, também passamos o parâmetro 1 na chamada ao "glVertexAttribPointer", 
    // pois estamos definindo o layout do segundo atributo.
    float cores[] = { 

        // Triangulos todos azuis 5x3 = 15
        0.0f, 0.0f, 1.0f, 
        0.0f, 0.0f, 1.0f, 
        0.0f, 0.0f, 1.0f, 
        0.0f, 0.0f, 1.0f, 
        0.0f, 0.0f, 1.0f, 
        0.0f, 0.0f, 1.0f, 
        0.0f, 0.0f, 1.0f, 
        0.0f, 0.0f, 1.0f, 
        0.0f, 0.0f, 1.0f, 
        0.0f, 0.0f, 1.0f, 
        0.0f, 0.0f, 1.0f, 
        0.0f, 0.0f, 1.0f, 
        0.0f, 0.0f, 1.0f, 
        0.0f, 0.0f, 1.0f, 
        0.0f, 0.0f, 1.0f
    };
    
    GLuint cvbo;
    glGenBuffers(1, &cvbo);
    glBindBuffer(GL_ARRAY_BUFFER, cvbo);
    glBufferData(GL_ARRAY_BUFFER, sizeof(cores), cores, GL_STATIC_DRAW);
    glEnableVertexAttribArray(1);
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, (void*)0);
}

void inicializaShaders() {
    // Especificação do Vertex Shader:
    // - O Vertex Shader é responsável por determinar a posição final de cada vértice do objeto
    // - a primeira linha especifica a versão da GLSL que estamos utilizando, no caso, 4.0.0
    // - em seguida definimos uma variável de entrada (in) do tipo vec3 (3 valores) chamada vertex_posicao,
    // que receberá os valores dos vértices do triangulo no VAO especificado no código
    // - a posição final do vértice é definida na variável gl_Position, que neste caso será o mesmo
    // valor de entrada
    // - a saída gl_Position deve ser um dado do tipo vec4 (4 valores), por isso adicionamos 1.0 no final
    // para o valor de w, indicando que o mesmo representa um ponto no espaço
    const char* vertex_shader = 
        "#version 400\n"
        "layout(location = 0) in vec3 vertex_posicao;\n"
        "layout(location = 1) in vec3 vertex_cores;\n"
        "out vec3 cores;\n"
        "void main () {\n"
        "    cores = vertex_cores;\n"
        "    gl_Position = vec4(vertex_posicao, 1.0);\n"
        "}\n";

    // Como os shaders são um programa "a parte", precisamos compilá-lo e verificar se não houve nenhum erro de compilação
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

    // Especificação do Fragment Shader:
    // - o Fragment Shader é responsável por determinar a cor de cada fragmento da superfície do objeto
    // - a primeira linha especifica a versão da GLSL que estamos utilizando, no caso, 4.0.0
    // - a cor final é determinada pela variável frag_colour, que neste caso é enviada a partir da cor interpolada
    const char* fragment_shader = 
        "#version 400\n"
        "in vec3 cores;\n"
        "out vec4 frag_colour;\n"
        "void main () {\n"
        "    frag_colour = vec4(cores, 1.0);\n"
        "}\n";

    // Do mesmo modo que o vertex shader, precisamos compilar o fragment shader e verificar se não houve nenhum erro de compilação
    GLuint fs = glCreateShader(GL_FRAGMENT_SHADER);
    glShaderSource(fs, 1, &fragment_shader, NULL);
    glCompileShader(fs);
    
    glGetShaderiv(fs, GL_COMPILE_STATUS, &success);
    if (!success) {
        glGetShaderInfoLog(fs, 512, NULL, infoLog);
        std::cerr << "Erro no fragment shader:\n" << infoLog << std::endl;
    }

    // Especificação do Shader Programm:
    // Após compilarmos os shaders, precisamos combiná-los em um único programa, denominado GPU Shader Program.
    // Para isso, chamamos a função glCreateProgram e glAttachShader passando os dois shaders que irão formar o nosso shader program
    // e testamos se não houve nenhum erro de linkagem
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
    // O triangulo é redesenhado o tempo todo, dentro de um laço de repetição
    // que é executado enquanto a janela não for fechada
    while (!glfwWindowShouldClose(Window)) {
        // Limpamos o buffer de cores da tela
        glClear(GL_COLOR_BUFFER_BIT);
        glClearColor(0.2f, 0.3f, 0.3f, 1.0f);

        // Redefinimos o tamanho da viewport para o tamanho atual da janela, a cada frame, de modo que
        // o desenho se ajuste de acordo com o tamanho da tela
        glViewport(0, 0, WIDTH, HEIGHT);

        // Especificamos qual Shader Programm vamos utilizar
        glUseProgram(Shader_programm);

        // Setamos o objeto Vao como sendo o VAO atual na máquina de estados do OpenGL
        glBindVertexArray(Vao);

        // Desenhamos o triângulo especificado no vao
        glDrawArrays(GL_TRIANGLES, 0, 15);

        // Atualiamos outros eventos, tais como entradas pelo teclado, mouse, etc, caso ocorram
        glfwPollEvents();

        // Renderizamos na tela tudo aquilo que foi desenhado logo acima
        glfwSwapBuffers(Window);

        // Verificamos se a tecla ESC foi pressionada. Caso positivo, definimos que a tela deve ser
        // fechada na próxima volta do laço.
        // Para testar se outras teclas foram pressionadas, verifique o seguinte link:
        // http://www.glfw.org/docs/latest/group__input.html
        if (glfwGetKey(Window, GLFW_KEY_ESCAPE) == GLFW_PRESS) {
            glfwSetWindowShouldClose(Window, true);
        }
    }
    
    glfwTerminate();
}

// Função principal
int main() {
    inicializaOpenGL();
    inicializaObjetos();
    inicializaShaders();
    inicializaRenderizacao();
    
    return 0;
}