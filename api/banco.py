#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Acesso ao Supabase (Postgres) para a API de suporte Avendre."""

import os

from psycopg_pool import ConnectionPool
from psycopg.types.json import Json
from pgvector.psycopg import register_vector

_pool: ConnectionPool | None = None


def obter_pool() -> ConnectionPool:
    global _pool
    if _pool is None:
        dsn = os.environ["DATABASE_URL"]
        _pool = ConnectionPool(dsn, min_size=1, max_size=5, configure=register_vector, open=True)
    return _pool


def obter_ou_criar_empresa(cursor, nome: str) -> str:
    cursor.execute("select id from empresas where nome = %s", (nome,))
    linha = cursor.fetchone()
    if linha:
        return str(linha[0])
    cursor.execute("insert into empresas (nome) values (%s) returning id", (nome,))
    return str(cursor.fetchone()[0])


def obter_ou_criar_usuario(cursor, empresa_id: str, email: str) -> str:
    cursor.execute(
        "select id from usuarios where empresa_id = %s and email = %s", (empresa_id, email)
    )
    linha = cursor.fetchone()
    if linha:
        return str(linha[0])
    cursor.execute(
        "insert into usuarios (empresa_id, email) values (%s, %s) returning id",
        (empresa_id, email),
    )
    return str(cursor.fetchone()[0])


def ler_cache(cursor, chave: str):
    cursor.execute("select resposta from cache_respostas where chave = %s", (chave,))
    linha = cursor.fetchone()
    return linha[0] if linha else None


def gravar_cache(cursor, chave: str, resposta: dict) -> None:
    cursor.execute(
        """
        insert into cache_respostas (chave, resposta) values (%s, %s)
        on conflict (chave) do update set resposta = excluded.resposta, criado_em = now()
        """,
        (chave, Json(resposta)),
    )


def gravar_pergunta(cursor, empresa_id, usuario_id, pergunta: str, metodo: str, veio_do_cache: bool) -> None:
    cursor.execute(
        """
        insert into perguntas (empresa_id, usuario_id, pergunta, metodo, veio_do_cache)
        values (%s, %s, %s, %s, %s)
        """,
        (empresa_id, usuario_id, pergunta, metodo, veio_do_cache),
    )


def buscar_trechos_similares(cursor, embedding, k: int):
    """Busca por similaridade vetorial (pgvector, distancia de cosseno)."""
    cursor.execute(
        """
        select a.id, t.trecho, a.titulo, a.categoria, a.pasta, a.url, a.imagens, a.videos,
               1 - (t.embedding <=> %s::vector) as score
        from trechos t
        join artigos a on a.id = t.artigo_id
        where t.embedding is not null
        order by t.embedding <=> %s::vector
        limit %s
        """,
        (embedding, embedding, k),
    )
    return cursor.fetchall()


def buscar_trechos_palavra_chave(cursor, pergunta: str, k: int):
    """Fallback offline: full-text search nativo do Postgres (sem precisar da API da OpenAI)."""
    cursor.execute(
        """
        select a.id, t.trecho, a.titulo, a.categoria, a.pasta, a.url, a.imagens, a.videos,
               ts_rank(to_tsvector('portuguese', t.trecho), plainto_tsquery('portuguese', %s)) as score
        from trechos t
        join artigos a on a.id = t.artigo_id
        where to_tsvector('portuguese', t.trecho) @@ plainto_tsquery('portuguese', %s)
        order by score desc
        limit %s
        """,
        (pergunta, pergunta, k),
    )
    return cursor.fetchall()
