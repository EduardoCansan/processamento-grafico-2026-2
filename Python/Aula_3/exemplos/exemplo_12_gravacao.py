from pathlib import Path
import time
import cv2

entrada = Path("assets/aula8_video_exemplo.avi")
captura = cv2.VideoCapture(str(entrada))
if not captura.isOpened():
    raise FileNotFoundError(f"Não foi possível abrir: {entrada}")

fps = captura.get(cv2.CAP_PROP_FPS)
if fps <= 0:
    fps = 30.0

largura = int(captura.get(cv2.CAP_PROP_FRAME_WIDTH))
altura = int(captura.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Define o formato de compressão (codec) para criar o novo arquivo de vídeo
# O MJPG (Motion JPEG) salva o vídeo como se fosse uma sequência rápida de fotos JPEG
codec = cv2.VideoWriter_fourcc(*"MJPG")

# Prepara o arquivo de gravação, configurando a mesma resolução e o mesmo FPS do original
# O parâmetro isColor=True avisa ao gravador para esperar exclusivamente imagens no formato colorido (3 canais)
gravador = cv2.VideoWriter(
    "video_processado.avi",
    codec,
    fps,
    (largura, altura),
    isColor=True,
)

if not gravador.isOpened():
    captura.release()
    raise RuntimeError("Não foi possível criar o vídeo de saída.")

periodo = 1 / fps

# Como este script salva um arquivo no disco, não reiniciamos o laço no final para evitar gerar um vídeo infinito
while True:
    inicio = time.perf_counter()
    sucesso, frame = captura.read()
    if not sucesso:
        break

    # Converte a imagem colorida para tons de cinza, o que é necessário para a detecção de bordas
    cinza = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Aplica o filtro de Canny para desenhar os contornos e as bordas dos objetos
    # Os valores 80 e 160 definem o limite mínimo e máximo da sensibilidade do filtro
    # O resultado é uma imagem preta e branca de apenas 1 canal
    bordas = cv2.Canny(cinza, 80, 160)

    # Converte a imagem das bordas (1 canal) de volta para o formato colorido (3 canais)
    # Isso não traz as cores originais de volta, apenas clona as linhas brancas nos canais de cor
    # É um passo obrigatório para evitar que o gravador de vídeo (VideoWriter) recuse o frame por causa do isColor=True
    resultado = cv2.cvtColor(bordas, cv2.COLOR_GRAY2BGR)

    # Escreve o frame processado no novo arquivo de vídeo
    gravador.write(resultado)
    cv2.imshow("Gravação", resultado)

    gasto = time.perf_counter() - inicio
    espera_ms = max(1, int((periodo - gasto) * 1000))
    if cv2.waitKey(espera_ms) & 0xFF == ord("q"):
        break

captura.release()
gravador.release()
cv2.destroyAllWindows()