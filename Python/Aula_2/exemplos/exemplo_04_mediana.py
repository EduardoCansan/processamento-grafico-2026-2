from pathlib import Path
import cv2

entrada = Path("assets/aula7_ruido_sal_pimenta.png")
imagem = cv2.imread(str(entrada))

if imagem is None:
    raise FileNotFoundError(
        f"Não foi possível abrir a imagem: {entrada}"
    )

# Aplica um filtro não-linear que substitui o valor do pixel central pela mediana matemática da sua vizinhança
# É altamente eficaz para remover ruídos pontuais (como o ruído "sal e pimenta") preservando as bordas e contornos, algo que os filtros de média e gaussiano não conseguem fazer tão bem
mediana = cv2.medianBlur(
    imagem, # 1. Imagem original
    5,      # 2. Tamanho da janela quadrada (kernel) de 5x5 pixels. Deve ser sempre um número ímpar
)

if not cv2.imwrite("ruido_reduzido.png", mediana):
    raise OSError("Falha ao salvar ruido_reduzido.png")

cv2.imshow("Ruido sal e pimenta", imagem)
cv2.imshow("Filtro da mediana", mediana)
cv2.waitKey(0)
cv2.destroyAllWindows()