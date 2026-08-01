#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rota POST /perguntar: busca (cache -> vetorial -> palavra-chave), registra metricas."""

from fastapi import APIRouter, HTTPException

from .banco import (
    buscar_artigo_completo,
    buscar_trechos_palavra_chave,
    buscar_trechos_similares,
    gravar_cache,
    gravar_feedback,
    gravar_pergunta,
    ler_cache,
    obter_ou_criar_empresa,
    obter_ou_criar_usuario,
    obter_pool,
)
from .busca import chave_cache, gerar_embedding_pergunta, montar_resultados
from .esquemas import FeedbackEntrada, PerguntaEntrada, PerguntaSaida
from .gerar_resposta import gerar_explicacao

roteador = APIRouter()

MODELO_EMBEDDING = "text-embedding-3-small"
LIMIAR_RELEVANCIA = 0.55  # score minimo (busca semantica) para considerar a resposta satisfatoria


def calcular_sem_resposta(metodo: str, resultados: list) -> bool:
    if not resultados:
        return True
    if metodo == "semantica":
        return resultados[0]["score"] < LIMIAR_RELEVANCIA
    return False  # ts_rank (palavra-chave) nao e comparavel a esse limiar


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
                sem_resposta = calcular_sem_resposta(
                    resposta_cache.get("metodo", ""), resposta_cache.get("resultados", [])
                )
                pergunta_id = gravar_pergunta(
                    cursor, empresa_id, usuario_id, entrada.pergunta,
                    resposta_cache.get("metodo", "desconhecido"), True, sem_resposta,
                )
                conexao.commit()
                return {**resposta_cache, "id": pergunta_id, "veio_do_cache": True}

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

            resultados = montar_resultados(linhas, entrada.k)
            sem_resposta = calcular_sem_resposta(metodo, resultados)

            artigo_principal = None
            if resultados:
                artigo_principal = buscar_artigo_completo(cursor, resultados[0]["artigo_id"])

            saida = {
                "pergunta": entrada.pergunta,
                "metodo": metodo,
                "veio_do_cache": False,
                "explicacao": gerar_explicacao(entrada.pergunta, resultados),
                "artigo_principal": artigo_principal,
                "resultados": resultados,
            }

            gravar_cache(cursor, chave, saida)
            pergunta_id = gravar_pergunta(
                cursor, empresa_id, usuario_id, entrada.pergunta, metodo, False, sem_resposta
            )
            conexao.commit()

            return {**saida, "id": pergunta_id}


@roteador.post("/perguntar/{pergunta_id}/feedback")
def feedback(pergunta_id: int, entrada: FeedbackEntrada):
    pool = obter_pool()
    with pool.connection() as conexao:
        with conexao.cursor() as cursor:
            encontrado = gravar_feedback(cursor, pergunta_id, entrada.util)
            conexao.commit()
    if not encontrado:
        raise HTTPException(status_code=404, detail="pergunta nao encontrada")
    return {"status": "ok"}
