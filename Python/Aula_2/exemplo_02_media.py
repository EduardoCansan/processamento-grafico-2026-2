from pathlib import Path
import cv2

entrada = Path("assets/imagem_base_opencv.jpg")
imagem = cv2.imread(str(entrada))

if imagem is None:
    raise FileNotFoundError(
        f"Não foi possível abrir a imagem: {entrada}"
    )

# Aplica um filtro de média (box filter) usando uma janela de 3x3 pixels
# Cada pixel se torna a média aritmética dele mesmo e de seus 8 vizinhos, causando um leve desfoque
media_3x3 = cv2.blur(
    imagem,                            # 1. Imagem original
    (3, 3),                            # 2. Tamanho do kernel (largura, altura). Define a área da vizinhança
    borderType=cv2.BORDER_REFLECT_101, # 3. Estratégia de borda: espelha os pixels da extremidade para calcular os cantos sem erro
)

# Aplica o mesmo algoritmo matematico, mas com uma janela maior de 7x7 pixels
# Como a média agora engloba 49 pixels para cada cálculo, o efeito de desfoque (blur) será bem mais forte
media_7x7 = cv2.blur(
    imagem,
    (7, 7),
    borderType=cv2.BORDER_REFLECT_101,
)

if not cv2.imwrite("media_3x3.png", media_3x3):
    raise OSError("Falha ao salvar media_3x3.png")
if not cv2.imwrite("media_7x7.png", media_7x7):
    raise OSError("Falha ao salvar media_7x7.png")

cv2.imshow("Original", imagem)
cv2.imshow("Media 3x3", media_3x3)
cv2.imshow("Media 7x7", media_7x7)
cv2.waitKey(0)
cv2.destroyAllWindows()