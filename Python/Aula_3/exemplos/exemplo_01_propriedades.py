from pathlib import Path
import cv2

caminho = Path("assets/aula8_video_exemplo.avi")

# Abre o arquivo de vídeo para leitura
# O OpenCV não carrega o vídeo inteiro de uma vez, ele cria um canal para puxar as imagens quadro a quadro e poupar memória RAM
captura = cv2.VideoCapture(str(caminho))

if not captura.isOpened():
    raise FileNotFoundError(
        f"Não foi possível abrir o vídeo: {caminho}"
    )

# Acessa as informações originais salvas no arquivo (metadados)
# Conseguimos consultar esses dados rapidamente sem precisar reproduzir ou processar o vídeo
fps = captura.get(cv2.CAP_PROP_FPS)
total = int(captura.get(cv2.CAP_PROP_FRAME_COUNT))
largura = int(captura.get(cv2.CAP_PROP_FRAME_WIDTH))
altura = int(captura.get(cv2.CAP_PROP_FRAME_HEIGHT))

# Calcula a duração total do vídeo em segundos (quantidade total de frames dividido por quantos passam por segundo)
duracao = total / fps if fps > 0 else 0

print(f"Resolução: {largura} × {altura}")
print(f"FPS informado: {fps:.2f}")
print(f"Frames: {total}")
print(f"Duração: {duracao:.2f} s")

# Lê exatamente o próximo quadro disponível no vídeo (neste caso, o primeiro)
# A imagem capturada é convertida automaticamente para o formato de matriz do NumPy
sucesso, frame = captura.read()
if sucesso:
    print("Tipo:", type(frame))
    # O shape revela as dimensões exatas da imagem gerada: (altura, largura, quantidade de canais de cor)
    print("Shape:", frame.shape)
    # Mostra o formato numérico de cada pixel. Geralmente é uint8, o que significa que as cores variam de 0 a 255
    print("Dtype:", frame.dtype)
    # Mostra o tamanho real em bytes que apenas esta imagem isolada está ocupando na memória RAM
    print("Bytes:", frame.nbytes)

# Fecha o arquivo e devolve para o sistema operacional a memória que estava sendo usada na leitura
captura.release()