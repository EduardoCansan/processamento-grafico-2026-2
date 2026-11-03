from pathlib import Path
import time
import cv2

fonte = Path("assets/aula8_video_exemplo.avi")
captura = cv2.VideoCapture(str(fonte))
if not captura.isOpened():
    raise FileNotFoundError(f"Não foi possível abrir: {fonte}")

# Obtém o FPS original para calcular e manter a velocidade correta da reprodução
fps = captura.get(cv2.CAP_PROP_FPS)
periodo = 1 / fps if fps > 0 else 1 / 30

frame_anterior = None

while True:
    inicio = time.perf_counter()
    sucesso, frame = captura.read()
    
    # Reinicia o vídeo ao chegar no final, criando um loop contínuo
    if not sucesso:
        captura.set(cv2.CAP_PROP_POS_FRAMES, 0)
        # Limpa o frame salvo para não comparar o fim do vídeo com o começo
        frame_anterior = None  
        continue

    # Converte a imagem colorida para tons de cinza, simplificando o processamento
    cinza = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Aplica o desfoque Gaussiano para suavizar a imagem
    # Isso evita que pequenas granulações ou ruídos de compressão sejam confundidos com movimento real
    atual = cv2.GaussianBlur(cinza, (15, 15), 0)

    # Salva a imagem atual para servir de comparação na próxima repetição do laço
    if frame_anterior is None:
        frame_anterior = atual
        continue

    # Calcula a diferença absoluta pixel a pixel entre o frame atual e o anterior
    # Isso garante que qualquer mudança na imagem gere um valor positivo, destacando apenas o que se moveu
    diferenca = cv2.absdiff(frame_anterior, atual)
    
    # Aplica a limiarização (thresholding) para binarizar a imagem
    # Variações sutis (abaixo de 12) viram preto absoluto, ignorando pequenos reflexos
    # Variações maiores que 12 viram branco (255), destacando claramente as silhuetas em movimento
    _, movimento = cv2.threshold(
        diferenca,
        12,
        255,
        cv2.THRESH_BINARY,
    )

    cv2.imshow("Frame", frame)
    cv2.imshow("Diferença", diferenca)
    cv2.imshow("Movimento", movimento)

    # Atualiza a memória, fazendo o frame atual virar o frame anterior do próximo ciclo
    frame_anterior = atual

    # Desconta o tempo de processamento do ciclo para garantir que a espera mantenha o FPS correto
    gasto = time.perf_counter() - inicio
    espera_ms = max(1, int((periodo - gasto) * 1000))

    if cv2.waitKey(espera_ms) & 0xFF == ord("q"):
        break

captura.release()
cv2.destroyAllWindows()