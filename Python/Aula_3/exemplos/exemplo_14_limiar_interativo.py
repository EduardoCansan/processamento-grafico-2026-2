from pathlib import Path
import time
import cv2

# Função vazia necessária para o funcionamento do controle deslizante (trackbar) no OpenCV
def ao_alterar_limiar(_valor):
    pass

fonte = Path("assets/aula8_video_exemplo.avi")
captura = cv2.VideoCapture(str(fonte))
if not captura.isOpened():
    raise FileNotFoundError(f"Não foi possível abrir: {fonte}")

# Obtém o FPS original para calcular e manter a velocidade correta da reprodução
fps = captura.get(cv2.CAP_PROP_FPS)
periodo = 1 / fps if fps > 0 else 1 / 30

janela = "Mapa de movimento"
cv2.namedWindow(janela)

# Cria um controle deslizante na janela para ajustar o valor do limiar interativamente em tempo real
cv2.createTrackbar("Limiar", janela, 12, 255, ao_alterar_limiar)

frame_anterior = None

while True:
    inicio = time.perf_counter()
    sucesso, frame = captura.read()

    # Reinicia o vídeo ao chegar no final, criando um loop contínuo
    if not sucesso:
        captura.set(cv2.CAP_PROP_POS_FRAMES, 0)
        frame_anterior = None
        continue

    # Converte a imagem colorida para tons de cinza e aplica o desfoque Gaussiano
    # Isso evita que pequenos ruídos e granulações do vídeo sejam detectados como movimento falso
    cinza = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    atual = cv2.GaussianBlur(cinza, (15, 15), 0)

    if frame_anterior is None:
        frame_anterior = atual
        continue

    # Calcula a diferença absoluta pixel a pixel entre o frame atual e o anterior
    diferenca = cv2.absdiff(frame_anterior, atual)

    # Lê o valor numérico definido pelo usuário no controle deslizante a cada repetição do laço
    limiar = cv2.getTrackbarPos("Limiar", janela)

    # Aplica a limiarização (thresholding) usando o valor dinâmico do trackbar
    # Pixels com diferença menor que o limite viram preto, isolando em branco apenas o movimento real
    _, movimento = cv2.threshold(diferenca, limiar, 255, cv2.THRESH_BINARY)

    cv2.imshow(janela, movimento)
    frame_anterior = atual

    # Desconta o tempo de processamento do ciclo para garantir que o laço mantenha o FPS correto
    gasto = time.perf_counter() - inicio
    espera_ms = max(1, int((periodo - gasto) * 1000))
    if cv2.waitKey(espera_ms) & 0xFF == ord("q"):
        break

captura.release()
cv2.destroyAllWindows()