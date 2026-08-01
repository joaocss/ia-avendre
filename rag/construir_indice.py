#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Constroi o indice vetorial (RAG) da base de conhecimento da Avendre.

Le os artigos em Markdown de ../base_conhecimento/artigos, quebra cada
artigo em trechos (chunks), gera embeddings com a API da OpenAI
(modelo text-embedding-3-small) e grava tudo em indice_embeddings.json.

Uso:
  set OPENAI_API_KEY=sk-...        (Windows)   /  export OPENAI_API_KEY=sk-...  (Linux/Mac)
  python construir_indice.py

Dependencias: openai, tiktoken  (ver requisitos.txt)
"""

import glob
import json
import os
import re

from dotenv import load_dotenv
load_dotenv()

MODELO_EMBEDDING = "text-embedding-3-small"
TAMANHO_CHUNK = 900          # caracteres por trecho (aprox.)
SOBREPOSICAO = 150           # sobreposicao entre trechos

RAIZ = os.path.dirname(__file__)
PASTA_BASE = os.path.join(RAIZ, "..", "base_conhecimento")
PASTA_ARTIGOS = os.path.join(PASTA_BASE, "artigos")
ARQ_INDICE = os.path.join(PASTA_BASE, "indice_embeddings.json")


def ler_frontmatter(texto):
    """Extrai o frontmatter (yaml simples) e o corpo do markdown."""
    meta = {}
    corpo = texto
    if texto.startswith("---"):
        fim = texto.find("\n---", 3)
        if fim != -1:
            bloco = texto[3:fim].strip().splitlines()
            corpo = texto[fim + 4:].strip()
            for linha in bloco:
                if ":" in linha:
                    chave, valor = linha.split(":", 1)
                    valor = valor.strip()
                    try:
                        valor = json.loads(valor)
                    except Exception:
                        pass
                    meta[chave.strip()] = valor
    return meta, corpo


def quebrar_em_trechos(texto):
    """Divide o texto em trechos com sobreposicao, respeitando paragrafos."""
    texto = re.sub(r"\n{3,}", "\n\n", texto).strip()
    if len(texto) <= TAMANHO_CHUNK:
        return [texto] if texto else []
    trechos = []
    inicio = 0
    while inicio < len(texto):
        fim = inicio + TAMANHO_CHUNK
        corte = texto.rfind("\n", inicio, fim)   # tenta cortar numa quebra de linha
        if corte == -1 or corte <= inicio + 200:
            corte = fim
        trechos.append(texto[inicio:corte].strip())
        inicio = max(corte - SOBREPOSICAO, inicio + 1)
    return [t for t in trechos if t]


def gerar_embeddings(cliente, textos):
    """Gera embeddings em lote."""
    resposta = cliente.embeddings.create(model=MODELO_EMBEDDING, input=textos)
    return [d.embedding for d in resposta.data]


def main():
    if not os.environ.get("OPENAI_API_KEY"):
        raise SystemExit("Defina OPENAI_API_KEY antes de rodar. Ex.: set OPENAI_API_KEY=sk-...")

    from openai import OpenAI
    cliente = OpenAI()

    arquivos = sorted(glob.glob(os.path.join(PASTA_ARTIGOS, "*.md")))
    if not arquivos:
        raise SystemExit(f"Nenhum artigo em {PASTA_ARTIGOS}. Rode antes: python ../scraper/raspar_base.py")

    registros = []      # cada trecho vira um registro
    for caminho in arquivos:
        with open(caminho, encoding="utf-8") as f:
            meta, corpo = ler_frontmatter(f.read())
        # remove a linha de titulo duplicada
        corpo = re.sub(r"^#\s.*\n", "", corpo, count=1).strip()
        for i, trecho in enumerate(quebrar_em_trechos(corpo)):
            registros.append({
                "id_artigo": meta.get("id", ""),
                "titulo": meta.get("titulo", ""),
                "categoria": meta.get("categoria", ""),
                "produto": meta.get("produto", ""),
                "pasta": meta.get("pasta", ""),
                "url": meta.get("url", ""),
                "imagens": meta.get("imagens", []),
                "videos": meta.get("videos", []),
                "n_trecho": i,
                "trecho": trecho,
            })

    print(f"{len(arquivos)} artigos -> {len(registros)} trechos. Gerando embeddings...")

    # gera embeddings em lotes de 96
    LOTE = 96
    for inicio in range(0, len(registros), LOTE):
        bloco = registros[inicio:inicio + LOTE]
        textos = [f"{r['titulo']}\n\n{r['trecho']}" for r in bloco]
        vetores = gerar_embeddings(cliente, textos)
        for r, v in zip(bloco, vetores):
            r["embedding"] = v
        print(f"  {min(inicio + LOTE, len(registros))}/{len(registros)}")

    with open(ARQ_INDICE, "w", encoding="utf-8") as f:
        json.dump({
            "modelo": MODELO_EMBEDDING,
            "total_trechos": len(registros),
            "registros": registros,
        }, f, ensure_ascii=False)

    print(f"Indice gravado em {ARQ_INDICE}")


if __name__ == "__main__":
    main()
