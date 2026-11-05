import cv2
import numpy as np

entrada = "assets/imagem_base_opencv.jpg"
imagem = cv2.imread(entrada, cv2.IMREAD_GRAYSCALE)
if imagem is None:
    raise FileNotFoundError(f"Não foi possível abrir: {entrada}")

kernel_nitidez = np.array([
    [0, -1, 0],
    [-1, 5, -1],
    [0, -1, 0]
], dtype=np.float32)

kernel_contornos = np.array([
    [-1, -1, -1],
    [-1, 8, -1],
    [-1, -1, -1]
], dtype=np.float32)

kernel_relevo = np.array([
    [-2, -1, 0],
    [-1, 1, 1],
    [0, 1, 2]
], dtype=np.float32)

# Soma 1: mantém a intensidade em regiões constantes (nitidez e relevo).
# Soma 0: regiões constantes ficam com intensidade 0 (contornos).
print("Soma nitidez:", kernel_nitidez.sum())
print("Soma contornos:", kernel_contornos.sum())
print("Soma relevo:", kernel_relevo.sum())

nitidez = cv2.filter2D(imagem, ddepth=-1, kernel=kernel_nitidez, borderType=cv2.BORDER_REFLECT_101)
contornos = cv2.filter2D(imagem, ddepth=-1, kernel=kernel_contornos, borderType=cv2.BORDER_REFLECT_101)
relevo = cv2.filter2D(imagem, ddepth=-1, kernel=kernel_relevo, borderType=cv2.BORDER_REFLECT_101)

cv2.imwrite("atividade_03_nitidez.png", nitidez)
cv2.imwrite("atividade_03_contornos.png", contornos)
cv2.imwrite("atividade_03_relevo.png", relevo)

cv2.imshow("Original", imagem)
cv2.imshow("Nitidez", nitidez)
cv2.imshow("Contornos", contornos)
cv2.imshow("Relevo", relevo)
cv2.waitKey(0)
cv2.destroyAllWindows()
