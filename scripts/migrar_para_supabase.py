#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Migra a base de conhecimento local (.md em base_conhecimento/artigos) para o
Supabase: grava artigos e trechos (com embeddings) nas tabelas `artigos` e
`trechos` definidas em db/esquema.sql.

Reaproveita a logica de chunking/embeddings de rag/construir_indice.py.
Idempotente: pode rodar de novo apos um re-scraping (faz upsert).

Uso:
  python scripts/migrar_para_supabase.py

Precisa de OPENAI_API_KEY e DATABASE_URL no .env (ver .env.example).
Dependencias extras: psycopg[binary,pool], pgvector (ver requisitos.txt).
"""

import glob
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "rag"))

from dotenv import load_dotenv
load_dotenv()

from construir_indice import ler_frontmatter, quebrar_em_trechos, MODELO_EMBEDDING

RAIZ = os.path.dirname(__file__)
PASTA_ARTIGOS = os.path.join(RAIZ, "..", "base_conhecimento", "artigos")
LOTE = 96


def gerar_embeddings(cliente, textos):
    resposta = cliente.embeddings.create(model=MODELO_EMBEDDING, input=textos)
    return [d.embedding for d in resposta.data]


def gravar_artigo(cursor, artigo_id, meta, corpo):
    from psycopg.types.json import Json

    cursor.execute(
        """
        insert into artigos (id, titulo, categoria, produto, pasta, url, imagens, videos, conteudo_markdown, atualizado_em)
        values (%s, %s, %s, %s, %s, %s, %s, %s, %s, now())
        on conflict (id) do update set
            titulo = excluded.titulo,
            categoria = excluded.categoria,
            produto = excluded.produto,
            pasta = excluded.pasta,
            url = excluded.url,
            imagens = excluded.imagens,
            videos = excluded.videos,
            conteudo_markdown = excluded.conteudo_markdown,
            atualizado_em = now()
        """,
        (
            artigo_id,
            meta.get("titulo", ""),
            meta.get("categoria", ""),
            meta.get("produto", ""),
            meta.get("pasta", ""),
            meta.get("url", ""),
            Json(meta.get("imagens", [])),
            Json(meta.get("videos", [])),
            corpo,
        ),
    )


def gravar_trecho(cursor, artigo_id, n_trecho, trecho, embedding):
    cursor.execute(
        """
        insert into trechos (artigo_id, n_trecho, trecho, embedding)
        values (%s, %s, %s, %s)
        on conflict (artigo_id, n_trecho) do update set
            trecho = excluded.trecho,
            embedding = excluded.embedding
        """,
        (artigo_id, n_trecho, trecho, embedding),
    )


def main():
    if not os.environ.get("OPENAI_API_KEY"):
        raise SystemExit("Defina OPENAI_API_KEY no .env antes de rodar.")
    if not os.environ.get("DATABASE_URL"):
        raise SystemExit("Defina DATABASE_URL no .env antes de rodar.")

    from openai import OpenAI
    import psycopg
    from pgvector.psycopg import register_vector

    cliente = OpenAI()
    conexao = psycopg.connect(os.environ["DATABASE_URL"])
    register_vector(conexao)

    arquivos = sorted(glob.glob(os.path.join(PASTA_ARTIGOS, "*.md")))
    if not arquivos:
        raise SystemExit(f"Nenhum artigo em {PASTA_ARTIGOS}. Rode antes: python scraper/raspar_base.py")

    total_artigos = 0
    total_trechos = 0

    with conexao:
        with conexao.cursor() as cursor:
            for caminho in arquivos:
                with open(caminho, encoding="utf-8") as f:
                    meta, corpo = ler_frontmatter(f.read())

                artigo_id = str(meta.get("id", "")).strip()
                if not artigo_id:
                    print(f"  [sem id] {caminho}")
                    continue

                gravar_artigo(cursor, artigo_id, meta, corpo)
                total_artigos += 1

                corpo_sem_titulo = re.sub(r"^#\s.*\n", "", corpo, count=1).strip()
                trechos = quebrar_em_trechos(corpo_sem_titulo)
                if not trechos:
                    continue

                textos = [f"{meta.get('titulo', '')}\n\n{t}" for t in trechos]
                vetores = []
                for inicio in range(0, len(textos), LOTE):
                    vetores.extend(gerar_embeddings(cliente, textos[inicio:inicio + LOTE]))

                for i, (trecho, vetor) in enumerate(zip(trechos, vetores)):
                    gravar_trecho(cursor, artigo_id, i, trecho, vetor)
                total_trechos += len(trechos)
                print(f"  ok  {meta.get('titulo', '')[:70]}  ({len(trechos)} trechos)")

    conexao.close()
    print(f"\nConcluido: {total_artigos} artigos, {total_trechos} trechos gravados no Supabase.")


if __name__ == "__main__":
    main()
