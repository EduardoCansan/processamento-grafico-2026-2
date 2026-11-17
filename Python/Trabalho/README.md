# Grupo 16 — Inspeção de esporas em placas (DeepPCB)

Trabalho de **Processamento de Imagens**, feito em Python, OpenCV e NumPy, no estilo dos exemplos das Aulas 1, 2 e 3. Não utiliza redes neurais, interface gráfica nem testes unitários.

## Objetivo

Comparar uma placa de referência (`_temp.jpg`) com a placa de teste (`_test.jpg`) para localizar possíveis **esporas (spur, classe 4)**. O programa processa vários pares e produz imagens anotadas, tabelas e métricas. Os outros cinco tipos de defeito podem aparecer nas mesmas imagens: **não são esporas**.

Base oficial: https://github.com/tangsanli5201/DeepPCB (uso em pesquisa, conforme autores). Os 1.500 pares de 640 × 640 são distribuídos em `trainval.txt` e `test.txt`. O dataset oficial já contém alguns defeitos inseridos pelos autores; nosso código **não cria defeitos artificiais**.

## Instalação no Windows / VSCode

No terminal do VSCode, a partir da pasta onde deseja guardar o projeto:

```powershell
git clone https://github.com/EduardoCansan/processamento-grafico-2026-2.git
cd processamento-grafico-2026-2\Python
git clone https://github.com/tangsanli5201/DeepPCB.git
cd Trabalho
python -m pip install -r requirements.txt
```

Confirme a pasta `../DeepPCB/PCBData` (no Windows: `..\DeepPCB\PCBData`). Exemplo de estrutura:

```text
Python/
  Trabalho/
    main.py
    README.md
    requirements.txt
  DeepPCB/
    PCBData/
      trainval.txt
      test.txt
      group00041/00041/00041000_temp.jpg
      group00041/00041/00041000_test.jpg
      group00041/00041_not/00041000.txt
```

Se o dataset estiver em outro lugar, informe o caminho absoluto em `--dados`.

## Executar

**1. Explorar o desenvolvimento** (primeiros 10 pares do subconjunto de desenvolvimento):

```powershell
python main.py --dados "..\DeepPCB\PCBData" --divisao trainval --etapa desenvolvimento --limite 10 --comparar --saida resultados_dev_novos
```

**2. Processar todo o desenvolvimento** (para observar defeitos e escolher parâmetros):

```powershell
python main.py --dados "..\DeepPCB\PCBData" --divisao trainval --etapa desenvolvimento --comparar --saida resultados_dev_novos
```

**3. Validar sem reajustar os parâmetros** (outros 20% de `trainval.txt`):

```powershell
python main.py --dados "..\DeepPCB\PCBData" --divisao trainval --etapa validacao --comparar --saida resultados_validacao_novos
```

**4. Avaliação oficial somente após fixar as escolhas** (todos os pares de `test.txt`):

```powershell
python main.py --dados "..\DeepPCB\PCBData" --divisao test --comparar --saida resultados_teste_novos
```

O corte de desenvolvimento/validação é fixo por posição na lista original: **80% / 20%**, a cada cinco pares. É uma divisão simples e reproduzível; imagens de grupos próximos ainda podem ser semelhantes. `--limite 0` (padrão) significa processar todas as imagens da etapa. Sem `--comparar`, executa apenas a versão geométrica.

Os parâmetros iniciais ficam no início do `main.py`: `RAIO`, `LIMIAR`, `AREA_MIN`, `AREA_MAX`, `MAX_LADO`, `IOU_MIN`, `COBRE_CLARO`. Ajustar **exclusivamente com desenvolvimento**. A polaridade `COBRE_CLARO` é uma hipótese que precisa ser conferida visualmente com exemplos reais do `trainval`, não foi validada nesta alteração.

## Pipeline explicado

