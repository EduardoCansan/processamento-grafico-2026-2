import cv2

original = cv2.imread("assets/imagem_base_opencv.jpg")
ruidosa = cv2.imread("assets/aula7_ruido_sal_pimenta.png")

if original is None:
    raise FileNotFoundError("Não foi possível abrir: assets/imagem_base_opencv.jpg")
if ruidosa is None:
    raise FileNotFoundError("Não foi possível abrir: assets/aula7_ruido_sal_pimenta.png")

# Aplica os três filtros 5x5, conforme os exemplos
media = cv2.blur(ruidosa, (5, 5), borderType=cv2.BORDER_REFLECT_101)
gaussiano = cv2.GaussianBlur(ruidosa, (5, 5), sigmaX=0, borderType=cv2.BORDER_REFLECT_101)
mediana = cv2.medianBlur(ruidosa, 5)

# Compara cada resultado com a imagem original sem ruído
print("Erro média:", cv2.absdiff(original, media).mean())
print("Erro Gaussiano:", cv2.absdiff(original, gaussiano).mean())
print("Erro mediana:", cv2.absdiff(original, mediana).mean())

cv2.imwrite("atividade_02_media.png", media)
cv2.imwrite("atividade_02_gaussiano.png", gaussiano)
cv2.imwrite("atividade_02_mediana.png", mediana)

cv2.imshow("Ruido", ruidosa)
cv2.imshow("Media", media)
cv2.imshow("Gaussiano", gaussiano)
cv2.imshow("Mediana", mediana)
cv2.waitKey(0)
cv2.destroyAllWindows()
