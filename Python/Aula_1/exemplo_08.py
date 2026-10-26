from pathlib import Path
import cv2
import numpy as np

entrada = Path("assets/imagem_base_opencv.jpg")
imagem = cv2.imread(str(entrada), cv2.IMREAD_GRAYSCALE)

if imagem is None:
    raise FileNotFoundError(f"Não foi possível abrir a imagem: {entrada}")

# Define a intensidade do contraste multiplicando o valor dos pixels
alpha = 1.5
# Compensa o brilho para que os tons médios (valor 128) permaneçam inalterados
beta = 128 * (1 - alpha)

# Aplica a equação matemática: (imagem * alpha) + beta
contraste = cv2.addWeighted(
    imagem,                 # 1. Imagem original que receberá o ajuste
    alpha,                  # 2. Peso da imagem original
    np.zeros_like(imagem),  # 3. Imagem preta auxiliar exigida pela função
    0,                      # 4. Peso zero para ignorar a imagem preta
    beta,                   # 5. Valor constante somado ou subtraído ao final
)

if not cv2.imwrite("assets/contraste.png", contraste):
    raise OSError("Falha ao salvar assets/contraste.png")

cv2.imshow("Original", imagem)
cv2.imshow("Contraste", contraste)
cv2.waitKey(0)
cv2.destroyAllWindows()
