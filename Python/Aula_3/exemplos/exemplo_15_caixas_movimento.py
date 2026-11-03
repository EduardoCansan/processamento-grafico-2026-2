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
        frame_anterior = None
        continue

    # Converte a imagem colorida para tons de cinza e aplica o desfoque Gaussiano 
    # para evitar que pequenos ruídos ou artefatos de compressão sejam lidos como movimento
    atual = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    atual = cv2.GaussianBlur(atual, (15, 15), 0)
    
    if frame_anterior is None:
        frame_anterior = atual
        continue

    # Calcula a diferença absoluta pixel a pixel entre o frame atual e o anterior
    diferenca = cv2.absdiff(frame_anterior, atual)
    
    # Aplica a limiarização (thresholding) para binarizar a imagem
    # Pixels com diferença de intensidade maior que 12 viram branco (movimento), o resto vira preto
    _, movimento = cv2.threshold(
        diferenca, 12, 255, cv2.THRESH_BINARY)
        
    # Aplica a dilatação morfológica na imagem binária
    # O algoritmo expande os pixels brancos por duas iterações consecutivas
    # Isso preenche buracos internos e une fragmentos separados do mesmo objeto em movimento
    movimento = cv2.dilate(movimento, None, iterations=2)
    
    # Mapeia os contornos das áreas em movimento
    # cv2.RETR_EXTERNAL ignora buracos internos, extraindo apenas o perímetro externo da forma
    # cv2.CHAIN_APPROX_SIMPLE economiza memória guardando apenas os vértices finais de linhas retas
    contornos, _ = cv2.findContours(
        movimento, cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
        
    for contorno in contornos:
        # Calcula a área do contorno em pixels quadrados
        # Atua como um filtro, ignorando pequenos ruídos que tenham menos de 300 pixels de área
        if cv2.contourArea(contorno) < 300:
            continue
            
        # Encontra as coordenadas (x, y) e as dimensões (largura, altura) do menor retângulo capaz de envolver o contorno
        x, y, largura, altura = cv2.boundingRect(contorno)
        
        cv2.rectangle(
            frame, (x, y),
            (x + largura, y + altura),
            (0, 255, 0), 2)

    cv2.imshow("Detecção de movimento", frame)
    cv2.imshow("Máscara", movimento)
    
    frame_anterior = atual
    
    # Desconta o tempo de processamento do ciclo para garantir que o laço mantenha o FPS correto
    gasto = time.perf_counter() - inicio
    espera_ms = max(1, int((periodo - gasto) * 1000))
    if cv2.waitKey(espera_ms) & 0xFF == ord("q"):
        break

captura.release()
cv2.destroyAllWindows()