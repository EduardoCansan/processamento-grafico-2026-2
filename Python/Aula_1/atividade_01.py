from pathlib import Path
import cv2

caminho = Path("assets/imagem_base_opencv.jpg")
imagem = cv2.imread(str(caminho))
if imagem is None:
    raise FileNotFoundError(f"Não foi possível abrir a imagem: {caminho}")
altura, largura, canais = imagem.shape
print("Largura:", largura)
print("Altura:", altura)
print("Canais:", canais)
print("Total de pixels:", largura * altura)
