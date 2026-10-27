from pathlib import Path
import cv2
import numpy as np

ENTRADAS = [Path('assets') / 'babuino.tiff']
SAIDAS = Path('saidas')
SAIDAS.mkdir(parents=True, exist_ok=True)

for entrada in ENTRADAS:
    imagem = cv2.imread(str(entrada))
    if imagem is None:
        raise FileNotFoundError(f'Não foi possível carregar a imagem: {entrada}')

    print(f'Arquivo: {entrada.name}')
    print(f'Shape: {imagem.shape}')
    print(f'Dtype: {imagem.dtype}')

    cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)
    brilho = cv2.add(cinza, 50)
    alpha = 1.5
    beta = 128 * (1 - alpha)
    contraste = cv2.addWeighted(cinza, alpha, np.zeros_like(cinza), 0, beta)
    negativa = cv2.bitwise_not(cinza)
    limiar, binaria = cv2.threshold(cinza, 127, 255, cv2.THRESH_BINARY)
    print(f'Limiar utilizado: {limiar}\n')

    pasta = SAIDAS / entrada.stem
    pasta.mkdir(parents=True, exist_ok=True)
    resultados = {
        '01_original.png': imagem,
        '02_cinza.png': cinza,
        '03_brilho.png': brilho,
        '04_contraste.png': contraste,
        '05_negativa.png': negativa,
        '06_binaria.png': binaria,
    }
    for nome, resultado in resultados.items():
        destino = pasta / nome
        if not cv2.imwrite(str(destino), resultado):
            raise OSError(f'Falha ao salvar: {destino}')
        print(f'Salvo: {destino.relative_to(SAIDAS)}')
