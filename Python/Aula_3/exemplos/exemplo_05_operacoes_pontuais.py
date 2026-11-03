from pathlib import Path
import time
import cv2
import numpy as np

caminho = Path("assets/aula8_video_exemplo.avi")
captura = cv2.VideoCapture(str(caminho))

if not captura.isOpened():
    raise RuntimeError(f"Não foi possível abrir o vídeo: {caminho}")

# Obtém o FPS original do vídeo para calcular e manter a velocidade correta da reprodução
fps = captura.get(cv2.CAP_PROP_FPS)
periodo = 1 / fps if fps > 0 else 1 / 30

gama = 1.5

# Cria uma tabela de mapeamento rápido (Look-Up Table ou LUT) para o ajuste de Gama
# Em vez de calcular a fórmula complexa para cada pixel em todos os frames, calculamos as 256 possibilidades de cor uma única vez
# Guardar esses resultados na memória e apenas trocar os valores acelera drasticamente o processamento do vídeo
tabela_gama = np.array(
    [255 * (i / 255) ** (1 / gama) for i in range(256)],
    dtype=np.uint8,
)

while True:
    inicio = time.perf_counter()
    sucesso, frame = captura.read()
    
    # Reinicia o vídeo ao chegar no final, criando um loop contínuo
    if not sucesso:
        captura.set(cv2.CAP_PROP_POS_FRAMES, 0)
        continue

    # Aumenta o brilho da imagem somando o valor 40 a todos os pixels
    # O OpenCV trava automaticamente o limite máximo em 255 (branco absoluto), evitando distorções nas cores
    brilho = cv2.add(frame, 40)

    # Ajusta o contraste multiplicando as cores por um fator de ganho (alpha)
    # Como a multiplicação também afeta a luminosidade geral, usamos a variável beta para corrigir o brilho de volta ao normal, focando estritamente no contraste
    alpha = 1.5
    beta = 128 * (1 - alpha)
    contraste = cv2.addWeighted(
        frame, alpha, np.zeros_like(frame), 0, beta
    )

    # Cria o efeito de imagem negativa invertendo os valores (o que é escuro vira claro e vice versa)
    negativo = cv2.bitwise_not(frame)
    
    # Aplica a correção de Gama usando a tabela que salvamos na memória no início do código
    # Ajustar o Gama revela detalhes que estavam escondidos nas sombras sem clarear demais as partes que já estão iluminadas
    corrigida = cv2.LUT(frame, tabela_gama)

    # Converte a imagem colorida para tons de cinza, preparando a matriz para o corte em preto e branco
    cinza = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Binariza a imagem (thresholding) dividindo tudo rigidamente em preto e branco
    # Pixels mais claros que a metade da escala (127) viram branco absoluto, e o resto vira preto absoluto
    _, binaria = cv2.threshold(
        cinza, 127, 255, cv2.THRESH_BINARY
    )

    cv2.imshow("Original", frame)
    cv2.imshow("Brilho", brilho)
    cv2.imshow("Contraste", contraste)
    cv2.imshow("Negativo", negativo)
    cv2.imshow("Correcao gama", corrigida)
    cv2.imshow("Limiarizacao", binaria)

    # Desconta o tempo de processamento do ciclo para garantir que a espera do waitKey mantenha o FPS correto
    gasto = time.perf_counter() - inicio
    espera_ms = max(1, int((periodo - gasto) * 1000))

    if cv2.waitKey(espera_ms) & 0xFF == ord("q"):
        break

captura.release()
cv2.destroyAllWindows()