from pathlib import Path
import time
import cv2

caminho = Path("assets/aula8_video_exemplo.avi")
captura = cv2.VideoCapture(str(caminho))

if not captura.isOpened():
    raise RuntimeError(f"Não foi possível abrir o vídeo: {caminho}")

# Obtém o FPS original do vídeo para calcular e manter a velocidade correta da reprodução
fps = captura.get(cv2.CAP_PROP_FPS)
periodo = 1 / fps if fps > 0 else 1 / 30

while True:
    inicio = time.perf_counter()
    
    sucesso, frame = captura.read()
    
    # Reinicia o vídeo ao chegar no final, criando um loop contínuo
    if not sucesso:
        captura.set(cv2.CAP_PROP_POS_FRAMES, 0)
        continue

    # Converte a imagem colorida para tons de cinza
    # Simplificar a imagem de 3 canais (cores) para apenas 1 canal deixa o processamento mais rápido para as etapas seguintes
    cinza = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Aplica o desfoque Gaussiano para suavizar a imagem
    # A janela de 15x15 pixels gera um borrão forte, ideal para esconder ruídos e texturas irrelevantes antes de detectar contornos
    # O sigmaX=0 avisa ao OpenCV para calcular automaticamente a intensidade correta do desfoque com base no tamanho (15x15) que escolhemos
    suave = cv2.GaussianBlur(
        cinza,
        (15, 15),
        sigmaX=0,
    )

    cv2.imshow("Original", frame)
    cv2.imshow("Cinza e suavizada", suave)

    # Desconta o tempo de processamento do ciclo para garantir que a espera do waitKey mantenha o FPS correto
    gasto = time.perf_counter() - inicio
    espera_ms = max(1, int((periodo - gasto) * 1000))

    if cv2.waitKey(espera_ms) & 0xFF == ord("q"):
        break

captura.release()
cv2.destroyAllWindows()