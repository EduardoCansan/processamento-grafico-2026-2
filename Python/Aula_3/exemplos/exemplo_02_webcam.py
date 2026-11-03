import cv2

# O número 0 indica que queremos acessar a primeira webcam conectada ao computador
captura = cv2.VideoCapture(0)

# Verifica se a câmera foi iniciada corretamente e se o sistema operacional liberou o acesso
if not captura.isOpened():
    raise RuntimeError("Não foi possível abrir a câmera.")

# Cria um laço contínuo para manter a exibição do vídeo em tempo real
while True:
    # Puxa o frame exato do sensor da câmera no instante em que o comando é executado
    sucesso, frame = captura.read()

    if not sucesso:
        print("Falha na leitura da câmera.")
        break

    # Exibe a imagem capturada em uma janela gráfica
    cv2.imshow("Webcam", frame)

    # Pausa o laço por 1 milissegundo
    # Esse tempo mínimo é obrigatório para que o OpenCV consiga atualizar a imagem na tela e escutar o teclado
    # O comando 0xFF limpa interferências do sistema operacional para garantir a leitura correta da tecla
    tecla = cv2.waitKey(1) & 0xFF
    
    # Interrompe o laço e encerra a visualização se a tecla 'q' for pressionada
    if tecla == ord("q"):
        break

# Libera o hardware da câmera para que outros programas possam usá-la e apaga a janela da memória
captura.release()
cv2.destroyAllWindows()