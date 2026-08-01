#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rota GET /admin/metricas: quais empresas e usuarios mais perguntam.

Sem autenticacao por enquanto (endpoint interno) - ver plano/README para a
pendencia de proteger isso antes de expor publicamente.
"""

from fastapi import APIRouter

from .banco import obter_metricas_satisfacao, obter_pool
from .datadog_cliente import consultar_serie
from .esquemas import MetricasSaida, MetricasSatisfacaoSaida

roteador = APIRouter()

NOME_CONTAINER_API = "avendre-api-1"


@roteador.get("/admin/metricas", response_model=MetricasSaida)
def metricas():
    pool = obter_pool()
    with pool.connection() as conexao:
        with conexao.cursor() as cursor:
            cursor.execute(
                """
                select e.nome, count(*) as total
                from perguntas p
                join empresas e on e.id = p.empresa_id
                group by e.nome
                order by total desc
                """
            )
            por_empresa = [
                {"empresa": nome, "total_perguntas": total} for nome, total in cursor.fetchall()
            ]

            cursor.execute(
                """
                select u.email, e.nome, count(*) as total
                from perguntas p
                join usuarios u on u.id = p.usuario_id
                join empresas e on e.id = p.empresa_id
                group by u.email, e.nome
                order by total desc
                """
            )
            por_usuario = [
                {"usuario": email, "empresa": nome, "total_perguntas": total}
                for email, nome, total in cursor.fetchall()
            ]

    return {"por_empresa": por_empresa, "por_usuario": por_usuario}


@roteador.get("/admin/metricas-satisfacao", response_model=MetricasSatisfacaoSaida)
def metricas_satisfacao():
    """Quanto a IA resolveu sozinha, feedback dos usuarios e o que ficou sem resposta boa."""
    pool = obter_pool()
    with pool.connection() as conexao:
        with conexao.cursor() as cursor:
            return obter_metricas_satisfacao(cursor)


@roteador.get("/admin/metricas-infra")
def metricas_infra(minutos: int = 15):
    """Metricas de infraestrutura do container da API, via Datadog (CPU/memoria)."""
    filtro = f"{{container_name:{NOME_CONTAINER_API}}}"
    return {
        "cpu": consultar_serie(f"avg:docker.cpu.usage{filtro}", minutos),
        "memoria_rss": consultar_serie(f"avg:docker.mem.rss{filtro}", minutos),
    }
