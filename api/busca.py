#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Logica de busca da API (equivalente a rag/buscar.py, mas consultando o Supabase
em vez de arquivos locais).

A normalizacao de texto usada na chave do cache espelha a de rag/buscar.py.
"""

import hashlib
import re
import unicodedata


def normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto.lower())
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9\s]", " ", texto)


def chave_cache(pergunta: str, k: int) -> str:
    base = f"{normalizar(pergunta).strip()}|{k}"
    return hashlib.sha256(base.encode("utf-8")).hexdigest()


def gerar_embedding_pergunta(cliente, pergunta: str, modelo: str):
    return cliente.embeddings.create(model=modelo, input=[pergunta]).data[0].embedding


def limpar_trecho(texto: str, limite: int = 600) -> str:
    """Remove markdown de imagem/link antes de truncar (evita cortar no meio de uma URL)."""
    texto = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", texto)
    texto = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", texto)
    # sobra de uma tag de imagem cortada no limite do chunk anterior (ex.:
    # ".../arquivo.png?123)" sem o "![](" correspondente, que ficou no chunk de tras)
    texto = re.sub(r"^[^\s()]*\)", "", texto)
    texto = re.sub(r"\n{2,}", "\n\n", texto).strip()
    return texto[:limite]


def montar_resultados(linhas, k: int):
    """Converte as linhas do banco (banco.buscar_trechos_*) em resultados deduplicados por artigo."""
    resultados = []
    vistos = set()
    for artigo_id, trecho, titulo, categoria, pasta, url, imagens, videos, score in linhas:
        if artigo_id in vistos:
            continue
        vistos.add(artigo_id)
        resultados.append({
            "artigo_id": artigo_id,
            "titulo": titulo,
            "categoria": categoria,
            "pasta": pasta,
            "url": url,
            "score": round(float(score), 4),
            "trecho": limpar_trecho(trecho),
            "imagens": imagens or [],
            "videos": videos or [],
        })
        if len(resultados) >= k:
            break
    return resultados
