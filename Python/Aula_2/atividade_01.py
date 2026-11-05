import cv2
import numpy as np

entrada = "assets/imagem_base_opencv.jpg"
imagem = cv2.imread(entrada, cv2.IMREAD_GRAYSCALE)
if imagem is None:
    raise FileNotFoundError(f"Não foi possível abrir: {entrada}")

# Seleciona uma região de no máximo 150x150 pixels
imagem = imagem[:150, :150]

# Filtro da média 3x3, como no exemplo de correlação manual
kernel_media = np.full((3, 3), 1 / 9, dtype=np.float32)
borda = cv2.copyMakeBorder(imagem, 1, 1, 1, 1, cv2.BORDER_REFLECT_101)
saida = np.zeros(imagem.shape, dtype=np.float32)

for y in range(imagem.shape[0]):
    for x in range(imagem.shape[1]):
        soma = 0.0
        for ky in range(3):
            for kx in range(3):
                pixel = float(borda[y + ky, x + kx])
                peso = float(kernel_media[ky, kx])
                soma += pixel * peso
        saida[y, x] = soma

manual = np.clip(saida, 0, 255).astype(np.uint8)
media_opencv = cv2.blur(imagem, (3, 3), borderType=cv2.BORDER_REFLECT_101)

# Compara os resultados (a conversão manual pode truncar decimais)
diferenca = cv2.absdiff(manual, media_opencv)
print("Maior diferença:", diferenca.max())

cv2.imwrite("atividade_01_manual.png", manual)
cv2.imwrite("atividade_01_blur.png", media_opencv)
cv2.imshow("Original", imagem)
cv2.imshow("Media manual", manual)
cv2.imshow("cv2.blur", media_opencv)
cv2.waitKey(0)
cv2.destroyAllWindows()
