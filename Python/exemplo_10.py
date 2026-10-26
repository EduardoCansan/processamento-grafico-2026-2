from pathlib import Path
import cv2

entrada = Path("assets/imagem_base_opencv.jpg")
imagem = cv2.imread(str(entrada), cv2.IMREAD_GRAYSCALE)

if imagem is None:
    raise FileNotFoundError(f"Não foi possível abrir a imagem: {entrada}")

# Converte a imagem para preto e branco dividindo os tons pelo valor de corte
# Retorna o valor de limiar efetivamente usado e a nova imagem gerada
limiar_usado, binaria = cv2.threshold(
    imagem,             # 1. Imagem original em tons de cinza
    127,                # 2. Valor de corte. Pixels acima desse valor vão mudar
    255,                # 3. Novo valor para os pixels que passaram do corte (255 = branco)
    cv2.THRESH_BINARY,  # 4. Método aplicado (maior que 127 vira branco, menor ou igual vira preto)
)

print("Limiar usado:", limiar_usado)

if not cv2.imwrite("imagem_binaria.png", binaria):
    raise OSError("Falha ao salvar imagem_binaria.png")

cv2.imshow("Tons de cinza", imagem)
cv2.imshow("Binaria", binaria)
cv2.waitKey(0)
cv2.destroyAllWindows()