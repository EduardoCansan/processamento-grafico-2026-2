from pathlib import Path
import cv2

entrada = Path("assets/imagem_base_opencv.jpg")
imagem = cv2.imread(str(entrada), cv2.IMREAD_GRAYSCALE)

if imagem is None:
    raise FileNotFoundError(f"Não foi possível abrir a imagem: {entrada}")

# Inverte os valores de todos os pixels da imagem (ex: branco vira preto)
# Matematicamente, faz a operação (255 - valor do pixel), criando um efeito de negativo
negativa = cv2.bitwise_not(imagem)

if not cv2.imwrite("assets/imagem_negativa.png", negativa):
    raise OSError("Falha ao salvar assets/imagem_negativa.png")

cv2.imshow("Original", imagem)
cv2.imshow("Negativa", negativa)
cv2.waitKey(0)
cv2.destroyAllWindows()
