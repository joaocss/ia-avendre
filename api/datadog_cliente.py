#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cliente para consultar a API do Datadog (metricas de infraestrutura/APM),
para trazer isso de volta pro /admin junto com as metricas de negocio
(empresas/usuarios) que ja ficam no Supabase.

Usa DD_API_KEY + DD_APP_KEY (Application Key) do .env - nao o mesmo uso do
DD_API_KEY do Agent (que so envia dados), aqui e para LER dados de volta.
"""

import os
import time

from datadog_api_client import ApiClient, Configuration
from datadog_api_client.v1.api.metrics_api import MetricsApi


def obter_configuracao() -> Configuration:
    configuracao = Configuration()
    configuracao.api_key["apiKeyAuth"] = os.environ["DD_API_KEY"]
    configuracao.api_key["appKeyAuth"] = os.environ["DD_APP_KEY"]
    if os.environ.get("DD_SITE"):
        configuracao.server_variables["site"] = os.environ["DD_SITE"]
    return configuracao


def consultar_serie(query: str, minutos: int = 15) -> dict:
    """Consulta uma serie temporal (query no formato do Datadog, ex.: 'avg:docker.cpu.usage{...}')."""
    configuracao = obter_configuracao()
    agora = int(time.time())
    with ApiClient(configuracao) as cliente_api:
        api_metricas = MetricsApi(cliente_api)
        resposta = api_metricas.query_metrics(_from=agora - minutos * 60, to=agora, query=query)
        return resposta.to_dict()
