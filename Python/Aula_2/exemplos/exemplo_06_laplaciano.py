from pathlib import Path
import cv2

entrada = Path("assets/imagem_base_opencv.jpg")
imagem = cv2.imread(str(entrada), cv2.IMREAD_GRAYSCALE)

if imagem is None:
    raise FileNotFoundError(
        f"Não foi possível abrir a imagem: {entrada}"
    )

# Calcula a derivada de segunda ordem da imagem (operador Laplaciano)
# Diferente do Sobel, que detecta contornos em eixos isolados, o Laplaciano é omnidirecional, detectando bordas em todas as direções de uma só vez
laplaciano = cv2.Laplacian(
    imagem,                            # 1. Imagem original em tons de cinza
    cv2.CV_32F,                        # 2. Profundidade de saída em ponto flutuante. Fundamental pois a segunda derivada naturalmente gera valores negativos
    ksize=3,                           # 3. Tamanho da matriz do filtro (kernel 3x3)
    borderType=cv2.BORDER_REFLECT_101, # 4. Método de espelhamento para processar os pixels encostados nas bordas da imagem
)

# Pega o valor absoluto matemático das derivadas calculadas (transformando números negativos em positivos)
# e converte o resultado de volta para o formato padrão de imagem (inteiros de 0 a 255)
visual = cv2.convertScaleAbs(laplaciano)

if not cv2.imwrite("laplaciano.png", visual):
    raise OSError("Falha ao salvar laplaciano.png")

cv2.imshow("Original", imagem)
cv2.imshow("Laplaciano", visual)
cv2.waitKey(0)
cv2.destroyAllWindows()