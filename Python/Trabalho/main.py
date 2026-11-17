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

SPUR = 4


def carregar_imagem(caminho, modo=cv2.IMREAD_GRAYSCALE):
    """Carrega imagens mesmo quando o caminho contém caracteres Unicode no Windows."""
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
        pasta = raiz / caminho.parent
        teste = pasta / f"{base}_test.jpg"
        referencia = pasta / f"{base}_temp.jpg"
        anotacao = raiz / anotacao_rel
        pares.append((base, referencia, teste, anotacao))
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

def alinhar_busca_local(referencia, teste, raio=4, passo=3, metodo="sad"):
    """Busca exaustiva de translação (dx,dy) minimizando SAD ou SSD.

    Para cada deslocamento, compara as mesmas regiões válidas de referência/teste.
    O cálculo é desenvolvido aqui: NÃO usa alignECC nem matchTemplate.
    A borda de largura `raio` é excluída para que todas as hipóteses
    tenham exatamente o mesmo número de pixels na função de custo.
    """
    if referencia.shape != teste.shape:
        raise ValueError("As imagens do par devem ter o mesmo tamanho")
    h, w = referencia.shape
    if h <= 2 * raio or w <= 2 * raio:
        raise ValueError("Imagem muito pequena para o raio de busca")
    ys = slice(raio, h - raio, passo)
    xs = slice(raio, w - raio, passo)
    ref = referencia[ys, xs].astype(np.int16)
    melhor = (float("inf"), 0, 0)
    for dy in range(-raio, raio + 1):
        for dx in range(-raio, raio + 1):
            amostra = teste[raio - dy:h - raio - dy:passo,
                            raio - dx:w - raio - dx:passo].astype(np.int16)
            delta = ref.astype(np.float32) - amostra.astype(np.float32)
            custo = np.mean(np.abs(delta) if metodo == "sad" else delta * delta)
            if custo < melhor[0]:
                melhor = (float(custo), dx, dy)
    _, dx, dy = melhor
    matriz = np.float32([[1, 0, dx], [0, 1, dy]])
    alinhada = cv2.warpAffine(teste, matriz, (w, h), flags=cv2.INTER_NEAREST,
                              borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    valido = cv2.warpAffine(np.full_like(teste, 255), matriz, (w, h),
                            flags=cv2.INTER_NEAREST, borderMode=cv2.BORDER_CONSTANT,
                            borderValue=0)
    return alinhada, valido, dx, dy, melhor[0]


def preparar(referencia, teste, metodo="sad", raio=4):
    # Pequena suavização somente para a função de custo do alinhamento.
    a = cv2.GaussianBlur(referencia, (3, 3), 0)
    b = cv2.GaussianBlur(teste, (3, 3), 0)
    _, _, dx, dy, custo = alinhar_busca_local(a, b, raio=raio, metodo=metodo)
    h, w = teste.shape
    m = np.float32([[1, 0, dx], [0, 1, dy]])
    alinhada = cv2.warpAffine(teste, m, (w, h), flags=cv2.INTER_NEAREST,
                              borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    valido = cv2.warpAffine(np.full_like(teste, 255), m, (w, h),
                            flags=cv2.INTER_NEAREST, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    return alinhada, valido, dx, dy, custo


# =============================================================================
# Detecção de esporas
# =============================================================================

def detectar(referencia, teste_alinhado, valido, versao="geometrica", limiar=45,
             area_min=5, area_max=1800, max_lado=100):
    """Baseline: diferenças absolutas; geométrica: cobre acrescentado e conectado.

    A orientação do cobre (claro/escuro) é estimada SOMENTE pela referência.
    Não são consultadas anotações nesta função.
    """
    diferenca = cv2.absdiff(referencia, teste_alinhado)
    _, mascara_dif = cv2.threshold(diferenca, limiar, 255, cv2.THRESH_BINARY)
    mascara_dif = cv2.bitwise_and(mascara_dif, valido)
    kernel = np.ones((3, 3), np.uint8)
    mascara_dif = cv2.morphologyEx(mascara_dif, cv2.MORPH_OPEN, kernel)

    if versao == "geometrica":
        _, ref_otsu = cv2.threshold(referencia, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        _, tst_otsu = cv2.threshold(teste_alinhado, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        # A classe menos frequente da referência corresponde aproximadamente ao cobre.
        if np.count_nonzero(ref_otsu) > ref_otsu.size / 2:
            ref_otsu = cv2.bitwise_not(ref_otsu)
            tst_otsu = cv2.bitwise_not(tst_otsu)
        acrescimo = cv2.bitwise_and(tst_otsu, cv2.bitwise_not(ref_otsu))
        mascara = cv2.bitwise_and(acrescimo, mascara_dif)
        mascara = cv2.morphologyEx(mascara, cv2.MORPH_CLOSE, kernel)
        mascara = cv2.bitwise_and(mascara, valido)
        vizinhanca = cv2.dilate(ref_otsu, kernel, iterations=2)
    else:
        mascara = mascara_dif
        vizinhanca = None

    total, rotulos, stats, _ = cv2.connectedComponentsWithStats(mascara, 8)
    deteccoes = []
    for i in range(1, total):
        x, y, w, h, area = map(int, stats[i])
        if not area_min <= area <= area_max or max(w, h) > max_lado:
            continue
        recorte = rotulos[y:y+h, x:x+w] == i
        if versao == "geometrica":
            # Espora é crescimento de cobre que encosta numa trilha existente.
            contato = np.count_nonzero(recorte & (vizinhanca[y:y+h, x:x+w] > 0))
            if contato == 0:
                continue
            # Uma estrutura muito extensa é menos típica de uma espora curta.
            if min(w, h) < 2 or max(w, h) / max(1, min(w, h)) > 7:
                continue
        # É uma medida de resposta, NÃO probabilidade calibrada de spur.
        resposta = float(np.mean(diferenca[y:y+h, x:x+w][recorte]) / 255)
        deteccoes.append({"bbox": (x, y, x+w, y+h), "area": area,
                          "largura": w, "altura": h, "resposta": round(resposta, 4)})
    return deteccoes, diferenca, mascara


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


def avaliar(deteccoes, anotacoes, iou_min=0.33):
    """Casamento 1:1, greedy por IoU, apenas com gabaritos spur.

    Defeitos de outras classes NÃO são convertidos em positivos.
    Se o detector os marcar como spur, contam como falso positivo.
    """
    gt = [a["bbox"] for a in anotacoes if a["classe"] == SPUR]
    pares = []
    for i, det in enumerate(deteccoes):
        for j, caixa in enumerate(gt):
            valor = iou(det["bbox"], caixa)
            if valor >= iou_min:
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
    vis = cv2.cvtColor(alinhada, cv2.COLOR_GRAY2BGR)
    for d in dets:
        x1, y1, x2, y2 = d["bbox"]
        cv2.rectangle(vis, (x1, y1), (x2, y2), (0, 0, 255), 2)
    gt_vis = cv2.cvtColor(alinhada, cv2.COLOR_GRAY2BGR)
    for a in anotacoes:
        if a["classe"] == SPUR:
            x1, y1, x2, y2 = a["bbox"]
            cv2.rectangle(gt_vis, (x1, y1), (x2, y2), (0, 255, 0), 2)
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
    if args.limite > 0:
        pares = pares[:args.limite]
    if not pares:
        raise RuntimeError("Lista vazia")
    configuracoes = ([("baseline", "sad"), ("geometrica", "sad")]
                     if args.comparar else [(args.versao, args.alinhamento)])
    resumo = {}
    for versao, metodo in configuracoes:
        pasta = saida / (versao + "_" + metodo)
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
            inicio = time.perf_counter()
            alinhada, valido, dx, dy, custo = preparar(ref, tst, metodo=metodo, raio=args.raio)
            dets, diferenca, mascara = detectar(ref, alinhada, valido, versao=versao,
                                                 limiar=args.limiar, area_min=args.area_min)
            tempo = (time.perf_counter() - inicio) * 1000
            t, f, n = avaliar(dets, anotacoes, iou_min=args.iou)
            tp += t; fp += f; fn += n
            tempos.append(tempo)
            linhas.append({"imagem": nome, "versao": versao, "alinhamento": metodo,
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
                "parametros": {"limiar": args.limiar, "area_min": args.area_min,
                               "raio": args.raio, "iou_min": args.iou}}
        (pasta / "resumo.json").write_text(json.dumps(info, indent=2, ensure_ascii=False), encoding="utf-8")
        resumo[versao + "_" + metodo] = info
        print(f"{versao} / {metodo}: " + json.dumps(info, ensure_ascii=False))
    (saida / "comparacao.json").write_text(json.dumps(resumo, indent=2, ensure_ascii=False), encoding="utf-8")


# =============================================================================
# Interface de linha de comando
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Inspeção clássica de esporas - DeepPCB")

    # Caminhos e seleção do conjunto de dados
    parser.add_argument("--dados", required=True, help="Pasta PCBData original do DeepPCB")
    parser.add_argument("--saida", default="resultados")
    parser.add_argument("--divisao", choices=["trainval", "test"], default="trainval")
    parser.add_argument("--limite", type=int, default=0, help="0 = todas as imagens da divisão")
    parser.add_argument("--salvar-exemplos", type=int, default=8)

    # Estratégias de detecção e alinhamento
    parser.add_argument("--comparar", action="store_true", help="Baseline x geométrica (mesmo SAD)")
    parser.add_argument("--versao", choices=["baseline", "geometrica"], default="geometrica")
    parser.add_argument("--alinhamento", choices=["sad", "ssd"], default="sad")

    # Parâmetros numéricos do processamento e da avaliação
    parser.add_argument("--raio", type=int, default=4)
    parser.add_argument("--limiar", type=int, default=45)
    parser.add_argument("--area-min", type=int, default=5)
    parser.add_argument("--iou", type=float, default=0.33)

    args = parser.parse_args()

    # Validação dos valores recebidos
    if args.raio < 0 or args.limiar not in range(256) or args.area_min < 1 or not (0 <= args.iou <= 1):
        parser.error("Parâmetros inválidos")

    executar(args)


# Ponto de entrada do programa
if __name__ == "__main__":
    main()