1. **Leitura:** monta os pares oficiais e lê as anotações da classe spur **apenas para avaliação**, nunca para a detecção.
2. **Busca local SAD própria:** tenta deslocamentos `dx,dy` de -`RAIO` a +`RAIO`; compara recortes amostrados (passo 3) usando a média do erro absoluto; escolhe o menor custo. Esse algoritmo **não** usa `matchTemplate` nem `alignECC`.
3. **Alinhamento:** suaviza as imagens para estimar o deslocamento e aplica `warpAffine` **uma única vez** sobre a imagem de teste original. Gera uma máscara válida para ignorar bordas deslocadas.
4. **Diferença e limiar:** `cv2.absdiff` + `cv2.threshold`. Não aplica abertura 3×3 automaticamente, para evitar eliminar esporas pequenas.
5. **Duas versões:** `baseline` usa diferenças acima do limiar; `geometrica` procura acréscimos de cobre próximos a uma trilha de referência, usando limiar de Otsu comum e critérios geométricos simples. Outras categorias ainda podem causar falsos positivos.
6. **Regiões:** `connectedComponentsWithStats` preserva a contagem de pixels pequenos; obtém caixa, área, largura, altura e intensidade de resposta. Contornos da Aula 3 são referência didática, mas `contourArea` não mede a mesma área para regiões minúsculas.
7. **Coordenadas:** converte as caixas da imagem alinhada de volta para a imagem de teste original (`x_original=x_alinhado-dx`, `y_original=y_alinhado-dy`); desenha sobre o teste e compara com as caixas anotadas.
8. **Avaliação:** pareamento 1:1 por `IoU > 0,33`, considerando positivas apenas anotações da classe 4. Exporta `TP`, `FP`, `FN`, precisão, recall, F1 e tempo em ms.

**Métricas:** `precisão=TP/(TP+FP)`, `recall=TP/(TP+FN)` e `F1=2·precisão·recall/(precisão+recall)`. O tempo medido inclui **alinhamento + detecção + conversão de caixas**, mas não inclui leitura, avaliação nem escrita de arquivos. A resposta do detector (0 a 1) indica intensidade de diferença, **não** probabilidade de espora.

## Saídas

Para cada versão são gerados `por_imagem.csv`, `deteccoes.csv`, `resumo.json` e amostras visuais em `exemplos/`. Cada exemplo inclui referência, teste, alinhada, diferença, máscara, detecções (caixas vermelhas) e gabarito spur (caixas verdes). `comparacao.json` reúne os dois resumos.

Os arquivos já versionados em `resultados/` e `resultados_teste/` são **históricos, anteriores a esta alteração**. Eles indicavam F1 muito baixo (geométrica: 0,0012 em 500 pares). **Não são resultados da versão nova**; não presumir melhora sem executar novamente a base.

## Investigação experimental e entrega

**Pergunta:** a filtragem geométrica melhora o F1 em comparação com a diferença simples?

Comparar as duas versões nas mesmas imagens do desenvolvimento e da validação, incluindo TP/FP/FN, precisão, recall, F1 e tempo. Observar casos de acerto, falhas e falsos positivos de `short` (2) e `copper` (5). Escolher parâmetros com o desenvolvimento, verificar na validação e manter as escolhas congeladas para `test.txt`. Uma execução exploratória anterior do teste já existe: mencionar isso com transparência no relatório.

**Entregar:** código, README, dataset e divisão utilizados, imagens e CSV/JSON de resultados, relatório técnico simples com hipótese/comparação/tempos/limitações e referências. Nenhuma interface ou teste unitário é exigido.

## Referências das aulas

As referências pedagógicas aparecem em comentários próximos às operações no `main.py`:

- `Aula_1/atividade_01/atividade_01.py`: leitura e salvamento;
- `Aula_1/exemplos/exemplo_09.py` e `exemplo_10.py`: máscaras e limiarização;
- `Aula_2/exemplo_03_gaussiano.py`: suavização;
- `Aula_2/exemplo_01_correlacao_manual.py`: exemplo didático de percorrer matrizes — **não** implementa o alinhamento SAD;
- `Aula_3/exemplos/exemplo_13_movimento.py`: diferença entre imagens;
- `Aula_3/exemplos/exemplo_15_caixas_movimento.py`: localização e desenho de caixas;
- `Aula_3/exemplos/exemplo_09_desempenho.py` e `exemplo_10_benchmark.py`: tempo e NumPy.

## Limitações

A classificação geométrica é uma heurística: ainda pode confundir `spur` com `short` e `copper`. A polaridade e os filtros precisam de validação visual em `trainval`. Busca por translação não corrige rotação nem escala, e deslocamentos maiores que `RAIO` não são tratados. O projeto não foi medido novamente no dataset completo após esta simplificação.
