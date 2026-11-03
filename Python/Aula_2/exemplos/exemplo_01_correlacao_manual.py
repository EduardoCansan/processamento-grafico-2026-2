import cv2
import numpy as np

def correlacao_manual(imagem, kernel):
    altura_k, largura_k = kernel.shape
    
    # Garante que a matriz do filtro tenha um pixel central exato (ex: 3x3, 5x5)
    if altura_k % 2 == 0 or largura_k % 2 == 0:
        raise ValueError("O kernel deve ter dimensões ímpares.")

    # Calcula quantos pixels o kernel se estende a partir do centro
    raio_y = altura_k // 2
    raio_x = largura_k // 2
    
    # Adiciona uma margem espelhada ao redor da imagem
    # Isso evita erro de "out of bounds" ao aplicar o kernel nos pixels das beiradas
    borda = cv2.copyMakeBorder(
        imagem, raio_y, raio_y, raio_x, raio_x,
        cv2.BORDER_REFLECT_101,
    )
    
    # Matriz vazia para armazenar o resultado temporário com precisão decimal
    saida = np.zeros(imagem.shape, dtype=np.float32)

    # Percorre cada pixel da imagem original (janela deslizante)
    for y in range(imagem.shape[0]):
        for x in range(imagem.shape[1]):
            soma = 0.0
            
            # Sobrepõe o kernel na região atual e faz a soma ponderada
            for ky in range(altura_k):
                for kx in range(largura_k):
                    pixel = float(borda[y + ky, x + kx])
                    peso = float(kernel[ky, kx])
                    soma += pixel * peso
                    
            # Grava o resultado matemático no pixel central da janela
            saida[y, x] = soma

    # Corta os valores que extrapolaram 0-255 e converte de volta para formato de imagem (inteiro 8 bits)
    return np.clip(saida, 0, 255).astype(np.uint8)

entrada = "assets/imagem_base_opencv.jpg"
imagem = cv2.imread(entrada, cv2.IMREAD_GRAYSCALE)
if imagem is None:
    raise FileNotFoundError(f"Não foi possível abrir: {entrada}")

# Cria um filtro de média 3x3 (Filtro passa-baixa)
# Cada uma das 9 posições recebe o peso de 1/9, resultando em um efeito de desfoque (blur)
kernel_media = np.full((3, 3), 1 / 9, dtype=np.float32)

filtrada = correlacao_manual(imagem, kernel_media)

cv2.imshow("Original", imagem)
cv2.imshow("Correlacao manual", filtrada)
cv2.waitKey(0)
cv2.destroyAllWindows()