# Grupo 16 — Inspeção de Esporas em PCBs (DeepPCB)

Implementação **clássica** em Python/OpenCV/NumPy. Sem redes neurais e sem interface.

## Dataset original

Fonte: https://github.com/tangsanli5201/DeepPCB

O repositório define 1.500 pares de imagens de 640x640 e seis classes. Para este trabalho, **spur = ID 4**. O README do DeepPCB diz que os autores inseriram alguns defeitos artificialmente nas imagens do próprio dataset; o projeto **não adiciona** ruído ou defeitos e utiliza os dados oficiais sem modificações.

Formato real:

```
DeepPCB/PCBData/
    trainval.txt
    test.txt
    group00041/00041/00041000_temp.jpg
    group00041/00041/00041000_test.jpg
    group00041/00041_not/00041000.txt
```

A lista oficial contém `group.../00041000.jpg` como identificador do par, **não** como imagem que deve ser aberta literalmente. O programa converte esse identificador para `_temp.jpg` e `_test.jpg`. As anotações usam `x1 y1 x2 y2 classe`, separados por espaços, e classe 4 indica espora.

## Instalação

```bash
git clone https://github.com/tangsanli5201/DeepPCB.git
cd inspecao_pcb_espora
python -m pip install -r requirements.txt
```

Se o DeepPCB tiver sido clonado na mesma pasta que este projeto, a pasta dos dados fica em `../DeepPCB/PCBData`.

## Executar

Primeiro teste, com 10 pares do conjunto de desenvolvimento:

```bash
python main.py --dados ../DeepPCB/PCBData --divisao trainval --limite 10 --comparar
```

Conjunto de desenvolvimento completo:

```bash
python main.py --dados ../DeepPCB/PCBData --divisao trainval --comparar --saida resultados_dev
```

Depois de fixar os parâmetros sem olhar o teste, rodar o teste oficial:

```bash
python main.py --dados ../DeepPCB/PCBData --divisao test --comparar --saida resultados_teste
```

Para comparar **SAD e SSD**, manter os demais parâmetros iguais e rodar separadamente:

```bash
python main.py --dados ../DeepPCB/PCBData --divisao trainval --versao geometrica --alinhamento sad --saida resultados_sad
python main.py --dados ../DeepPCB/PCBData --divisao trainval --versao geometrica --alinhamento ssd --saida resultados_ssd
```

## Explicação do pipeline

1. **Registro translacional por busca local** (`alinhar_busca_local`): tenta todos os pares de deslocamento `(dx,dy)` de `-raio` a `+raio`. Para cada hipótese calcula **SAD**, média dos valores absolutos das diferenças de pixels, ou **SSD**, média dos quadrados dessas diferenças. A hipótese de menor custo é aplicada por `warpAffine`. É implementação manual da função de custo e da busca. Usa pixels amostrados a cada 3 posições, por custo computacional, e evita bordas variáveis durante a comparação. O DeepPCB já vem pré-alinhado, mas pequenos deslocamentos residuais ainda podem ser avaliados.
2. **Mapa de diferenças:** `absdiff(referencia, teste_alinhado)`.
3. **Segmentação:** limiar fixo e morfologia para filtrar respostas pequenas.
4. **Baseline:** todas as diferenças segmentadas são candidatas, respeitando limites de área e tamanho.
5. **Versão geométrica:** mantém somente diferenças com **cobre acrescentado** em relação à referência, que se conectem a uma trilha existente, com limites simples de geometria. A polaridade do cobre é estimada pela classe de pixels menos frequente na imagem de referência. **Limitação importante:** isso pode confundir spur com short ou outros defeitos de cobre; a hipótese deve ser verificada com os resultados e exemplos de erro, sem fingir que é um classificador perfeito.
6. **Relatório:** caixa `(x1,y1,x2,y2)`, área, largura, altura, resposta de diferença (0 a 1), tempo por imagem e deslocamento calculado.
7. **Avaliação:** as anotações são lidas **apenas depois de executar a detecção**. A correspondência 1:1 com o gabarito da classe 4 usa IoU >= 0,33, seguindo o valor descrito no README do dataset (que menciona estritamente > 0,33). As outras classes não são consideradas esporas; marcações indevidas nelas são FP.

## Métricas

- `TP`: detecções de spur que casam com uma anotação spur.
- `FP`: detecções que não casam com nenhuma spur.
- `FN`: spurs anotadas que não receberam detecção.
- `Precisão = TP / (TP + FP)`.
- `Recall = TP / (TP + FN)`.
- `F1 = 2*Precisão*Recall / (Precisão+Recall)`.
- `tempo_medio_ms`: média do tempo de processamento por par, sem incluir leitura de imagem e salvamento dos resultados.

Arquivos por configuração: `por_imagem.csv`, `deteccoes.csv`, `resumo.json` e `exemplos/` com referência, teste, alinhada, diferença, máscara, caixas de detecção (vermelhas) e caixas de gabarito spur (verdes). `comparacao.json` resume os cenários.

## Investigação e apresentação

**Pergunta:** as regras geométricas de acréscimo de cobre e contato com trilhas melhoram o F1 para a classe spur em relação à simples diferença de imagens?

- Compare `baseline_sad` vs. `geometrica_sad`, com parâmetros idênticos.
- Relate as métricas reais produzidas em `resultados_dev` e `resultados_teste`, sem preencher resultados fictícios.
- Explore visualmente falsos positivos de classes 2 (short) e 5 (copper), além de esporas não detectadas.
- Registre qualquer parâmetro alterado e escolha-o **somente no desenvolvimento**. `test.txt` fica reservado para a medição final.
- Não aplique ajuste de parâmetros com base no conjunto de teste.

## Testes unitários

```bash
python -m unittest discover -s tests -v
```

## Limitações conhecidas

- A heurística geométrica **não garante** separação entre spur e outras classes. A classificação exige critérios morfológicos adicionais ou outra abordagem clássica, a desenvolver mediante análise do conjunto de desenvolvimento.
- SSD/SAD por translação não corrige escala nem rotação.
- Deslocamentos maiores que `--raio` não podem ser corrigidos.
- Amostragem espacial do alinhamento acelera o cálculo, mas pode reduzir sua estabilidade em padrões periódicamente repetidos.
- O valor de resposta não é probabilidade calibrada.
- O resultado ainda precisa ser **executado e medido na base completa** antes de ser apresentado como desempenho obtido.

## Crédito e licença

Dados: DeepPCB, *On-line PCB Defect Detector On A New PCB Defect Dataset*, https://github.com/tangsanli5201/DeepPCB. Os autores indicam uso do dataset para pesquisa. Este repositório entrega somente o código do trabalho; os dados devem ser obtidos da origem, respeitando suas condições de uso.
