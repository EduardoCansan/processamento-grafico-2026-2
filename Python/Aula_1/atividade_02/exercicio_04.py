from pathlib import Path
import cv2
import numpy as np

entrada = Path('assets/imagem_base_opencv.jpg')
imagem = cv2.imread(str(entrada))
if imagem is None:
    raise FileNotFoundError(f'Não foi possível abrir a imagem: {entrada}')

cartao = imagem[370:640, 430:860]
cinza = cv2.cvtColor(cartao, cv2.COLOR_BGR2GRAY)
alpha = 1.5
beta = 128 * (1 - alpha)
contraste = cv2.addWeighted(cinza, alpha, np.zeros_like(cinza), 0, beta)
limiar, binaria = cv2.threshold(contraste, 127, 255, cv2.THRESH_BINARY)

resultados = {
    'cartao_original.png': cartao,
    'cartao_cinza.png': cinza,
    'cartao_contraste.png': contraste,
    'cartao_binaria.png': binaria,
}
for nome, resultado in resultados.items():
    saida = Path('saidas') / nome
    if not cv2.imwrite(str(saida), resultado):
        raise OSError(f'Falha ao salvar: {saida}')
