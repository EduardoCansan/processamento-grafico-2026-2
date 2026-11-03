from pathlib import Path
import time
import cv2

caminho = Path("assets/aula8_video_exemplo.avi")
captura = cv2.VideoCapture(str(caminho))

if not captura.isOpened():
    raise RuntimeError(f"Não foi possível abrir o vídeo: {caminho}")

# Obtém o FPS original do vídeo para calcular o tempo correto que cada frame deve durar
fps_video = captura.get(cv2.CAP_PROP_FPS)
periodo = 1 / fps_video if fps_video > 0 else 1 / 30

fps_suave = None

while True:
    inicio_laco = time.perf_counter()
    sucesso, frame = captura.read()
    
    # Reinicia o vídeo ao chegar no final, criando um loop contínuo
    if not sucesso:
        captura.set(cv2.CAP_PROP_POS_FRAMES, 0)
        continue

    inicio_filtro = time.perf_counter()
    
    # Aplica um desfoque Gaussiano intencionalmente pesado (área de 31x31 pixels)
    # Como a área de cálculo para cada pixel é muito grande, isso exige bastante do processador
    resultado = cv2.GaussianBlur(frame, (31, 31), 0)
    
    # Mede exatamente quantos milissegundos o computador gastou apenas executando o desfoque
    filtro_ms = (
        time.perf_counter() - inicio_filtro
    ) * 1000

    if fps_suave is None:
        fps_exibido = 0.0
    else:
        fps_exibido = fps_suave

    texto = (
        f"Filtro: {filtro_ms:.1f} ms | "
        f"FPS: {fps_exibido:.1f}"
    )
    
    # Escreve o texto com os indicadores de desempenho diretamente sobre a imagem
    cv2.putText(
        resultado, texto, (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7, (0, 255, 0), 2,
    )
    cv2.imshow("Desempenho", resultado)

    # Desconta o tempo de processamento do ciclo para garantir que a espera mantenha o FPS correto
    gasto = time.perf_counter() - inicio_laco
    espera_ms = max(1, int((periodo - gasto) * 1000))
    tecla = cv2.waitKey(espera_ms) & 0xFF
    
    # Calcula a taxa real de quadros por segundo que conseguimos atingir neste ciclo específico
    tempo_laco = time.perf_counter() - inicio_laco
    fps_atual = 1 / tempo_laco if tempo_laco > 0 else 0
    
    # Suaviza o valor do FPS exibido na tela usando uma média móvel
    # Ao misturar 90% do valor histórico com apenas 10% do valor atual, evitamos que o número fique pulando sem parar a cada pequeno atraso
    if fps_suave is None:
        fps_suave = fps_atual
    else:
        fps_suave = 0.9 * fps_suave + 0.1 * fps_atual

    if tecla == ord("q"):
        break

captura.release()
cv2.destroyAllWindows()