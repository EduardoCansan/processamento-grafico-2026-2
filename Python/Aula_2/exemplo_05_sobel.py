from pathlib import Path
import cv2

entrada = Path("assets/imagem_base_opencv.jpg")
imagem = cv2.imread(str(entrada), cv2.IMREAD_GRAYSCALE)

if imagem is None:
    raise FileNotFoundError(
        f"Não foi possível abrir a imagem: {entrada}"
    )

# Aplica o operador de Sobel para calcular a derivada de primeira ordem na direção X
# Isso realça as mudanças abruptas de intensidade no eixo horizontal (detectando contornos verticais)
# Usamos cv2.CV_32F (ponto flutuante) em vez de inteiro 8 bits, pois a derivada pode gerar valores negativos
sobel_x = cv2.Sobel(
    imagem, cv2.CV_32F, 1, 0, # dx=1, dy=0 indica que o cálculo é apenas no eixo X
    ksize=3, borderType=cv2.BORDER_REFLECT_101,
)

# Aplica a mesma lógica matemática, mas agora no eixo Y
# Isso vai realçar as transições de intensidade na vertical (detectando contornos horizontais)
sobel_y = cv2.Sobel(
    imagem, cv2.CV_32F, 0, 1, # dx=0, dy=1 indica que o cálculo é apenas no eixo Y
    ksize=3, borderType=cv2.BORDER_REFLECT_101,
)

# Combina as respostas X e Y para calcular a força total do contorno em cada pixel
# Matematicamente, resolve a hipotenusa do triângulo retângulo formado pelas derivadas: sqrt(x² + y²)
magnitude = cv2.magnitude(sobel_x, sobel_y)

# Como as derivadas calculadas anteriormente possuem valores negativos e de ponto flutuante, 
# precisamos extrair o valor absoluto (módulo) e comprimir o resultado para o intervalo de 0 a 255 (inteiro 8 bits).
# Sem isso, os pixels negativos virariam preto e os contornos ficariam invisíveis ou distorcidos
visual_x = cv2.convertScaleAbs(sobel_x)
visual_y = cv2.convertScaleAbs(sobel_y)
visual_magnitude = cv2.convertScaleAbs(magnitude)

resultados = {
    "sobel_x.png": visual_x,
    "sobel_y.png": visual_y,
    "sobel_magnitude.png": visual_magnitude,
}

for nome, resultado in resultados.items():
    if not cv2.imwrite(nome, resultado):
        raise OSError(f"Falha ao salvar: {nome}")

cv2.imshow("Sobel X", visual_x)
cv2.imshow("Sobel Y", visual_y)
cv2.imshow("Magnitude", visual_magnitude)
cv2.waitKey(0)
cv2.destroyAllWindows()