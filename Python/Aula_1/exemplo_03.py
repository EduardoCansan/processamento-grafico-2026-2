from pathlib import Path
import cv2

caminho = Path("assets/imagem_base_opencv.jpg")
imagem = cv2.imread(str(caminho))

if imagem is None:
    raise FileNotFoundError(f"Não foi possível abrir a imagem: {caminho}")

# Cria uma cópia independente da matriz na memória
# Isso evita que as modificações vazem para a variável da imagem original por referência
resultado = imagem.copy()

# O fatiamento do NumPy acessa uma sub-matriz usando a sintaxe [y_inicial:y_final, x_inicial:x_final]
# O limite final é sempre exclusivo, portanto 150 processa até a linha 149 e 250 vai até a coluna 249
# Atribuir a cor [0, 255, 0] (Verde no padrão BGR) a essa fatia pinta o bloco inteiro instantaneamente, sem precisar de laços de repetição
resultado[50:150, 50:250] = [0, 255, 0]

cv2.imshow("Original", imagem)
cv2.imshow("Regiao alterada", resultado)
cv2.waitKey(0)
cv2.destroyAllWindows()
