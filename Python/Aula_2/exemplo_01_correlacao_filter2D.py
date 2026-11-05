import cv2
import numpy as np

entrada = "assets/imagem_base_opencv.jpg"
# Carrega a imagem descartando as cores para alocar diretamente uma matriz de apenas um canal de intensidade (tons de cinza)
imagem = cv2.imread(entrada, cv2.IMREAD_GRAYSCALE)
if imagem is None:
    raise FileNotFoundError(f"Não foi possível abrir: {entrada}")

# Constrói o kernel matemático do filtro passa-baixa de média
# É uma matriz 3x3 onde cada posição vale exatamente 1/9
# Como a soma total de todos os pesos da matriz é igual a 1, o algoritmo preserva a luminosidade geral da imagem original
kernel_media = np.full((3, 3), 1 / 9, dtype=np.float32)

# Executa a operação de convolução bidimensional deslizando a matriz do kernel por todos os pixels
filtrada = cv2.filter2D(
    imagem,
    # Mantém o tipo de dado da matriz de saída idêntico ao da original (inteiros de 8 bits)
    ddepth=-1,
    kernel=kernel_media,
    # Define a matemática para calcular os pixels que ficam nas extremidades da foto
    # BORDER_REFLECT_101 espelha os valores internos como um reflexo de espelho no limite da imagem, evitando bordas pretas falsas
    borderType=cv2.BORDER_REFLECT_101,
)

cv2.imshow("Original", imagem)
cv2.imshow("filter2D", filtrada)
cv2.waitKey(0)
cv2.destroyAllWindows()