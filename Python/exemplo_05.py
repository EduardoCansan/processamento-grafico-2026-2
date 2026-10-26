from pathlib import Path
import cv2

entrada = Path("assets/imagem_base_opencv.jpg")
saida = Path("copia_da_imagem.png")
imagem = cv2.imread(str(entrada))
if imagem is None:
    raise FileNotFoundError(f"Não foi possível abrir a imagem: {entrada}")
sucesso = cv2.imwrite(str(saida), imagem)
if not sucesso:
    raise OSError(f"Não foi possível salvar: {saida}")
print(f"Imagem salva em: {saida.resolve()}")
