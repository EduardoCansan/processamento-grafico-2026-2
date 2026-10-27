from pathlib import Path
import cv2

caminho = Path("assets/imagem_base_opencv.jpg")
original = cv2.imread(str(caminho))
if original is None:
    raise FileNotFoundError(f"Não foi possível abrir a imagem: {caminho}")

# A atribuição direta não duplica a matriz, apenas cria um novo nome (ponteiro) apontando para o mesmo endereço de memória
referencia = original

# O método copy força a alocação de um novo espaço na memória RAM e clona os dados de forma totalmente independente
copia = original.copy()

# Como "referencia" e "original" compartilham a mesma memória, pintar este quadrante de verde altera as duas variáveis simultaneamente
referencia[0:100, 0:100] = [0, 255, 0]

# O operador "is" do Python avalia a identidade da memória (se é o mesmo objeto físico), não apenas o conteúdo, retornando True neste caso
print("referencia é original:", referencia is original)

# Retorna False, pois "copia" foi alocada em um bloco de memória separado e não sofreu a alteração feita acima
print("copia é original:", copia is original)

cv2.imshow("Original alterada", original)
cv2.imshow("Copia independente", copia)
cv2.waitKey(0)
cv2.destroyAllWindows()
