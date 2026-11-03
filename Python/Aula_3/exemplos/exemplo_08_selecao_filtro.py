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

modo = "0"

while True:
    inicio = time.perf_counter()
    sucesso, frame = captura.read()
    
    # Reinicia o vídeo ao chegar no final, criando um loop contínuo
    if not sucesso:
        captura.set(cv2.CAP_PROP_POS_FRAMES, 0)
        continue

    if modo == "1":
        # Converte a imagem colorida para tons de cinza
        # A função calcula a intensidade da luz misturando as cores, simplificando a imagem para um único canal
        resultado = cv2.cvtColor(
            frame, cv2.COLOR_BGR2GRAY
        )
        nome = "Tons de cinza"
        
    elif modo == "2":
        # Aplica o desfoque Gaussiano para suavizar a imagem
        # O algoritmo borra a imagem calculando a média dos pixels em uma área de 15x15, o que disfarça ruídos e detalhes muito pequenos
        resultado = cv2.GaussianBlur(
            frame, (15, 15), 0
        )
        nome = "Gaussiano"
        
    elif modo == "3":
        # Converte a imagem para tons de cinza, um passo preparatório obrigatório para a detecção de bordas
        cinza = cv2.cvtColor(
            frame, cv2.COLOR_BGR2GRAY
        )
        
        # Aplica o filtro de Canny para identificar e desenhar as bordas dos objetos
        # Os valores 100 e 200 definem a sensibilidade: linhas fortes são mantidas e oscilações fracas são descartadas, isolando o contorno real
        resultado = cv2.Canny(cinza, 100, 200)
        nome = "Canny"
        
    else:
        resultado = frame
        nome = "Original"

    cv2.imshow("Filtro selecionado", resultado)
    print(f"\rModo: {nome:15}", end="")

    # Desconta o tempo de processamento do ciclo para garantir que a espera do waitKey mantenha o FPS correto
    gasto = time.perf_counter() - inicio
    espera_ms = max(1, int((periodo - gasto) * 1000))
    
    # Lê a entrada do teclado para fechar o programa ou trocar dinamicamente o efeito visual na tela
    tecla = cv2.waitKey(espera_ms) & 0xFF
    if tecla == ord("q"):
        break
    if tecla in map(ord, ("0", "1", "2", "3")):
        modo = chr(tecla)

captura.release()
cv2.destroyAllWindows()