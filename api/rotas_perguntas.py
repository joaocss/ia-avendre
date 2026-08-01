#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rota POST /perguntar: busca (cache -> vetorial -> palavra-chave), registra metricas."""

from fastapi import APIRouter

from .banco import (
    buscar_trechos_palavra_chave,
    buscar_trechos_similares,
    gravar_cache,
    gravar_pergunta,
    ler_cache,
    obter_ou_criar_empresa,
    obter_ou_criar_usuario,
    obter_pool,
)
from .busca import chave_cache, gerar_embedding_pergunta, montar_resultados
from .esquemas import PerguntaEntrada, PerguntaSaida

roteador = APIRouter()

MODELO_EMBEDDING = "text-embedding-3-small"


@roteador.post("/perguntar", response_model=PerguntaSaida)
def perguntar(entrada: PerguntaEntrada):
    pool = obter_pool()
    chave = chave_cache(entrada.pergunta, entrada.k)

    with pool.connection() as conexao:
        with conexao.cursor() as cursor:
            empresa_id = obter_ou_criar_empresa(cursor, entrada.empresa_nome)
            usuario_id = None
            if entrada.usuario_email:
                usuario_id = obter_ou_criar_usuario(cursor, empresa_id, entrada.usuario_email)
            conexao.commit()  # garante que empresa/usuario sobrevivem a um rollback futuro

            resposta_cache = ler_cache(cursor, chave)
            if resposta_cache is not None:
                gravar_pergunta(
                    cursor, empresa_id, usuario_id, entrada.pergunta,
                    resposta_cache.get("metodo", "desconhecido"), True,
                )
                conexao.commit()
                return {**resposta_cache, "veio_do_cache": True}

            metodo = "semantica"
            try:
                from openai import OpenAI

                cliente = OpenAI()
                embedding = gerar_embedding_pergunta(cliente, entrada.pergunta, MODELO_EMBEDDING)
                linhas = buscar_trechos_similares(cursor, embedding, entrada.k * 3)
            except Exception:
                metodo = "palavra-chave"
                conexao.rollback()  # a excecao pode ter deixado a transacao abortada
                linhas = buscar_trechos_palavra_chave(cursor, entrada.pergunta, entrada.k * 3)

            saida = {
                "pergunta": entrada.pergunta,
                "metodo": metodo,
                "veio_do_cache": False,
                "resultados": montar_resultados(linhas, entrada.k),
            }

            gravar_cache(cursor, chave, saida)
            gravar_pergunta(cursor, empresa_id, usuario_id, entrada.pergunta, metodo, False)
            conexao.commit()

            return saida
