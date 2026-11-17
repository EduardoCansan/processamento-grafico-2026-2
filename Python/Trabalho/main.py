# =============================================================================
# Importação e configuração geral
# =============================================================================
import argparse
import csv
import json
import time
from pathlib import Path
import cv2
import numpy as np

SPUR = 4  # Classe espora do DeepPCB.
# Valores iniciais; ajustar somente em imagens de trainval.
RAIO = 4
LIMIAR = 45
AREA_MIN = 5
AREA_MAX = 1800
MAX_LADO = 100
IOU_MIN = 0.33
SALVAR_EXEMPLOS = 8

# Hipotese de polaridade do cobre: conferir visualmente em trainval.
# True = cobre claro; False = cobre escuro. Nao calibrar pelo test.txt.
COBRE_CLARO = True


def carregar_imagem(caminho, modo=cv2.IMREAD_GRAYSCALE):
    # Aula_1/atividade_01/atividade_01.py, linhas 9-12: leitura/validacao.
    # Adaptacao com NumPy para suportar caminhos Unicode no Windows.
    dados = np.fromfile(str(caminho), dtype=np.uint8)
    return cv2.imdecode(dados, modo)


# =============================================================================
# Leitura do conjunto de dados
# =============================================================================

def ler_lista(raiz, divisao):
    # A lista oficial usa caminhos *.jpg sem _test; eles indicam o identificador do par.
    lista = raiz / ("trainval.txt" if divisao == "trainval" else "test.txt")
    if not lista.is_file():
        raise FileNotFoundError(f"Lista oficial ausente: {lista}")
    pares = []
    for linha in lista.read_text(encoding="utf-8").splitlines():
        if not linha.strip():
            continue
        imagem_rel, anotacao_rel = linha.split()[:2]
        caminho = Path(imagem_rel)
        base = caminho.stem
        nome = str(caminho.with_suffix("")).replace("\\", "__").replace("/", "__")
        pasta = raiz / caminho.parent
        teste = pasta / f"{base}_test.jpg"
        referencia = pasta / f"{base}_temp.jpg"
        anotacao = raiz / anotacao_rel
        pares.append((nome, referencia, teste, anotacao))
    return pares


def ler_anotacoes(arquivo):
    # Cada linha DeepPCB: x1 y1 x2 y2 id_classe (id spur = 4).
    caixas = []
    if not arquivo.is_file():
        raise FileNotFoundError(f"Anotação ausente: {arquivo}")
    for linha in arquivo.read_text(encoding="utf-8").splitlines():
        if not linha.strip():
            continue
        partes = linha.replace(",", " ").split()
        if len(partes) != 5:
            raise ValueError(f"Anotação inválida em {arquivo}: {linha}")
        x1, y1, x2, y2, classe = map(int, partes)
        caixas.append({"bbox": (x1, y1, x2, y2), "classe": classe})
    return caixas


# =============================================================================
# Alinhamento e preparação das imagens
# =============================================================================

def alinhar_busca_local(referencia, teste, raio=RAIO, passo=3):
    """Implementacao propria: busca translação por SAD, devolve dx, dy, custo."""
    # Aula_2/exemplo_01_correlacao_manual.py, linhas 26-41: referencia de loops.
    # Aula_3/exemplos/exemplo_10_benchmark.py, linhas 35-44: NumPy em lote.
    # A correlacao da Aula 2 NAO substitui a busca por translacao exigida.
    if referencia.shape != teste.shape:
        raise ValueError("As imagens do par devem ter o mesmo tamanho")
    altura, largura = referencia.shape
    if raio < 0 or passo < 1 or altura <= 2 * raio or largura <= 2 * raio:
        raise ValueError("Raio/passo incompativel com as imagens")

    amostra_ref = referencia[raio:altura-raio:passo,
                             raio:largura-raio:passo].astype(np.float32)
    menor_custo = float("inf")
    melhor_dx = melhor_dy = 0
    for dy in range(-raio, raio + 1):
        for dx in range(-raio, raio + 1):
            amostra_teste = teste[raio-dy:altura-raio-dy:passo,
                                  raio-dx:largura-raio-dx:passo].astype(np.float32)
            custo = float(np.mean(np.abs(amostra_ref - amostra_teste)))
            if custo < menor_custo:
                menor_custo = custo
                melhor_dx, melhor_dy = dx, dy
    return melhor_dx, melhor_dy, menor_custo

