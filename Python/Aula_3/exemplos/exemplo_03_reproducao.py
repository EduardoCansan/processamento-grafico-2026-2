from pathlib import Path
import time
import cv2

caminho = Path("assets/aula8_video_exemplo.avi")
captura = cv2.VideoCapture(str(caminho))

if not captura.isOpened():
    raise FileNotFoundError(
        f"Não foi possível abrir o vídeo: {caminho}"
    )

fps = captura.get(cv2.CAP_PROP_FPS)

# Calcula o tempo (em segundos) que cada frame deve ficar na tela para manter a velocidade original
# Se o vídeo não informar o FPS internamente, aplicamos um padrão seguro de 30 quadros por segundo
periodo = 1 / fps if fps > 0 else 1 / 30

while True:
    # Inicia o cronômetro para medir o tempo que o computador gasta processando o frame atual
    inicio = time.perf_counter()
    
    sucesso, frame = captura.read()

    if not sucesso:
        break

    cv2.imshow("Reprodução", frame)

    # Mede exatamente quanto tempo levou para ler e exibir a imagem na tela
    gasto = time.perf_counter() - inicio
    
    # Calcula a pausa exata descontando o tempo já gasto no processamento
    # Isso estabiliza a reprodução, impedindo que o vídeo rode rápido ou devagar demais em computadores diferentes
    # A função "max" garante pelo menos 1 milissegundo de pausa, que é uma exigência do OpenCV para conseguir atualizar a janela gráfica
    espera_ms = max(1, int((periodo - gasto) * 1000))

    if cv2.waitKey(espera_ms) & 0xFF == ord("q"):
        break

captura.release()
cv2.destroyAllWindows()