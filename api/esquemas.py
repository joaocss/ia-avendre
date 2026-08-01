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


class ArtigoCompleto(BaseModel):
    titulo: str
    categoria: str
    pasta: str
    url: str
    conteudo_markdown: str
    imagens: list = []
    videos: list = []


class PerguntaSaida(BaseModel):
    id: int
    pergunta: str
    metodo: str
    veio_do_cache: bool
    explicacao: Optional[str] = None
    artigo_principal: Optional[ArtigoCompleto] = None
    resultados: list[ResultadoArtigo]


class FeedbackEntrada(BaseModel):
    util: bool


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


class PerguntaSemResposta(BaseModel):
    pergunta: str
    empresa: Optional[str] = None
    criado_em: str


class MetricasSatisfacaoSaida(BaseModel):
    total_perguntas: int
    resolvidas_pela_ia: int
    escalonadas_para_humano: int
    sem_resposta_count: int
    feedback_positivo: int
    feedback_negativo: int
    sem_feedback: int
    perguntas_sem_resposta_recentes: list[PerguntaSemResposta]
