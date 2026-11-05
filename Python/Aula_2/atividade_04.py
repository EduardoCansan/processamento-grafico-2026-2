import cv2

entrada = "assets/imagem_base_opencv.jpg"
imagem = cv2.imread(entrada, cv2.IMREAD_GRAYSCALE)
if imagem is None:
    raise FileNotFoundError(f"Não foi possível abrir: {entrada}")

# Aplica os operadores diretamente e depois da suavização Gaussiana 5x5
suavizada = cv2.GaussianBlur(imagem, (5, 5), sigmaX=0, borderType=cv2.BORDER_REFLECT_101)

for nome, entrada_filtro in [("direto", imagem), ("gaussiano", suavizada)]:
    sobel_x = cv2.Sobel(entrada_filtro, cv2.CV_32F, 1, 0, ksize=3, borderType=cv2.BORDER_REFLECT_101)
    sobel_y = cv2.Sobel(entrada_filtro, cv2.CV_32F, 0, 1, ksize=3, borderType=cv2.BORDER_REFLECT_101)
    magnitude = cv2.magnitude(sobel_x, sobel_y)
    laplaciano = cv2.Laplacian(entrada_filtro, cv2.CV_32F, ksize=3, borderType=cv2.BORDER_REFLECT_101)

    resultados = {
        "sobel_x": cv2.convertScaleAbs(sobel_x),
        "sobel_y": cv2.convertScaleAbs(sobel_y),
        "magnitude": cv2.convertScaleAbs(magnitude),
        "laplaciano": cv2.convertScaleAbs(laplaciano)
    }

    print("\nProcessamento:", nome)
    for filtro, resultado in resultados.items():
        # Conta os pixels cuja intensidade é superior a 100
        print(filtro, "- pixels acima de 100:", (resultado > 100).sum())
        cv2.imwrite(f"atividade_04_{nome}_{filtro}.png", resultado)
        cv2.imshow(nome + " - " + filtro, resultado)

cv2.waitKey(0)
cv2.destroyAllWindows()
