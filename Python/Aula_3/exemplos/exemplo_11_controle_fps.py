from pathlib import Path
import time
import cv2

caminho = Path("assets/aula8_video_exemplo.avi")
captura = cv2.VideoCapture(str(caminho))

if not captura.isOpened():
    raise RuntimeError(f"Não foi possível abrir o vídeo: {caminho}")

# Define um limite manual de velocidade (FPS) para a reprodução
# Isso força o vídeo a rodar nessa taxa específica, ignorando a velocidade original do arquivo
FPS_ALVO = 15

# Calcula o tempo exato (em segundos) que cada frame deve permanecer na tela para atingir o alvo
PERIODO = 1 / FPS_ALVO

while True:
    inicio = time.perf_counter()
    sucesso, frame = captura.read()
    
    # Reinicia o vídeo ao chegar no final, criando um loop contínuo
    if not sucesso:
        captura.set(cv2.CAP_PROP_POS_FRAMES, 0)
        continue

    # Aplica o desfoque Gaussiano para suavizar a imagem
    resultado = cv2.GaussianBlur(frame, (15, 15), 0)
    cv2.imshow("FPS controlado", resultado)

    # Mede o tempo exato que o computador levou para ler o frame e aplicar o filtro
    gasto = time.perf_counter() - inicio
    
    # Calcula a pausa necessária para manter o FPS cravado no valor definido
    # Subtrai o tempo já gasto no processamento do tempo total que o frame deveria durar
    # O valor final diz ao waitKey quantos milissegundos ele deve pausar antes de avançar
    espera_ms = max(1, int((PERIODO - gasto) * 1000))

    if cv2.waitKey(espera_ms) & 0xFF == ord("q"):
        break

captura.release()
cv2.destroyAllWindows()