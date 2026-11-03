from pathlib import Path
import time
import cv2
import numpy as np

caminho = Path("assets/aula8_video_exemplo.avi")
captura = cv2.VideoCapture(str(caminho))

if not captura.isOpened():
    raise RuntimeError(f"Não foi possível abrir o vídeo: {caminho}")

# Extrai apenas o primeiro quadro do arquivo para realizar o comparativo de velocidade
sucesso, frame = captura.read()
captura.release()

if not sucesso:
    raise RuntimeError("Não foi possível capturar um frame.")

altura, largura = frame.shape[:2]

# Teste 1: Laços nativos do Python (Pior desempenho)
# Processar a imagem pixel por pixel usando "for" no Python é extremamente lento.
# A conversão para int16 é obrigatória: se somarmos 40 a um pixel de valor 250 no formato padrão de 8 bits, o valor passa de 255, "dá a volta" e vira 34, estragando a cor antes de podermos cortá-la no limite.
inicio = time.perf_counter()
saida_laco = frame.copy()
for y in range(altura):
    for x in range(largura):
        pixel = frame[y, x].astype(np.int16) + 40
        saida_laco[y, x] = np.clip(pixel, 0, 255)
tempo_laco = (time.perf_counter() - inicio) * 1000

# Teste 2: Operações em lote com NumPy (Desempenho intermediário)
# O NumPy aplica a conta na matriz inteira de uma vez, rodando código otimizado em C nos bastidores.
# É muito mais rápido, mas gasta muita memória porque cria uma cópia inteira da imagem em 16 bits apenas para fazer a soma em segurança antes de voltar para 8 bits.
inicio = time.perf_counter()
saida_numpy = np.clip(frame.astype(np.int16) + 40, 0, 255).astype(np.uint8)
tempo_numpy = (time.perf_counter() - inicio) * 1000

# Teste 3: Funções nativas do OpenCV (Melhor desempenho)
# O OpenCV é feito especificamente para lidar com imagens de forma eficiente.
# Ele soma os valores e automaticamente trava o teto no 255 (saturação). Como ele faz isso direto na fonte, não precisa gastar memória convertendo a imagem para 16 bits.
inicio = time.perf_counter()
saida_opencv = cv2.add(frame, 40)
tempo_opencv = (time.perf_counter() - inicio) * 1000

print(f"Laço Python: {tempo_laco:8.2f} ms")
print(f"NumPy:       {tempo_numpy:8.2f} ms")
print(f"OpenCV:      {tempo_opencv:8.2f} ms")

assert np.array_equal(saida_numpy, saida_opencv)