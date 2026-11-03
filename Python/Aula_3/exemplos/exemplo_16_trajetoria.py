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
trajetoria = []

while True:
    inicio = time.perf_counter()
    sucesso, frame = captura.read()

    # Reinicia o vídeo ao chegar no final, criando um loop contínuo
    if not sucesso:
        captura.set(cv2.CAP_PROP_POS_FRAMES, 0)
        frame_anterior = None
        # Limpa o histórico de posições para que a linha não atravesse a tela ao reiniciar o vídeo
        trajetoria.clear()
        continue

    # Converte a imagem colorida para tons de cinza, reduzindo de 3 canais para 1 canal
    atual = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Aplica o desfoque Gaussiano para suavizar a imagem e evitar que granulações e ruídos sejam lidos como movimento
    atual = cv2.GaussianBlur(atual, (15, 15), 0)

    if frame_anterior is None:
        frame_anterior = atual
        continue

    # Calcula a diferença absoluta pixel a pixel entre o frame atual e o frame anterior
    diferenca = cv2.absdiff(frame_anterior, atual)
    
    # Aplica a limiarização (thresholding) para binarizar a imagem
    # Pixels com diferença de intensidade maior que 12 viram branco (255), destacando o movimento. O resto vira preto (0)
    _, movimento = cv2.threshold(diferenca, 12, 255, cv2.THRESH_BINARY)
    
    # Aplica a dilatação morfológica para preencher buracos internos e unir partes separadas do mesmo objeto
    movimento = cv2.dilate(movimento, None, iterations=2)
    
    # Encontra os contornos mapeando apenas os perímetros externos (cv2.RETR_EXTERNAL) das áreas brancas
    contornos, _ = cv2.findContours(
        movimento, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    # Filtra os contornos por área para descartar pequenos ruídos residuais menores que 300 pixels quadrados
    validos = [c for c in contornos if cv2.contourArea(c) >= 300]

    if validos:
        # Encontra o contorno com a maior área de movimento na cena
        maior = max(validos, key=cv2.contourArea)
        x, y, largura, altura = cv2.boundingRect(maior)

        # Calcula a coordenada (x, y) do ponto central do retângulo delimitador
        centro = (x + largura // 2, y + altura // 2)

        # Salva o ponto central atual na lista que forma o rastro do movimento
        trajetoria.append(centro)

        # Limita o tamanho da lista aos últimos 64 pontos para a linha não crescer infinitamente
        trajetoria = trajetoria[-64:]

        # Desenha o retângulo ao redor do objeto e um círculo marcando o ponto central
        cv2.rectangle(frame, (x, y), (x + largura, y + altura), (0, 255, 0), 2)
        cv2.circle(frame, centro, 5, (0, 0, 255), -1)

    # Conecta os pontos salvos na lista com linhas retas para desenhar a trajetória visual
    for indice in range(1, len(trajetoria)):
        cv2.line(frame, trajetoria[indice - 1], trajetoria[indice], (255, 0, 0), 2)

    cv2.imshow("Trajetória aproximada", frame)
    frame_anterior = atual

    # Desconta o tempo de processamento do ciclo para garantir que a espera do waitKey mantenha o FPS correto
    gasto = time.perf_counter() - inicio
    espera_ms = max(1, int((periodo - gasto) * 1000))

    if cv2.waitKey(espera_ms) & 0xFF == ord("q"):
        break

captura.release()
cv2.destroyAllWindows()