def preparar(referencia, teste):
    # Aula_2/exemplo_03_gaussiano.py, linhas 14-19: suavizacao leve.
    ref_suave = cv2.GaussianBlur(referencia, (3, 3), 0)
    teste_suave = cv2.GaussianBlur(teste, (3, 3), 0)
    dx, dy, custo = alinhar_busca_local(ref_suave, teste_suave)
    altura, largura = teste.shape
    matriz = np.float32([[1, 0, dx], [0, 1, dy]])
    # Aplica o deslocamento apenas uma vez sobre a imagem original.
    alinhada = cv2.warpAffine(teste, matriz, (largura, altura),
                              flags=cv2.INTER_NEAREST, borderValue=0)
    valido = cv2.warpAffine(np.full_like(teste, 255), matriz,
                            (largura, altura), flags=cv2.INTER_NEAREST,
                            borderValue=0)
    return alinhada, valido, dx, dy, custo

# =============================================================================
# Detecção de esporas
# =============================================================================

def detectar(referencia, teste_alinhado, valido, versao="geometrica"):
    """Detecta candidatos com processamento classico, sem consultar anotacoes."""
    # Aula_3/exemplos/exemplo_13_movimento.py, linhas 41-50: absdiff + threshold.
    # Aula_1/exemplos/exemplo_10.py, linhas 12-17: limiarizacao binaria.
    diferenca = cv2.absdiff(referencia, teste_alinhado)
    _, mascara = cv2.threshold(diferenca, LIMIAR, 255, cv2.THRESH_BINARY)
    mascara = cv2.bitwise_and(mascara, valido)

    # Sem abertura 3x3: ela pode apagar esporas muito pequenas.
    # Verificar essa escolha nas imagens de desenvolvimento.
    if versao == "geometrica":
        # Implementacao propria para DeepPCB: cobre acrescentado perto de
        # uma trilha da referencia. Nao e uma classificacao perfeita de spur.
        # O MESMO limiar de Otsu e usado nas duas imagens.
        limiar_cobre, ref_cobre = cv2.threshold(
            referencia, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        _, teste_cobre = cv2.threshold(
            teste_alinhado, limiar_cobre, 255, cv2.THRESH_BINARY)
        if not COBRE_CLARO:
            # Aula_1/exemplos/exemplo_09.py, linha 12: bitwise_not.
            ref_cobre = cv2.bitwise_not(ref_cobre)
            teste_cobre = cv2.bitwise_not(teste_cobre)
        acrescimo = cv2.bitwise_and(teste_cobre, cv2.bitwise_not(ref_cobre))
        mascara = cv2.bitwise_and(mascara, acrescimo)
        mascara = cv2.bitwise_and(mascara, valido)
        borda_trilha = cv2.dilate(ref_cobre, np.ones((3, 3), np.uint8),
                                  iterations=1)
    else:
        borda_trilha = None

    # Aula_3/exemplos/exemplo_15_caixas_movimento.py, linhas 51-62:
    # contornos sao uma alternativa; mantemos componentes para contar pixels
    # pequenos (contourArea nao corresponde a quantidade de pixels).
    total, rotulos, medidas, _ = cv2.connectedComponentsWithStats(mascara, 8)
    deteccoes = []
    for i in range(1, total):
        x, y, largura, altura, area = map(int, medidas[i])
        if not AREA_MIN <= area <= AREA_MAX or max(largura, altura) > MAX_LADO:
            continue
        pixels = rotulos[y:y+altura, x:x+largura] == i

        if versao == "geometrica":
            # Uma espora deve ser uma protuberancia curta junto ao cobre.
            contato = np.count_nonzero(
                pixels & (borda_trilha[y:y+altura, x:x+largura] > 0))
            if contato == 0 or min(largura, altura) < 2:
                continue
            if max(largura, altura) / min(largura, altura) > 7:
                continue

        resposta = float(np.mean(diferenca[y:y+altura, x:x+largura][pixels]) / 255)
        deteccoes.append({
            "bbox": (x, y, x + largura, y + altura),
            "area": area, "largura": largura, "altura": altura,
            "resposta": round(resposta, 4)
        })
    return deteccoes, diferenca, mascara


def converter_caixas_para_teste(deteccoes, dx, dy, largura, altura):
    """Converte caixas da imagem alinhada para o teste original."""
    resultado = []
    for det in deteccoes:
        x1, y1, x2, y2 = det["bbox"]
        x1 = max(0, min(largura, x1 - dx))
        x2 = max(0, min(largura, x2 - dx))
        y1 = max(0, min(altura, y1 - dy))
        y2 = max(0, min(altura, y2 - dy))
        if x2 > x1 and y2 > y1:
            resultado.append({**det, "bbox": (x1, y1, x2, y2)})
    return resultado


# =============================================================================
# Avaliação dos resultados
# =============================================================================

def iou(a, b):
    x1, y1 = max(a[0], b[0]), max(a[1], b[1])
    x2, y2 = min(a[2], b[2]), min(a[3], b[3])
    inter = max(0, x2-x1) * max(0, y2-y1)
    aa = max(0, a[2]-a[0]) * max(0, a[3]-a[1])
    bb = max(0, b[2]-b[0]) * max(0, b[3]-b[1])
    return inter / (aa + bb - inter) if aa + bb - inter else 0.0


def avaliar(deteccoes, anotacoes, iou_min=IOU_MIN):
    """Casamento 1:1, greedy por IoU, apenas com gabaritos spur.

    Defeitos de outras classes NÃO são convertidos em positivos.
    Se o detector os marcar como spur, contam como falso positivo.
    """
    gt = [a["bbox"] for a in anotacoes if a["classe"] == SPUR]
    pares = []
    for i, det in enumerate(deteccoes):
        for j, caixa in enumerate(gt):
            valor = iou(det["bbox"], caixa)
            if valor > iou_min:
                pares.append((valor, i, j))
    usados_d, usados_g = set(), set()
    for _, i, j in sorted(pares, reverse=True):
        if i not in usados_d and j not in usados_g:
            usados_d.add(i)
            usados_g.add(j)
    return len(usados_d), len(deteccoes) - len(usados_d), len(gt) - len(usados_g)


# =============================================================================
# Geração das imagens de saída
# =============================================================================

def salvar_imagens(destino, referencia, teste, alinhada, diferenca, mascara, dets, anotacoes):
    destino.mkdir(parents=True, exist_ok=True)
    # Aula_3/exemplos/exemplo_15_caixas_movimento.py, linhas 64-67:
    # desenha caixas na imagem de TESTE ORIGINAL.
    vis = cv2.cvtColor(teste, cv2.COLOR_GRAY2BGR)
    for d in dets:
        x1, y1, x2, y2 = d["bbox"]
        cv2.rectangle(vis, (x1, y1), (x2, y2), (0, 0, 255), 2)
    gt_vis = cv2.cvtColor(teste, cv2.COLOR_GRAY2BGR)
    for a in anotacoes:
        if a["classe"] == SPUR:
            x1, y1, x2, y2 = a["bbox"]
            cv2.rectangle(gt_vis, (x1, y1), (x2, y2), (0, 255, 0), 2)
    # Aula_1/atividade_01/atividade_01.py, linhas 33-41: salvar imagens.
    for nome, img in [("referencia", referencia), ("teste", teste),
                      ("alinhada", alinhada), ("diferenca", diferenca),
                      ("mascara", mascara), ("deteccoes", vis), ("gabarito_spur", gt_vis)]:
        cv2.imwrite(str(destino / (nome + ".png")), img)


# =============================================================================
# Execução do experimento e exportação dos resultados
# =============================================================================

def executar(args):
    raiz = Path(args.dados).resolve()
    saida = Path(args.saida).resolve()
    saida.mkdir(parents=True, exist_ok=True)
    pares = ler_lista(raiz, args.divisao)
    if args.divisao == "trainval":
        # Separacao fixa: a cada cinco pares, um e reservado para validacao.
        # O gabarito nunca e usado para selecionar candidatos na deteccao.
        pares = [par for i, par in enumerate(pares)
                 if (i % 5 == 0) == (args.etapa == "validacao")]
    if args.limite > 0:
        pares = pares[:args.limite]
    if not pares:
        raise RuntimeError("Lista vazia")
    configuracoes = (["baseline", "geometrica"] if args.comparar else ["geometrica"])
    resumo = {}
    for versao in configuracoes:
        pasta = saida / (versao + "_sad")
        pasta.mkdir(parents=True, exist_ok=True)
        linhas = []
        detalhes = []
        tp = fp = fn = 0
        tempos = []
        for indice, (nome, ref_path, tst_path, anot_path) in enumerate(pares):
            ref = carregar_imagem(ref_path)
            tst = carregar_imagem(tst_path)
            if ref is None or tst is None:
                raise FileNotFoundError(f"Par ausente: {ref_path} / {tst_path}")
            anotacoes = ler_anotacoes(anot_path)
            if ref.shape != tst.shape:
                raise ValueError(f"Imagens com dimensoes diferentes: {nome}")
            # Aula_3/exemplos/exemplo_09_desempenho.py, linhas 26-35:
            # mede o tempo de alinhamento e deteccao em milissegundos.
            inicio = time.perf_counter()
            alinhada, valido, dx, dy, custo = preparar(ref, tst)
            dets_alinhadas, diferenca, mascara = detectar(
                ref, alinhada, valido, versao=versao)
            dets = converter_caixas_para_teste(
                dets_alinhadas, dx, dy, tst.shape[1], tst.shape[0])
            tempo = (time.perf_counter() - inicio) * 1000
            # Anotacoes so entram na avaliacao, nunca no detector.
            t, f, n = avaliar(dets, anotacoes)
            tp += t
            fp += f
            fn += n
            tempos.append(tempo)
            linhas.append({"imagem": nome, "versao": versao, "alinhamento": "sad",
                           "dx": dx, "dy": dy, "custo_registro": round(custo, 3),
                           "gt_spur": sum(a["classe"] == SPUR for a in anotacoes),
                           "detectados": len(dets), "tp": t, "fp": f, "fn": n,
                           "tempo_ms": round(tempo, 3)})
            for d in dets:
                detalhes.append({"imagem": nome, **d})
            if indice < args.salvar_exemplos:
                salvar_imagens(pasta / "exemplos" / nome, ref, tst, alinhada,
                               diferenca, mascara, dets, anotacoes)
        with (pasta / "por_imagem.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=linhas[0].keys()); w.writeheader(); w.writerows(linhas)
        with (pasta / "deteccoes.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=["imagem", "bbox", "area", "largura", "altura", "resposta"])
            w.writeheader(); w.writerows(detalhes)
        precisao = tp / (tp + fp) if tp + fp else 0
        recall = tp / (tp + fn) if tp + fn else 0
        f1 = 2 * precisao * recall / (precisao + recall) if precisao + recall else 0
        info = {"imagens": len(linhas), "tp": tp, "fp": fp, "fn": fn,
                "precisao": round(precisao, 4), "recall": round(recall, 4),
                "f1": round(f1, 4), "tempo_medio_ms": round(float(np.mean(tempos)), 3),
                "divisao": args.divisao,
                "etapa": args.etapa if args.divisao == "trainval" else "teste",
                "parametros": {"limiar": LIMIAR, "area_min": AREA_MIN,
                               "raio": RAIO, "iou_min": IOU_MIN,
                               "cobre_claro": COBRE_CLARO}}
        (pasta / "resumo.json").write_text(json.dumps(info, indent=2, ensure_ascii=False), encoding="utf-8")
        resumo[versao + "_sad"] = info
        print(f"{versao} / sad: " + json.dumps(info, ensure_ascii=False))
    (saida / "comparacao.json").write_text(json.dumps(resumo, indent=2, ensure_ascii=False), encoding="utf-8")


# =============================================================================
# Interface de linha de comando
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Inspecao classica de esporas - DeepPCB")
    parser.add_argument("--dados", required=True, help="Pasta PCBData do DeepPCB")
    parser.add_argument("--saida", default="resultados")
    parser.add_argument("--divisao", choices=["trainval", "test"],
                        default="trainval")
    parser.add_argument("--etapa", choices=["desenvolvimento", "validacao"],
                        default="desenvolvimento",
                        help="Subconjunto de trainval; ignorado se --divisao test")
    parser.add_argument("--limite", type=int, default=0,
                        help="0 = todas as imagens do subconjunto")
    parser.add_argument("--comparar", action="store_true",
                        help="Comparar baseline e geometrica com SAD")
    parser.add_argument("--salvar-exemplos", type=int, default=SALVAR_EXEMPLOS)
    args = parser.parse_args()

    if args.limite < 0 or args.salvar_exemplos < 0:
        parser.error("--limite e --salvar-exemplos devem ser >= 0")
    executar(args)


# Ponto de entrada do programa
if __name__ == "__main__":
    main()
