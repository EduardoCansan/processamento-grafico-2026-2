from pathlib import Path
import cv2
import numpy as np

entrada = Path("assets/imagem_base_opencv.jpg")
imagem = cv2.imread(str(entrada))

if imagem is None:
    raise FileNotFoundError(
        f"Não foi possível abrir a imagem: {entrada}"
    )

# Cria uma matriz de convolução (kernel) para realçar a nitidez das bordas (sharpening)
# O valor central alto (5) amplifica a intensidade do pixel atual, enquanto os vizinhos negativos subtraem a intensidade ao redor
# A soma total de todos os elementos da matriz é exatamente 1, o que garante que o brilho global da imagem original seja preservado
kernel = np.array([
    [ 0, -1,  0],
    [-1,  5, -1],
    [ 0, -1,  0],
], dtype=np.float32)

# Aplica o filtro espacial linear passando a nossa matriz personalizada
nitida = cv2.filter2D(
    imagem,                            # 1. Imagem original em tons de cinza ou colorida
    ddepth=-1,                         # 2. Profundidade de dados da saída. O valor negativo forçará a imagem resultante a ter o exato mesmo formato da entrada (ex: inteiro de 8 bits)
    kernel=kernel,                     # 3. A matriz de pesos matemáticos definida acima
    borderType=cv2.BORDER_REFLECT_101, # 4. Estratégia de espelhamento para processar os pixels encostados nas beiradas da imagem
)

if not cv2.imwrite("imagem_nitida.png", nitida):
    raise OSError("Falha ao salvar imagem_nitida.png")

cv2.imshow("Original", imagem)
cv2.imshow("Nitidez", nitida)
cv2.waitKey(0)
cv2.destroyAllWindows()