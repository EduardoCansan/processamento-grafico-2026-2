from pathlib import Path
import cv2

caminho = Path("assets/imagem_base_opencv.jpg")
imagem = cv2.imread(str(caminho))

if imagem is None:
    raise FileNotFoundError(f"Não foi possível abrir a imagem: {caminho}")

linha = 100
coluna = 250
b, g, r = imagem[linha, coluna]

print(f"Posição: linha={linha}, coluna={coluna}")
print(f"Azul: {b}")
print(f"Verde: {g}")
print(f"Vermelho: {r}")
