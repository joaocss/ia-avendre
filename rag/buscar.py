#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Busca semantica na base de conhecimento da Avendre (o coracao do RAG).

Fluxo:
  1. Recebe a pergunta do usuario.
  2. Se houver indice de embeddings + OPENAI_API_KEY -> busca semantica (cosseno).
  3. Caso contrario -> fallback por palavra-chave (funciona offline, sem custo).
  4. Retorna os trechos mais relevantes com titulo, link, imagens e videos.

Uso:
  python buscar.py "como consultar meu extrato no avendre pay"
  python buscar.py "erro de login conta inexistente" --k 4 --json

A skill "suporte-avendre" chama este script e usa o JSON para montar a resposta.
"""

import argparse
import glob
import json
import math
import os
import re
import unicodedata

RAIZ = os.path.dirname(__file__)
PASTA_BASE = os.path.join(RAIZ, "..", "base_conhecimento")
PASTA_ARTIGOS = os.path.join(PASTA_BASE, "artigos")
ARQ_INDICE = os.path.join(PASTA_BASE, "indice_embeddings.json")
ARQ_MANIFESTO = os.path.join(PASTA_BASE, "manifesto.json")
MODELO_EMBEDDING = "text-embedding-3-small"

PALAVRAS_VAZIAS = set("""a o e de da do das dos em no na nos nas um uma para por com que
como meu minha seu sua eu voce esta este isso ao aos as os se sobre qual quais onde quando
nao sim ja tem ter e ou pra pelo pela""".split())


def normalizar(texto):
    texto = unicodedata.normalize("NFKD", texto.lower())
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9\s]", " ", texto)


def tokenizar(texto):
    return [t for t in normalizar(texto).split() if t and t not in PALAVRAS_VAZIAS and len(t) > 2]


# ---------- busca semantica (embeddings) ----------

def cosseno(a, b):
    soma = na = nb = 0.0
    for x, y in zip(a, b):
        soma += x * y
        na += x * x
        nb += y * y
    if na == 0 or nb == 0:
        return 0.0
    return soma / (math.sqrt(na) * math.sqrt(nb))


def busca_semantica(pergunta, k):
    with open(ARQ_INDICE, encoding="utf-8") as f:
        indice = json.load(f)
    from openai import OpenAI
    cliente = OpenAI()
    consulta = cliente.embeddings.create(model=indice.get("modelo", MODELO_EMBEDDING),
                                         input=[pergunta]).data[0].embedding
    pontuados = []
    for r in indice["registros"]:
        pontuados.append((cosseno(consulta, r["embedding"]), r))
    pontuados.sort(key=lambda x: x[0], reverse=True)
    return [(s, r) for s, r in pontuados[:k]], "semantica"


# ---------- fallback por palavra-chave ----------

def carregar_trechos_para_keyword():
    """Monta uma lista de trechos a partir do indice (se existir) ou dos .md."""
    if os.path.exists(ARQ_INDICE):
        with open(ARQ_INDICE, encoding="utf-8") as f:
            return json.load(f)["registros"]
    registros = []
    for caminho in sorted(glob.glob(os.path.join(PASTA_ARTIGOS, "*.md"))):
        with open(caminho, encoding="utf-8") as f:
            texto = f.read()
        meta = {}
        if texto.startswith("---"):
            fim = texto.find("\n---", 3)
            bloco, corpo = texto[3:fim], texto[fim + 4:]
            for linha in bloco.splitlines():
                if ":" in linha:
                    ch, va = linha.split(":", 1)
                    va = va.strip()
                    try:
                        va = json.loads(va)
                    except Exception:
                        pass
                    meta[ch.strip()] = va
        else:
            corpo = texto
        registros.append({
            "id_artigo": meta.get("id", ""), "titulo": meta.get("titulo", ""),
            "categoria": meta.get("categoria", ""), "produto": meta.get("produto", ""),
            "pasta": meta.get("pasta", ""), "url": meta.get("url", ""),
            "imagens": meta.get("imagens", []), "videos": meta.get("videos", []),
            "n_trecho": 0, "trecho": corpo,
        })
    return registros


def busca_keyword(pergunta, k):
    registros = carregar_trechos_para_keyword()
    termos = tokenizar(pergunta)
    # frequencia de documento para dar peso a termos raros (idf simples)
    df = {}
    docs_tokens = []
    for r in registros:
        toks = tokenizar(f"{r['titulo']} {r['titulo']} {r['trecho']}")  # titulo pesa 2x
        docs_tokens.append(toks)
        for t in set(toks):
            df[t] = df.get(t, 0) + 1
    n = max(len(registros), 1)
    pontuados = []
    for r, toks in zip(registros, docs_tokens):
        conjunto = {}
        for t in toks:
            conjunto[t] = conjunto.get(t, 0) + 1
        score = 0.0
        for t in termos:
            if t in conjunto:
                idf = math.log((n + 1) / (df.get(t, 0) + 1)) + 1
                score += conjunto[t] * idf
        if score > 0:
            pontuados.append((score, r))
    pontuados.sort(key=lambda x: x[0], reverse=True)
    return pontuados[:k], "palavra-chave"


# ---------- montagem do resultado ----------

def deduplicar_por_artigo(resultados, k):
    vistos = {}
    saida = []
    for score, r in resultados:
        chave = r.get("id_artigo") or r.get("url")
        if chave in vistos:
            continue
        vistos[chave] = True
        saida.append((score, r))
        if len(saida) >= k:
            break
    return saida


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("pergunta", help="pergunta do usuario")
    parser.add_argument("--k", type=int, default=4, help="quantos artigos retornar")
    parser.add_argument("--json", action="store_true", help="saida em JSON")
    args = parser.parse_args()

    tem_indice = os.path.exists(ARQ_INDICE)
    tem_chave = bool(os.environ.get("OPENAI_API_KEY"))

    try:
        if tem_indice and tem_chave:
            brutos, metodo = busca_semantica(args.pergunta, args.k * 3)
        else:
            brutos, metodo = busca_keyword(args.pergunta, args.k * 3)
    except Exception as e:
        brutos, metodo = busca_keyword(args.pergunta, args.k * 3)
        metodo += f" (fallback: {e})"

    resultados = deduplicar_por_artigo(brutos, args.k)

    saida = {
        "pergunta": args.pergunta,
        "metodo": metodo,
        "resultados": [{
            "titulo": r["titulo"],
            "categoria": r.get("categoria", ""),
            "pasta": r.get("pasta", ""),
            "url": r["url"],
            "score": round(float(s), 4),
            "trecho": r["trecho"][:600],
            "imagens": r.get("imagens", []),
            "videos": r.get("videos", []),
        } for s, r in resultados],
    }

    if args.json:
        print(json.dumps(saida, ensure_ascii=False, indent=2))
    else:
        print(f"\nPergunta: {saida['pergunta']}   (metodo: {metodo})\n")
        for i, r in enumerate(saida["resultados"], 1):
            print(f"{i}. {r['titulo']}  [{r['pasta']}]  score={r['score']}")
            print(f"   {r['url']}")
            if r["imagens"]:
                print(f"   imagens: {len(r['imagens'])} | videos: {len(r['videos'])}")
            print()


if __name__ == "__main__":
    main()
