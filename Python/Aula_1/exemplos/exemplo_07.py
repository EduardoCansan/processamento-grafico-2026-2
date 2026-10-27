from pathlib import Path
import cv2

entrada = Path("assets/imagem_base_opencv.jpg")
imagem = cv2.imread(str(entrada), cv2.IMREAD_GRAYSCALE)

if imagem is None:
    raise FileNotFoundError(f"Não foi possível abrir a imagem: {entrada}")

# Aumenta o brilho somando 50 ao valor de cada pixel
# A função do OpenCV trava matematicamente o limite superior em 255 (aritmética de saturação)
mais_clara = cv2.add(imagem, 50)

# O operador padrão de soma causa overflow (estouro de limite) na matriz
# Se um pixel de valor 250 somar 50, ele ultrapassa o limite de 8 bits e reinicia a contagem do zero, resultando na cor 4 (quase preto)
#mais_clara = imagem + 50

# Reduz o brilho subtraindo 50 de cada pixel
# A função do OpenCV trava o limite inferior estritamente em 0
mais_escura = cv2.subtract(imagem, 50)

# O operador padrão de subtração causa underflow na matriz
# Se um pixel de valor 10 subtrair 50, o valor negativo dá a volta no limite da memória e resulta na cor 216 (quase branco)
#mais_escura = imagem - 50

if not cv2.imwrite("assets/brilho_mais_50.png", mais_clara):
    raise OSError("Falha ao salvar assets/brilho_mais_50.png")

if not cv2.imwrite("assets/brilho_menos_50.png", mais_escura):
    raise OSError("Falha ao salvar assets/brilho_menos_50.png")

cv2.imshow("Original", imagem)
cv2.imshow("Mais clara", mais_clara)
cv2.imshow("Mais escura", mais_escura)
cv2.waitKey(0)
cv2.destroyAllWindows()
