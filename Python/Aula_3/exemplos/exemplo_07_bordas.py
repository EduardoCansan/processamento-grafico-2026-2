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

    # Aplica o filtro de média para desfocar a imagem
    # Ele suaviza tudo de forma igual, calculando a média simples das cores em pequenos blocos de 5x5 pixels
    media = cv2.blur(frame, (5, 5))
    
    # Aplica o filtro de mediana, que é excelente para limpar ruídos pontuais (como pequenos pontinhos na tela)
    # Diferente da média, a mediana borra a imagem por dentro, mas preserva melhor o limite e as bordas das formas
    mediana = cv2.medianBlur(frame, 5)

    # Converte a imagem colorida para tons de cinza
    # Esse é um passo preparatório obrigatório para facilitar o trabalho do detector de bordas
    cinza = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Aplica o desfoque Gaussiano na imagem em tons de cinza
    # Esse desfoque extra evita que granulações do vídeo ou texturas muito pequenas sejam confundidas com bordas reais
    suave = cv2.GaussianBlur(cinza, (5, 5), 0)
    
    # Aplica o filtro de Canny para identificar e desenhar as bordas dos objetos
    # Os valores 100 e 200 controlam a sensibilidade: linhas fortes e bem definidas são mantidas, enquanto riscos fracos ou falhos são apagados
    bordas = cv2.Canny(suave, 100, 200)

    cv2.imshow("Original", frame)
    cv2.imshow("Media", media)
    cv2.imshow("Mediana", mediana)
    cv2.imshow("Canny", bordas)

    # Desconta o tempo de processamento do ciclo para garantir que a espera do waitKey mantenha o FPS correto
    gasto = time.perf_counter() - inicio
    espera_ms = max(1, int((periodo - gasto) * 1000))

    if cv2.waitKey(espera_ms) & 0xFF == ord("q"):
        break

captura.release()
cv2.destroyAllWindows()