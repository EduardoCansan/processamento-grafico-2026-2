from pathlib import Path
import cv2
import numpy as np

entrada = Path('assets/imagem_base_opencv.jpg')
imagem = cv2.imread(str(entrada))
if imagem is None:
    raise FileNotFoundError(f'Não foi possível abrir a imagem: {entrada}')

cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
brilho_mais = cv2.add(cinza, 50)
brilho_menos = cv2.subtract(cinza, 50)
alpha = 1.5
beta = 128 * (1 - alpha)
contraste = cv2.addWeighted(cinza, alpha, np.zeros_like(cinza), 0, beta)
negativa = cv2.bitwise_not(cinza)

resultados = {
    'cinza.png': cinza,
    'brilho_mais.png': brilho_mais,
    'brilho_menos.png': brilho_menos,
    'contraste.png': contraste,
    'negativa.png': negativa,
}
for nome, resultado in resultados.items():
    saida = Path('saidas') / nome
    print(nome, 'Shape:', resultado.shape, 'Dtype:', resultado.dtype)
    if not cv2.imwrite(str(saida), resultado):
        raise OSError(f'Falha ao salvar: {saida}')
