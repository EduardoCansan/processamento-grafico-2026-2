from pathlib import Path
import cv2

entrada = Path('assets/imagem_base_opencv.jpg')
imagem = cv2.imread(str(entrada), cv2.IMREAD_GRAYSCALE)
if imagem is None:
    raise FileNotFoundError(f'Não foi possível abrir a imagem: {entrada}')

for valor in [80, 127, 180]:
    limiar, binaria = cv2.threshold(imagem, valor, 255, cv2.THRESH_BINARY)
    brancos = cv2.countNonZero(binaria)
    total = imagem.shape[0] * imagem.shape[1]
    porcentagem = brancos * 100 / total
    print('Limiar:', limiar, 'Pixels brancos:', brancos, 'Porcentagem:', f'{porcentagem:.2f}%')
    saida = Path(f'saidas/binaria_{valor}.png')
    if not cv2.imwrite(str(saida), binaria):
        raise OSError(f'Falha ao salvar: {saida}')

# Limiar 127: separa melhor o texto escuro do cartão branco entre os três
# valores testados, mantendo o fundo do cartão claro e as letras escuras.
