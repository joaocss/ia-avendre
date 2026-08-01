#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Modelos Pydantic (request/response) da API de suporte Avendre."""

from typing import Optional

from pydantic import BaseModel, Field


class PerguntaEntrada(BaseModel):
    pergunta: str
    empresa_nome: str
    usuario_email: Optional[str] = None
    k: int = Field(default=4, ge=1, le=10)


class ResultadoArtigo(BaseModel):
    titulo: str
    categoria: str
    pasta: str
    url: str
    score: float
    trecho: str
    imagens: list = []
    videos: list = []


class PerguntaSaida(BaseModel):
    pergunta: str
    metodo: str
    veio_do_cache: bool
    explicacao: Optional[str] = None
    resultados: list[ResultadoArtigo]


class MetricaEmpresa(BaseModel):
    empresa: str
    total_perguntas: int


class MetricaUsuario(BaseModel):
    usuario: str
    empresa: str
    total_perguntas: int


class MetricasSaida(BaseModel):
    por_empresa: list[MetricaEmpresa]
    por_usuario: list[MetricaUsuario]
