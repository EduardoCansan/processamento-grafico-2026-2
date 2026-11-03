from pathlib import Path
import cv2

entrada = Path("assets/imagem_base_opencv.jpg")
imagem = cv2.imread(str(entrada))

if imagem is None:
    raise FileNotFoundError(
        f"Não foi possível abrir a imagem: {entrada}"
    )

# Aplica um filtro passa-baixa Gaussiano para suavizar a imagem
# Diferente do filtro de média, o Gaussiano dá mais peso ao pixel central e menos aos das bordas do kernel, borrando a imagem enquanto preserva melhor os contornos originais
gaussiano = cv2.GaussianBlur(
    imagem,                            # 1. Imagem original
    (7, 7),                            # 2. Tamanho do kernel (largura, altura). Deve ser ímpar
    sigmaX=0,                          # 3. Desvio padrão da curva no eixo X. O valor 0 faz o OpenCV calcular isso automaticamente com base no tamanho do kernel
    borderType=cv2.BORDER_REFLECT_101, # 4. Estratégia de espelhamento para processar os pixels encostados nas beiradas da imagem
)

if not cv2.imwrite("gaussiano_7x7.png", gaussiano):
    raise OSError("Falha ao salvar gaussiano_7x7.png")

cv2.imshow("Original", imagem)
cv2.imshow("Gaussiano 7x7", gaussiano)
cv2.waitKey(0)
cv2.destroyAllWindows()