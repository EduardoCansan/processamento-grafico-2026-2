from pathlib import Path
import cv2

entrada = Path('assets/imagem_base_opencv.jpg')
saida = Path('saidas/exercicio_1.png')
imagem = cv2.imread(str(entrada))
if imagem is None:
    raise FileNotFoundError(f'Não foi possível abrir a imagem: {entrada}')

altura, largura, canais = imagem.shape
print('Largura:', largura)
print('Altura:', altura)
print('Canais:', canais)
print('Dtype:', imagem.dtype)
print('Total de pixels:', altura * largura)
print('Pixel central (BGR):', imagem[altura // 2, largura // 2])

# Faz uma cópia para preservar a imagem original
alterada = imagem.copy()
alterada[100:200, 100:200] = (0, 0, 255)
if not cv2.imwrite(str(saida), alterada):
    raise OSError(f'Falha ao salvar: {saida}')
