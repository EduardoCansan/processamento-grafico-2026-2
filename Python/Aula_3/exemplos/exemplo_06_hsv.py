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

# Define os limites de cor no formato HSV para rastrear especificamente os tons de verde
# H (Matiz): é a cor propriamente dita (aqui filtramos a faixa do verde, de 35 a 85)
# S (Saturação): é a pureza da cor (ignoramos cores desbotadas ou muito acinzentadas, abaixo de 80)
# V (Valor): é o brilho (ignoramos áreas quase pretas ou sombras muito fortes, abaixo de 80)
limite_inferior = (35, 80, 80)
limite_superior = (85, 255, 255)

while True:
    inicio = time.perf_counter()
    sucesso, frame = captura.read()

    # Reinicia o vídeo ao chegar no final, criando um loop contínuo
    if not sucesso:
        captura.set(cv2.CAP_PROP_POS_FRAMES, 0)
        continue

    # Converte a imagem do padrão BGR para o padrão HSV
    # No BGR, uma simples sombra altera o azul, o verde e o vermelho ao mesmo tempo, quebrando a detecção
    # No HSV, a cor (H) fica separada do brilho (V), permitindo rastrear o verde mesmo que a iluminação da cena mude
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Cria uma máscara em preto e branco filtrando apenas as cores que definimos acima
    # Os pixels do vídeo que estiverem dentro da faixa de verde ficam brancos e todo o resto vira preto
    mascara = cv2.inRange(
        hsv,
        limite_inferior,
        limite_superior,
    )
    
    # Usa a máscara em preto e branco como um molde de recorte sobre a imagem original
    # Onde a máscara for branca, a cor verdadeira do vídeo aparece; onde for preta, o vídeo fica totalmente preto
    regiao_verde = cv2.bitwise_and(
        frame,
        frame,
        mask=mascara,
    )

    cv2.imshow("Original", frame)
    cv2.imshow("Mascara", mascara)
    cv2.imshow("Regiao verde", regiao_verde)

    # Desconta o tempo de processamento do ciclo para garantir que a espera do waitKey mantenha o FPS correto
    gasto = time.perf_counter() - inicio
    espera_ms = max(1, int((periodo - gasto) * 1000))

    if cv2.waitKey(espera_ms) & 0xFF == ord("q"):
        break

captura.release()
cv2.destroyAllWindows()